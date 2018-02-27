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
          puts "There is no #{name} to list"
        end
      end
    end
  end
end
