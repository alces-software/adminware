require 'adminware'

module Adminware
  module ScheduleRemove 
    class << self
      def run(host, group, name, id)
        @host = host
        @group = group
        @name = name
        @id = id
       
        if group.nil?
          get_host_schedule(@host)
          remove_from_host
        else
          remove_from_group
        end
      end
    
      def remove_job_by_name
        removed_jobs = false
        (0..(@schedule.length-1)).each do |i| 
          s = @schedule[i]
          if s[:job] == @name && s[:scheduled]
            s[:scheduled] = false
            s[:run_date] = 'Removed from schedule'
            removed_jobs = true if !removed_jobs
          end
        end
        
        #Check if any jobs have been removed
        if removed_jobs
          save_schedule
          puts "\t> Removed all instances of #{@name} from the schedule of #{@host}" 
        else
          puts "\t> There were no instances of #{@name} to remove from the schedule of #{@host}"
        end
      end

      def remove_job_by_id
        (0..(@schedule.length-1)).each do |i|
          job = @schedule[i]
          if job[:id] == @id
            if job[:scheduled]
              job[:scheduled] = false
              job[:run_date] = 'Removed from schedule'
              job[:exit] = 'Removed'
              
              save_schedule
              puts "\t> Removed job with ID ##{@id} from the schedule of #{@host}" 
            else
              puts "\t> Can't remove a job that has already run from the schedule"
            end
            break
          elsif i == @schedule.length-1
            puts "\t> There is no job with ID ##{@id} within the schedule for #{@host}" 
          end
        end
      end

      private
      
      #Loads the schedule for the given host
      def get_host_schedule(host)
        path = File.join(Adminware.root, 'var', "#{host}_schedule.yaml")
        if File.exist?(path)
          @file = Schedule.new(host, nil)
          @schedule = @file.load_array
        else
          puts "\t> There is no schedule for #{host}"
          exit 1
        end
      end
     
      def remove_from_host
        if @id.nil?
          remove_job_by_name
        else
          remove_job_by_id
        end
      end

      def remove_from_group 
        groups = YAML.load_file(File.join(Adminware.root, 'var/groups.yaml'))
        if groups[@group]
          groups[@group].each do |host|
            @host = host
            get_host_schedule(host)
            remove_from_host 
          end
        else
          puts "\t> The group '#{@group}' could not be found"
          exit 1
        end
      end
      
      def save_schedule
        @file.save!
      end
    end
  end
end
