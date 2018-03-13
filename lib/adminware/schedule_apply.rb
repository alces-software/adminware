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
            execute_job
            
            #After the job has run flag it as no longer scheduled
            @schedule[n][:scheduled] = false
            state = YAML.load_file(File.join(@config.statedir, "#{@host}_state.yaml"))
            @schedule[n][:exit] = state[@job_name][:exit] 
            @file.save!
          end
        end
      end
      
      #Creates a job instance and attempts to run the job from the schedule
      def execute_job
        job = Job.new(@job_name)
        job.state = @state
        job.command = @status
        job.host = @host
        
        job.validate!

        job.run
        @state.save!
      end
    end
  end
end
