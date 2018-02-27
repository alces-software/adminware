require 'adminware'
require 'adminware/log'
require 'adminware/config'
require 'adminware/state'
require 'open3'

module Adminware
  class Job
    attr_accessor :command
    attr_accessor :host

    def initialize(name, state)
      @path = Adminware::root 
      @config = Adminware::config
      @logger = Adminware::log
      @name = name
      @state = state
    end

    #Performs validation on entered command
    def validate!
      @file = File.join(@config.jobdir, @name, @command + '.sh')
      @job = "#{@command} script for #{@name}"

      running_locally?
      @logger.log('info', "Attempting to run #{@job}")
      
      #Check if the directory and file exist
      if dir_exist? and file_exist? then
        return true
      else
        @logger.log('error', "Failed to validate")
        exit 1
      end
    end

    #Runs the requested script for the job
    def run
      if status_matches_command? #Don't execute
      else
        execute(@script)
        set_job_values
      end
    end

    private

    #Checks to see if the directory exists for input NAME
    def dir_exist?
      jobdir = File.join(@config.jobdir, @name)
      if Dir.exist?(jobdir)
        return true
      else
        @logger.log('error', "The directory: #{jobdir} does not exist")
        return false
      end
    end

    #Checks to see if the file exists for input COMMAND:
    def file_exist?
      if File.exist?(@file)
        return true
      else
        @logger.log('error', "The #{@command} script for #{@name} does not exist")
        return false
      end
    end

    #Execute the command given and sends necessary output to the logger
    def execute(command)
      @logger.log('info', "Running #{@job}")
      stdout, stderr, status = Open3.capture3(command)
      @logger.log('debug', stderr.chomp)
      @logger.log('debug', status)
      if status.success?
        @logger.log('info', "Successfully executed #{@job}")
      else 
        @logger.log('error', "Failed to execute #{@job}")
        exit!
      end
    end

    #Checks if the job's status matches the entered command
    def status_matches_command?
      if "#{@state.status(@name)}" == @command
        @logger.log('error', "Can't execute #{@command} script for #{@name} as it is already set to true")
        @state.set_exit(@name, 1)
        @state.save!
        return true
      end
    end

    #Checks if the job needs to run locally or on another machine
    def running_locally?
      if @host == 'local'
        @script = "bash #{@file}"
      else
        @job = @job + " on #{@host}"
        @script = "ssh #{@host} bash #{@path}/../jobs/#{@name}/#{@command}.sh"
      end
    end

    #Sets the correct values for the job after successful execution
    def set_job_values
      @state.toggle(@name, @command)
      @state.set_exit(@name, 0)
    end
  end
end
