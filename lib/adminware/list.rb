require 'adminware'
require 'adminware/config'
require 'adminware/state'
require 'fileutils'
require 'terminal-table'

module Adminware
  module ListCommands
    class << self
      #Handle the input command
      def run(name, command, state)
        @name = name
        @command = command
        @state = state
        @jobdir = Adminware::config.jobdir

        case command
        when 'all'
          list_all_jobs
        when 'job'
          list_job_values
        end
      end

      #List all available jobs
      def list_all_jobs
        jobs = Dir.entries(@jobdir)

        #Create the table of jobs
        table = Terminal::Table.new :headings => ['Jobs', 'Description', 'Status', 'Exit Code'] do |rows|
          #Iterate through each job and create a row for them
          (2..(jobs.length-1)).each do |i|
            file = YAML::load_file(File.join(@jobdir, jobs[i], 'job.yaml'))
            rows << [jobs[i], file['description'], @state.print[jobs[i]][:status], @state.print[jobs[i]][:exit]]
          end
          rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts table
      end

      #Lists the values of a job within the state file
      def list_job_values
        if job_exists?
          create_table
        else exit 1 end
      end
      
      #Create the table for the given job      
      def create_table
        job = YAML::load_file(File.join(@jobdir, @name, 'job.yaml'))
        table = Terminal::Table.new :headings => ['Job', 'Description', 'Status', 'Exit Code'] do |rows|
          rows << [@name, job['description'], @state.print[@name][:status], @state.print[@name][:exit]]
          rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts table
      end 
     
      #Checks the job exists within the state file
      def job_exists?
        if @state.print.include? "#{@name}"
          return true
        else
          job_dir_exist?
        end
      end

      #Checks the job directory exists
      def job_dir_exist?
        namedir = File.join(@jobdir, @name)
        if Dir.exist?(namedir)
          puts "#{@name} needs to be run at least once before it can be listed"
        else
          puts "The directory for #{@name} does not exist and therefore can't be run or listed"
        end
      end
    end
  end
end
