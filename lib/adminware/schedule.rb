require 'adminware'
require 'adminware/job'
require 'adminware/config'
require 'yaml'
require 'fileutils'

module Adminware
  class Schedule
    attr_accessor :share_index
    def initialize(host, group)
      @host = host
      @group = group
      @config = Adminware.config

      load_index
      if @group.nil?
        @file = File.join(Adminware.root, 'var', "#{@host}_schedule.yaml")
        load_schedule
      end
    end

    #Add a job to the schedule
    def add_job(name, command)
      increment_index
      hash = {
        :id => @index[:index],
        :job => name, 
        :status => command, 
        :scheduled => true, 
        :exit => 'N/A', 
        :schedule_date => get_time,
        :run_date => 'N/A'
      }
      @schedule.push(hash)

      puts "\t> #{command} script for #{name} scheduled on #{@host}" unless @share_index
    end

    def add_to_individual_schedules(name, command)
      increment_index
      @groups[@group].each do |host|
        schedule = Schedule.new(host, nil)
        schedule.share_index = true
        schedule.add_job(name, command)
        schedule.save!
      end
      puts "\t> #{command} script for #{name} scheduled for #{@group} (#{@groups.count} nodes)"
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
      if @group.nil?
        Job.new(name, command, @host).valid?
      else
        group_path = File.join(Adminware.root, 'var/groups.yaml')
        @groups = YAML.load_file(group_path)
        @groups[@group].each do |host|
          Job.new(name, command, host).valid?
        end
      end
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

    def load_index
      @index = YAML.load_file(File.join(Adminware.root, 'var/cache.yaml')) rescue {}
    end
  
    def increment_index
      @index.empty? ? (@index[:index] = 1) : (@index[:index] = @index[:index]+1 unless @share_index)
      File.write(File.join(Adminware.root, 'var/cache.yaml'), @index.to_yaml)
    end
  end
end
