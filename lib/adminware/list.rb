require 'adminware/log'
require 'adminware/config'
require 'adminware/state'

module Adminware
  module ListCommands
    #Handle the input command
    def self.run(name, command, state)
      case command
      when 'all'
        list_all_jobs
      when 'job'
        list_job_values(name, state)
      end
    end

    #List all available jobs
    def self.list_all_jobs
      puts 'Available jobs:'
      system "ls", ConfigFile::config.jobdir
    end

    #Lists the values of a job within the state file
    def self.list_job_values(name, state)
      if job_exists?(name, state)
        status = state.print["#{name}"][:status]
        code = state.print["#{name}"][:exit]
        puts "#{name}: Status = #{status},  Last Exit Code = #{code}"
      else exit 1 end
    end
    
    #Checks the job exists within the state file
    def self.job_exists?(name, state)
      if state.print.include? "#{name}"
        return true
      else
        puts "There is no #{name} to list"
      end
    end
  end
end
