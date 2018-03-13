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
        @description = nil

        if @host == 'local' 
          list_job_values
        else
          search_remote_host
        end
      end
      
      #Lists the values of a job within the state file
      def list_job_values
        @jobs = []
        add_jobs_from(@config.central_jobdir)
        add_jobs_from(@config.local_jobdir)
        if @jobs.empty?
          puts "\t> No jobs to list"
        else
          which_output?
        end
      end
     
      def add_jobs_from(directory)
        if Dir.exist?(directory)
          Dir.foreach("#{directory}") do |item|
            next if item == '.' or item == '..'

            file = File.join(directory, item, 'job.yaml')
            if File.exist?(file)
              file = YAML.load_file(file)
              description = file['description'] 
            else 
              description = 'No description available'
            end

            hash = { :job => item, :directory => directory, :description => description }
            @jobs.push(hash)
          end
        end
      end
 
      #Figure out which output to use 
      def which_output?
        if @plain
          plain_output
        else
          create_table
        end
      end
     
      #Output in tab delimited form
      def plain_output
        puts "Host\tJob\tDescription"
        (0..(@jobs.length-1)).each do |i|
          puts "#{@host}\t#{@jobs[i][:job]}\t#{@jobs[i][:description]}"
        end
      end
     
      def create_table
        table = Terminal::Table.new do |rows|
          rows.headings = ['Host', 'Job', 'Description']
          (0..(@jobs.length-1)).each do |i|
            rows << [@host, @jobs[i][:job], @jobs[i][:description]]
          end
        rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts "\n#{table}"
      end 

      def search_remote_host
        @jobs = []
        add_jobs_from(@config.central_jobdir)

        job_names = []
        stdout, stderr, status = Open3.capture3("ssh #{@host} ls #{@config.local_jobdir}")
        if status.success?
          #Grab the local job names from @host
          start = 0
          (0..(stdout.length-1)).each do |i|
            if stdout[i+1] == "\n"
              job_names << stdout[start..i]
              start = i + 2
            end
          end
          
          #Where possible get the descriptions for the jobs
          job_names.each do |job|
            stdout, stderr, status = Open3.capture3("ssh #{@host} cat #{@config.local_jobdir}/#{job}/job.yaml")
            if status.success?
              description = stdout[18..-3] 
            else
              description = 'No description available'
            end
            hash = { :job => job, :description => description }
            @jobs.push(hash)
          end

          which_output?
        else
          puts "\t> #{@host} is not a valid host name"
          exit 1
        end
      end 
    end
  end
end
