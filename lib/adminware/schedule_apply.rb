require 'adminware/config'
require 'adminware/schedule'
require 'adminware/state'
require 'adminware/job'

module Adminware
  module ScheduleApply
    class << self
      def run(host)
        @file = Schedule.new(host)
        @state = State.new(host)
        @schedule = @file.load_array
        @host = host
        @config = Adminware.config

        find_next_job
        run_schedule        
      end

      #Finds the next job to run in the schedule
      def find_next_job
        (0..(@schedule.length-1)).each do |n|
          if @schedule[n][:scheduled]
            @job_number = n
            break
          end 
        end
      end

      #Iterates through the schedule and runs queued jobs in order
      def run_schedule
        if @job_number.nil?
          puts "\t> No jobs currently scheduled for #{@host}"
        else
          (@job_number..(@schedule.length-1)).each do |n|
            @job_name = @schedule[n][:job]
            @status = @schedule[n][:status]
            
            #Stop further jobs in schedule if current fails
            unless execute_job
              save_schedule_values(n, false) 
              break
            else
              save_schedule_values(n, true)
            end
          end
        end
      end
      
      def save_schedule_values(n, success)
        if success
          #If ran successfully flag as no longer scheduled
          @schedule[n][:scheduled] = false
        end
        
        state = YAML.load_file(File.join(@config.statedir, "#{@host}_state.yaml"))
        @schedule[n][:run_date] = get_time
        @schedule[n][:exit] = state[@job_name][:exit]
        @file.save!
      end
    
      def get_time
        time = Time.new
        time.strftime("%d-%m-%Y %H:%M:%S")
      end

      #Creates a job instance and attempts to run the job from the schedule
      def execute_job
        job = Job.new(@job_name, @status, @host)
        job.state = @state
        
        job.valid? 
          job.run ? true : false
      end
    end
  end
end
