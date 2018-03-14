require 'adminware'
require 'adminware/log'
require 'adminware/config'
require 'adminware/state'
require 'open3'

module Adminware
  class Job
    attr_accessor :state

    def initialize(name, command, host)
      @path = Adminware.root 
      @config = Adminware.config
      @logger = Adminware.log
      @name = name
      @command = command
      @host = host
    end

    def valid?
      #Check if the directory and file exist
      if dir_exist? && file_exist? 
        true
      else
        @logger.log('error', "Failed to validate")
      end
    end

    def run
      @job = "#{@command} script for #{@name} on #{@host}"

      #Checks if the job needs to run on another host
      if running_locally?
        set_script("bash #{@file}")
      elsif @remote_dir == 'local'
        set_script("ssh #{@host} bash #{@file}")
      else
        set_script("ssh #{@host} bash #{File.expand_path(@config.central_jobdir)}/#{@name}/#{@command}.sh")
      end

      #Prevents the running of commands that match the requested job's status
      if status_matches_command?
        @logger.log('error', "Can't execute #{@command} script for #{@name} as it is already set to true")
        @state.set_exit(@name, 1)
        @state.save!
      else
        @logger.log('info', "Attempting to execute #{@job}")
        stdout, stderr, status = Open3.capture3(@script)
        @logger.log('debug', stderr.chomp) if !stderr.empty? 
        @logger.log('debug', status)
        if status.success?
          @logger.log('info', "Successfully executed #{@job}")
          set_job_values
        else
          @logger.log('error', "Failed to execute #{@job}")
        end
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
      elsif exist_remotely?(local)
        @file = File.join(local, @command + '.sh')
      else  
        @logger.log('error', "The job directory for #{@name} on #{@host} does not exist")
        false
      end
    end

    #Checks to see if the file exists for input COMMAND
    def file_exist?
      if File.exist?(@file)
        true
      elsif exist_remotely?(@file)
        @remote_dir = 'local'
      else
        @logger.log('error', "The #{@command} script for #{@name} on #{@host} does not exist")
        false
      end
    end
    
    #Checks if the job's status matches the entered command
    def status_matches_command?
      if @state.status(@name) == @command then true end
    end

    #Checks if the job needs to run locally or on another host
    def running_locally?
      @host == 'local' ? true : false
    end
   
    #Checks the remote host for a given path 
    def exist_remotely?(path)
      stdout, stderr, status = Open3.capture3("ssh #{@host} find #{path}")
      status.success?
    end

    def set_script(command)
      @script = command
    end

    #Sets the correct values for the job after successful execution
    def set_job_values
      @state.toggle(@name, @command)
      @state.set_exit(@name, 0)
    end
  end
end
