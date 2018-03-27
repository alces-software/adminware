require 'adminware'
require 'adminware/schedule'
require 'fileutils'
require 'terminal-table'

module Adminware
  module ScheduleList
    class << self
      def run(host, show_all, plain)
        @host = host
        @show_all = show_all
        @plain = plain
     
        list_schedule
      end

      def list_schedule
        if schedule_exists?
          @file = Schedule.new(@host, nil)          
          @schedule = @file.load_array
        end
        output
      end
 
      #Check if a schedule exists for the host
      def schedule_exists?
        @schedule = File.join(Adminware.root, 'var', "#{@host}_schedule.yaml")
        if File.exist?(@schedule)
          true
        else
          puts "\t> There is no schedule for #{@host}"
          exit 1
        end
      end
     
      #Figure out which output to use 
      def output
        @plain ? plain_output : table_output 
      end
     
      #Output schedule data in a tab delimited format 
      def plain_output
        no_queued_jobs = true
        puts "Host\tID\tJob\tStatus\tExit Code\tQueued\tSchedule Date\tRun Date"
        (0..(@schedule.length-1)).each do |i|
          s = @schedule[i]
          if s[:scheduled] or @show_all
            print @host
            print "\t#{s[:id]}"
            print "\t#{s[:job]}"
            print "\t#{s[:status]}"
            print "\t#{s[:exit]}"
            print "\t#{s[:scheduled]}"
            print "\t#{s[:schedule_date]}"
            print "\t#{s[:run_date]}\n"
            no_queued_jobs = false if no_queued_jobs
          elsif i == (@schedule.length-1) && no_queued_jobs
            puts "\t> There are no scheduled jobs to list. Use the 'all' option to see history"
            exit 1
          end
        end 
      end

      #Output the schedule in a table for the given host
      def table_output
        no_queued_jobs = true
        table = Terminal::Table.new :title => 'Schedule' do |rows|
          rows.headings = ['Host', 'ID', 'Job', 'Status', 'Exit Code', 'Queued', 'Schedule Date', 'Run Date']
          (0..(@schedule.length-1)).each do |i|
            s = @schedule[i]

            if s[:scheduled] or @show_all
              rows << [@host, s[:id], s[:job], s[:status], 
                s[:exit], s[:scheduled], s[:schedule_date], s[:run_date]]
              no_queued_jobs = false if no_queued_jobs
            elsif i == (@schedule.length-1) && no_queued_jobs
              puts "\t> There are no scheduled jobs to list. Use the 'all' option to see history"
              exit 1
            end
          end
          rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts "\n#{table}"
      end
    end
  end
end
