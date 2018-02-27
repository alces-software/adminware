require 'adminware'
require 'adminware/config'
require 'adminware/state'
require 'fileutils'

module Adminware
  module ListCommands
    class << self
      #Handle the input command
      def run(name, command, state)
        case command
        when 'all'
          list_all_jobs
        when 'job'
          list_job_values(name, state)
        end
      end

      #List all available jobs
      def list_all_jobs
        config = Adminware::config
        puts 'Available jobs:'
        puts Dir.entries(config.jobdir)[2..-1]
      end

      #Lists the values of a job within the state file
      def list_job_values(name, state)
        if job_exists?(name, state)
          status = state.print["#{name}"][:status]
          code = state.print["#{name}"][:exit]
          puts "#{name}: Status = #{status},  Last Exit Code = #{code}"
        else exit 1 end
      end
      
      #Checks the job exists within the state file
      def job_exists?(name, state)
        if state.print.include? "#{name}"
          return true
        else
          job_dir_exist?(name)
        end
      end

      def job_dir_exist?(name)
        jobdir = File.join(Adminware::config.jobdir, name)
        if Dir.exist?(jobdir)
          puts "#{name} needs to be run at least once before it can be listed"
        else
          puts "The directory for #{name} does not exist and therefore can't be run or listed"
        end
      end
    end
  end
end
