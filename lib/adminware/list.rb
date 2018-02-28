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
          list_all_jobs
        when 'job'
          list_job_values(name, state)
        end
      end

      #List all available jobs
      def list_all_jobs
        config = Adminware::config
        jobs = Dir.entries(config.jobdir)

        #Create the table of jobs
        table = Terminal::Table.new do |rows|
          rows << ['Available jobs']
          rows.add_separator
          (2..(jobs.length-1)).each do |i|
            rows << [{:value => jobs[i], :alignment => :center}]
          end
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
        table = Terminal::Table.new :headings => ['Job', 'Variable', 'Value'] do |rows|
          rows << [name, 'Status', state.print[name][:status]]
          rows << ['','Exit Code', state.print[name][:exit]]
          rows.style = {:alignment => :right}
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
