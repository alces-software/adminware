module Adminware
 module ScheduleRemove 
  class << self
    def run(name, host, id)
     @name = name
     @host = host
     @id = id
     
     get_schedule

     if id.nil?
      remove_job_by_name
     else
      remove_job_by_id
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
      job = @schedule[@id-1]
      #Ensure the job exists before attempting to remove
      if job_exists?(job)
        if job[:scheduled]
          job[:scheduled] = false
          job[:run_date] = 'Removed from schedule'
          
          save_schedule
          puts "\t> Removed job with ID ##{@id} from the schedule of #{@host}"
        else 
          puts "\t> Can't remove a job that has already run from the schedule"
        end
      end
    end

    private
    
    #Loads the schedule for the given host
    def get_schedule
      path = File.join(Adminware.root, 'var', "#{@host}_schedule.yaml")
      if File.exist?(path)
        @file = Schedule.new(@host)
        @schedule = @file.load_array
      else
        puts "\t> There is no schedule for #{@host}"
        exit 1
      end
    end
   
    #Check the job exists within the schedule
    def job_exists?(job)
      if job
        true
      else
        puts "\t> There is no job with ID ##{@id} within the schedule for #{@host}"
        false
      end
    end

    def save_schedule
      @file.save!
    end
  end
 end
end
