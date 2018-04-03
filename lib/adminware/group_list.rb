require 'adminware'
require 'adminware/schedule'
require 'fileutils'
require 'terminal-table'
require 'yaml'

module Adminware
  module GroupList
    class << self
      def run(group, exit_code, show_all, plain)
        @group = group
        @show_all = show_all
        @plain = plain  
        @exit_code = exit_code 
        @groups = YAML.load_file(File.join(Adminware.root, 'var/groups.yaml'))
        
        get_hosts
        get_schedules
        list_schedule
      end 
        
      def get_hosts
        @hosts = []
        if @groups[@group]
          @groups[@group].each do |host|
            @hosts << host
          end
        else
          puts "\t> The group '#{@group}' could not be found"
          exit 1
        end
      end
      
      def get_schedules
        schedules = []
        @hosts.each do |host|
          if schedule_exists?(host)
            schedule = Schedule.new(host, nil).load_array
            schedules << schedule
          else
            @hosts.delete(host)
          end
        end

        if schedules.empty?
          puts "\t> No schedules found for group '#{@group}'"
          exit 1
        else
          @jobs = []
          (0..(@hosts.length-1)).each do |host|
            (0..(schedules[host].length-1)).each do |job|
               schedules[host][job][:host] = @hosts[host]
               job = schedules[host][job]
               @jobs << job
            end
          end
          @jobs.sort_by! { |job| [job[:scheduled] ? 1 : 0, job[:id]] }
        end
      end

      def list_schedule
        filter_by_exit_code if @exit_code 
        output
      end

      def schedule_exists?(host)
        schedule = File.join(Adminware.root, 'var', "#{host}_schedule.yaml")
        File.exist?(schedule) ? true : false
      end

      def filter_by_exit_code
        (0..(@jobs.length-1)).each do |i|
          if @jobs[i][:exit].to_s.downcase == @exit_code.downcase 
            next 
          else
            @jobs.delete_at(i) 
            filter_by_exit_code 
            break
          end
        end
      end

      def output
        @plain ? plain_output : table_output
      end

      def plain_output
        no_queued_jobs = true
        puts "Host\tID\tJob\tStatus\tExit Code\tQueued\tSchedule Date\tRun Date"
        @jobs.each do |job|
          if job[:scheduled] or @show_all
            print job[:host]
            print "\t#{job[:id]}"
            print "\t#{job[:job]}"
            print "\t#{job[:status]}"
            print "\t#{job[:exit]}"
            print "\t#{job[:scheduled]}"
            print "\t#{job[:schedule_date]}"
            print "\t#{job[:run_date]}\n"
            no_queued_jobs = false if no_queued_jobs
          elsif no_queued_jobs
            puts "\t> There are no scheduled jobs to list for the group. Use the 'all' option to see history"
            exit 1
          end
        end
      end

      def table_output
        no_queued_jobs = true
        table = Terminal::Table.new :title => "Schedule\nGroup: #{@group}" do |rows|
          rows.headings = ['Host', 'ID', 'Job', 'Status', 'Exit Code', 'Queued', 'Schedule Date', 'Run Date']
          @jobs.each do |job|
            if job[:scheduled] or @show_all
              rows << [job[:host], job[:id], job[:job], job[:status], job[:exit],
                job[:scheduled], job[:schedule_date], job[:run_date]]
              no_queued_jobs = false if no_queued_jobs
            end
          end

          if no_queued_jobs
            puts "\t> There are no scheduled jobs to list for the group. Use the 'all' option to see history"
            exit 1
          end

          rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts "\n#{table}"
      end
    end
  end
end
