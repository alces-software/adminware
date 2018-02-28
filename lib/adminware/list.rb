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
        case command
        when 'all'
          list_all_jobs(values = false, state)
        when 'job'
          if name == 'all'
            list_all_jobs(values = true, state)
          else
            list_job_values(name, state)
          end
        end
      end

      #List all available jobs
      def list_all_jobs(values, state)
        config = Adminware::config
        jobs = Dir.entries(config.jobdir)

        #Create the table of jobs
        table = Terminal::Table.new do |rows|
          (2..(jobs.length-1)).each do |i|
            file = YAML::load_file(File.join(config.jobdir, jobs[i], 'job.yaml'))
            if values
              rows.headings = ['Job', 'Description', 'Status', 'Exit Code']
              rows << [jobs[i], file['description'], state.print[jobs[i]][:status], state.print[jobs[i]][:exit]]
            else
              rows.headings = ['Job', 'Description']
              rows << [jobs[i], file['description']]
            end
          end
          rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts table
      end

      #Lists the values of a job within the state file
      def list_job_values(name, state)
        if job_exists?(name, state)
          create_table(name, state)
        else exit 1 end
      end
      
      #Create the table for the given job      
      def create_table(name, state)
        job = YAML::load_file(File.join(Adminware::config.jobdir, name, 'job.yaml'))
        table = Terminal::Table.new :headings => ['Job', 'Description', 'Status', 'Exit Code'] do |rows|
          rows << [name, job['description'], state.print[name][:status], state.print[name][:exit]]
          rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts table
      end 
     
      #Checks the job exists within the state file
      def job_exists?(name, state)
        if state.print.include? "#{name}"
          return true
        else
          job_dir_exist?(name)
        end
      end

      #Checks the job directory exists
      def job_dir_exist?(name)
        jobdir = File.join(Adminware::config.jobdir, name)
        if Dir.exist?(jobdir)
          puts "#{name} needs to be run at least once before it can be listed"
        else
          puts "The directory for #{name} does not exist and therefore can't be run or listed"
        end
      end
    end
  end
end
