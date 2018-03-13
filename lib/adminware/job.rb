require 'adminware'
require 'adminware/log'
require 'adminware/config'
require 'adminware/state'
require 'open3'

module Adminware
  class Job
    attr_accessor :command
    attr_accessor :host
    attr_accessor :state

    def initialize(name)
      @path = Adminware.root 
      @config = Adminware.config
      @logger = Adminware.log
      @name = name
    end

    #Performs validation on entered command
    def validate!
      @job = "#{@command} script for #{@name}"

      running_locally?
      
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
      central = File.join(@config.central_jobdir, @name)
      local = File.join(@config.local_jobdir, @name)

      if Dir.exist?(central)
        @file = File.join(central, @command + '.sh')
      elsif Dir.exist?(local)
        @file = File.join(local, @command + '.sh')
      elsif check_remotely("ssh #{@host} find #{local}")
        @file = File.join(local, @command + '.sh')
      else  
        @logger.log('error', "The job directory for #{@name} on #{@host} does not exist")
        return false
      end
    end

    #Checks to see if the file exists for input COMMAND:
    def file_exist?
      if File.exist?(@file)
        return true
      elsif check_remotely("ssh #{@host} find #{@file}")
        @script = "ssh #{@host} bash #{@file}"
      else
        @logger.log('error', "The #{@command} script for #{@name} on #{@host} does not exist")
        return false
      end
    end

    #Execute the command given and sends necessary output to the logger
    def execute(command)
      @logger.log('info', "Attempting to execute #{@job}")
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
        @running_remotely = false
      else
        @job = @job + " on #{@host}"
        @script = "ssh #{@host} bash #{File.expand_path(@config.central_jobdir)}/#{@name}/#{@command}.sh"
        @running_remotely = true
      end
    end
   
    #Checks the remote host for a given directory/file 
    def check_remotely(command)
      stdout, stderr, status = Open3.capture3(command)
      if status.success?
        return true
      else
        return false
      end
    end

    #Sets the correct values for the job after successful execution
    def set_job_values
      @state.toggle(@name, @command)
      @state.set_exit(@name, 0)
    end
  end
end
