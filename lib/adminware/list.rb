require 'adminware'
require 'adminware/config'
require 'adminware/state'
require 'adminware/schedule'
require 'fileutils'
require 'terminal-table'

module Adminware
  module List
    class << self
      #Handle the input command
      def run(name, command, host, boolean)
        @name = name
        @command = command
        @host = host
        @state = State.new(host)
        @jobdir = Adminware::config.jobdir
        @plain = boolean

        case command
        when 'all'
          list_all_jobs
        when 'job'
          list_job_values
        when 'schedule'
          list_schedule
        end
      end

      #List all available jobs
      def list_all_jobs
        jobs = []
        @state.file.each do |key, value|
           jobs << key
        end

        if jobs.empty?
          puts "\t> Nothing in the #{@host} state file to list, run a job for it first"
        else
          which_output?(jobs)
        end
      end
      
      #Lists the values of a job within the state file
      def list_job_values
        job_exists?
        job = [@name]
        which_output?(job)
      end
      
      #List the schedule for the given host
      def list_schedule
        schedule_exists?
        print_schedule
      end

      #Figure out which output to use 
      def which_output?(job)
        if @plain
          plain_output(job)
        else
          create_table(job)
        end
      end
      
      def print_schedule
        @file = Schedule.new(@host)
        @schedule = @file.load_array
        table = Terminal::Table.new :title => 'Scheduled Jobs', :headings => ['Host', 'Job(s)', 'Status'] do |rows|
          (0..(@schedule.length-1)).each do |i|
            if @schedule[i][:scheduled]
              rows << [@host, @schedule[i][:job], @schedule[i][:status]]
            end
          end
          rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts table
      end

      #Output in tab delimited form
      def plain_output(jobs)
        puts "Host\tJobs\tDescription\tStatus\tExit Code"
        (0..(jobs.length-1)).each do |i|
          file = YAML::load_file(File.join(@jobdir, jobs[i], 'job.yaml'))
          puts "#{@host}\t#{jobs[i]}\t#{file['description']}\t#{@state.file[jobs[i]][:status]}\t#{@state.file[jobs[i]][:exit]}"        end
      end
      
      #Create the table for the given job(s)      
      def create_table(jobs)
        table = Terminal::Table.new :headings => ['Host', 'Job(s)', 'Description', 'Status', 'Exit Code'] do |rows|
          (0..(jobs.length-1)).each do |i|
            file = YAML::load_file(File.join(@jobdir, jobs[i], 'job.yaml'))
            rows << [@host, jobs[i], file['description'], @state.file[jobs[i]][:status], @state.file[jobs[i]][:exit]]
            rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
          end
        end
        puts table
      end 
     
      #Checks the job exists within the state file
      def job_exists?
        if @state.file.include? "#{@name}"
          return true
        else
          job_dir_exist?
        end
      end

      #Checks the job directory exists
      def job_dir_exist?
        namedir = File.join(@jobdir, @name)
        if Dir.exist?(namedir)
          puts "\t> #{@name} needs to be run at least once before it can be listed"
        else
          puts "\t> The directory for #{@name} does not exist and therefore can't be run or listed"
        end
        exit 1
      end
      
      def schedule_exists?
        @schedule = File.join(Adminware::root, 'var', "#{@host}_schedule.yaml")
        if File.exist?(@schedule)
          return true
        else
          puts "\t> There is no schedule for #{@host}"
          exit 1
        end
      end
    end
  end
end
