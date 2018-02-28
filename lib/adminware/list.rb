require 'adminware'
require 'adminware/config'
require 'adminware/state'
require 'fileutils'
require 'terminal-table'

module Adminware
  module ListCommands
    class << self
      #Handle the input command
      def run(name, command, state, output)
        @name = name
        @command = command
        @state = state
        @jobdir = Adminware::config.jobdir
        @output = output

        case command
        when 'all'
          list_all_jobs
        when 'job'
          list_job_values
        end
      end

      #List all available jobs
      def list_all_jobs
        jobs = []
        Dir.entries(@jobdir).each do |dir|
          jobs << dir unless dir =~ /^\.\.?$/
        end
        which_output?(jobs)
      end
      
      #Lists the values of a job within the state file
      def list_job_values
        job_exists?
        job = [@name]
        which_output?(job)
      end
     
      #Figure out which output to use 
      def which_output?(job)
        if @output
          plain_output(job)
        else
          create_table(job)
        end
      end

      #Output in tab delimited form
      def plain_output(jobs)
        puts "Jobs\tDescription\tStatus\tExit Code"
        (0..(jobs.length-1)).each do |i|
          file = YAML::load_file(File.join(@jobdir, jobs[i], 'job.yaml'))
          puts "#{jobs[i]}\t#{file['description']}\t#{@state.print[jobs[i]][:status]}\t#{@state.print[jobs[i]][:exit]}"        end
      end
      
      #Create the table for the given job(s)      
      def create_table(jobs)
        table = Terminal::Table.new :headings => ['Job(s)', 'Description', 'Status', 'Exit Code'] do |rows|
          (0..(jobs.length-1)).each do |i|
            file = YAML::load_file(File.join(@jobdir, jobs[i], 'job.yaml'))
            rows << [jobs[i], file['description'], @state.print[jobs[i]][:status], @state.print[jobs[i]][:exit]]
            rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
          end
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
          exit 1
        end
      end
    end
  end
end
