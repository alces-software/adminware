require 'adminware/config'
require 'adminware/schedule'
require 'adminware/state'
require 'adminware/job'
require 'adminware'

module Adminware
  module ScheduleApply
    class << self
      def run(host, group)
        @host = host
        @group = group
        @file = Schedule.new(host, group)
        @schedule = @file.load_array
        @state = State.new(host) unless host.nil?
        @config = Adminware.config

        if group.nil?
          find_next_job
          run_schedule        
        else
          get_hosts
          run_each_schedule
        end
      end

      def get_hosts
        @hosts = []
        group_file = YAML.load_file(File.join(Adminware.root, 'var/groups.yaml'))
        if group_file[@group]
          group_file[@group].each do |host|
            @hosts << host
          end
        else
          puts "\t> The group '#{@group}' could not be found"
          exit 1
        end
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
 
            if @schedule[n][:scheduled] 
              #Stop further jobs in schedule if current fails
              unless execute_job(@schedule[n][:id])
                save_schedule_values(n, false) 
                break
              else
                save_schedule_values(n, true)
              end
            end
          end
        end
      end

      def run_each_schedule
        @hosts.each do |host|
          ScheduleApply.run(host, nil)
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
      
      def find_job_in_schedule(schedule)
        (0..(schedule.length-1)).each do |n|
          if schedule[n][:id] == @id
            @n = n
          end
        end
      end

      def get_time
        time = Time.new
        time.strftime("%Y-%m-%d %H:%M:%S")
      end

      #Creates a job instance and attempts to run the job from the schedule
      def execute_job(id)
        job = Job.new(@job_name, @status, @host)
        job.state = @state
        job.id = id
 
        job.valid? 
          job.run ? true : false
      end
    end
  end
end
