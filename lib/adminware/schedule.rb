require 'adminware'
require 'adminware/job'
require 'adminware/config'
require 'yaml'
require 'fileutils'

module Adminware
  class Schedule
    def initialize(host)
      @host = host
      @config = Adminware.config
      @file = File.join(Adminware.root, 'var', "#{@host}_schedule.yaml")

      load_schedule
    end

    #Add a job to the schedule
    def add_job(name, command)
      hash = {
        :job => name, 
        :status => command, 
        :scheduled => true, 
        :exit => 'N/A', 
        :schedule_date => get_time,
        :run_date => 'N/A'
      }
      @schedule.push(hash)
      puts "\t> #{command} script for #{name} scheduled on #{@host}"
    end
    
    def get_time
      time = Time.new
      time.strftime("%Y-%m-%d %H:%M:%S")
    end

    def save!
      File.write(@file, @schedule.to_yaml)
    end
    
    #This ensures you can't schedule invalid jobs
    def valid?(name, command)
      Job.new(name, command, @host).valid?
    end
    
    def load_array
      @schedule
    end
   
    #Deletes the schedule file 
    def clear_schedule
      if File.exist?(@file) 
        FileUtils.rm(@file) 
        puts "\t> Successfully cleared schedule for #{@host}"
      else
        puts "\t> No schedule to clear for #{@host}"
      end
    end

    private
    
    #Load the schedule file for the given host
    def load_schedule
      @schedule = YAML.load_file(@file) rescue [] 
    end
  end
end
