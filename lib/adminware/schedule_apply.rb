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
        @config = Adminware.config

        get_hosts
        find_next_job
        run_schedule        
      end
      
      def get_hosts
        @hosts = []
        if @group.nil?
          @hosts << @host
          @name = @host
        else
          group_file = YAML.load_file(File.join(Adminware.root, 'var/groups.yaml'))
          if group_file[@group]
            group_file[@group].each do |host|
              @hosts << host
            end
          else
            puts "\t> The group '#{@group}' could not be found"
            exit 1
          end
          @name = @group
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
          puts "\t> No jobs currently scheduled for #{@name}"
        else
          (@job_number..(@schedule.length-1)).each do |n|
            @job_name = @schedule[n][:job]
            @status = @schedule[n][:status]
            @id = @schedule[n][:id]
 
            if @schedule[n][:scheduled] 
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
      end
      
      def save_schedule_values(n, success)
        if success
          #If ran successfully flag as no longer scheduled
          @schedule[n][:scheduled] = false
        end
       
        @schedule[n][:run_date] = get_time
        @hosts.each do |host| 
          state = YAML.load_file(File.join(@config.statedir, "#{host}_state.yaml"))
          @schedule[n][:exit] = state[@job_name][:exit]
          if !@group.nil?
            file = Schedule.new(host, nil)
            schedule = file.load_array
            find_job_in_schedule(schedule)
            if schedule[@n][:scheduled]
              schedule[@n][:scheduled] = false
              schedule[@n][:run_date] = @schedule[n][:run_date]
              schedule[@n][:exit] = @schedule[n][:exit]
              file.save!
            end
          end
        end
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
      def execute_job
        @hosts.each do |host|
          state = State.new(host)
          job = Job.new(@job_name, @status, host)
          job.state = state
          
          job.valid? 
            job.run ? true : false
        end
      end
    end
  end
end
