require 'adminware'
require 'adminware/job'
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
      job = Job.new(@name)
      job.command = @command
      job.host = @host

      if job.validate!
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
  end
end
