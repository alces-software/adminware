require 'adminware/log'
require 'adminware/config'
require 'adminware/state'
require 'open3'

module Adminware
  class Job
    attr_accessor :command
    attr_accessor :host

    def initialize(name, state)
      @path = File.expand_path(File.dirname(__FILE__))
      @config = ConfigFile::config.jobdir
      @name = name
      @state = state
    end

    #Performs validation on entered command
    def validate!
      @file = File.join(@config, @name, @command + '.sh')
      @job = "#{@command} script for #{@name}"

      running_locally?
      EventLogger.log('info', "Attempting to run #{@job}")

      #Check if the directory and file exist
      if dir_exist? and file_exist? then
        return true
      else
        EventLogger.log('error', "Failed to validate")
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
      if Dir.exist?(@config)
        return true
      else
        EventLogger.log('error', "#{@config} does not exist")
        return false
      end
    end

    #Checks to see if the file exists for input COMMAND:
    def file_exist?
      if File.exist?(@file)
        return true
      else
        EventLogger.log('error', "The #{@command} script for #{@name} does not exist")
        return false
      end
    end

    #Execute the command given and sends necessary output to the logger
    def execute(command)
      EventLogger.log('info', "Running #{@job}")
      stdout, stderr, status = Open3.capture3(command)
      EventLogger.log('debug', stderr.chomp)
      EventLogger.log('debug', status)
      if (status.to_s).include? "exit 127" or (status.to_s).include? "exit 255"
        EventLogger.log('error', "Failed to execute #{@job}")
        exit!
      end
    end

    #Checks if the job's status matches the entered command
    def status_matches_command?
      if "#{@state.status(@name)}" == @command
        EventLogger.log('error', "Can't execute #{@command} script for #{@name} as it is already set to true")
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
        @script = "ssh #{@host} bash #{@path}/../../jobs/#{@name}/#{@command}.sh"
      end
    end

    #Sets the correct values for the job after successful execution
    def set_job_values
      @state.toggle(@name, @command)
      @state.set_exit(@name, 0)
      EventLogger.log('info', "Successfully executed #{@job}")
    end
  end
end
