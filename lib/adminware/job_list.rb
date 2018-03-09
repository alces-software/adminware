require 'adminware'
require 'adminware/config'
require 'adminware/schedule'
require 'fileutils'
require 'terminal-table'

module Adminware
  module JobList
    class << self
      #Handle the input command
      def run(name, host, boolean)
        @name = name
        @host = host
        @config = Adminware.config
        @plain = boolean
      
        list_job_values
      end
      
      #Lists the values of a job within the state file
      def list_job_values
        jobs = []
        Dir.foreach("#{@config.jobdir}") do |item|
          next if item == '.' or item == '..'
          jobs << item 
        end 

        if jobs.empty?
          puts "\t> No jobs to list"
        else
          which_output?(jobs)
        end
      end
      
      #Figure out which output to use 
      def which_output?(jobs)
        if @plain
          plain_output(jobs)
        else
          create_table(jobs)
        end
      end
     
      #Output in tab delimited form
      def plain_output(jobs)
        puts "Host\tJob\tDescription"
        (0..(jobs.length-1)).each do |i|
          file = YAML.load_file(File.join(@config.jobdir, jobs[i], 'job.yaml'))
          puts "#{@host}\t#{jobs[i]}\t#{file['description']}"
        end
      end
      
      def create_table(jobs)
        table = Terminal::Table.new do |rows|
          rows.headings = ['Host', 'Job', 'Description']
          (0..(jobs.length-1)).each do |i|
            file = YAML.load_file(File.join(@config.jobdir, jobs[i], 'job.yaml'))
            rows << [@host, jobs[i], file['description']]
          end
        rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts table
      end  
    end
  end
end
