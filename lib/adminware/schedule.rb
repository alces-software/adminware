require 'adminware'
require 'adminware/config'
require 'yaml'
require 'fileutils'

module Adminware
  class Schedule
    attr_accessor :name
    attr_accessor :command

    def initialize(host)
      @host = host
      @config = Adminware.config
      @file = File.join(Adminware.root, 'var', "#{@host}_schedule.yaml")
      @array = []

      load_schedule
    end

    #Add a job to the schedule
    def add_job
      hash = { :job => @name, :status => @command, :scheduled => true, :exit => 'N/A' }
      @array.push(hash)
      puts "\t> #{@command} script for #{@name} scheduled on #{@host}"
    end
 
    def save!
      File::write(@file, @array.to_yaml)
    end

    def validate!
      if dir_exist? and script_exist?
        return true
      else
        return false
      end
    end
    
    def load_array
      @array
    end
   
    #Deletes the schedule file 
    def clear_schedule
      FileUtils.rm(@file)
      puts "\t> Successfully cleared schedule for #{@host}"
    end

    private
    
    #Load the schedule file for the given host
    def load_schedule
      @schedule = YAML.load_file(@file) rescue {}
      load_into_array
    end

    #Load scheduled jobs from file into an array
    def load_into_array
      @schedule.each do |s|
        @array.push(s)
      end 
    end

    def dir_exist?
      if Dir.exist?(File.join(@config.jobdir, @name))
        return true
      else
        puts "\t> The directory for #{@name} does not exist"
        return false
      end
    end

    def script_exist?
      if File.exist?(File.join(@config.jobdir, @name, "#{@command}.sh"))
        return true
      else
        puts "\t> The #{@command} script does not exist for #{@name}"
        return false
      end
    end
  end
end
