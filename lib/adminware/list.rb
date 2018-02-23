require 'log'
require 'config'
require 'state'

module Adminware
  class ListCommands
    include ConfigFile
    include EventLogger

    def initialize(name, command, state)
      @name = name
      @command = command
      @state = state
    end

    def run
      case @command
      when 'all'
        list_all_jobs
      when 'job'
        list_job_values
      end
    end

    private

    #List all available jobs
    def list_all_jobs
      puts 'Available jobs:'
      system "ls", config.jobdir
    end

    #Lists the values of a job within the state file
    def list_job_values
      if job_exists?
        status = @state.print["#{@name}"][:status]
        code = @state.print["#{@name}"][:exit]
        puts "#{@name}: Status = #{status},  Last Exit Code = #{code}"
      else exit 1 end
   end

   #Checks the job exists within the state file
    def job_exists?
      if @state.print.include? "#{@name}"
        return true
      else
        puts "There is no #{@name} to list"
      end
    end
  end
end
