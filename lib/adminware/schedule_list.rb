require 'adminware'
require 'adminware/schedule'
require 'fileutils'
require 'terminal-table'

module Adminware
  module ScheduleList
    class << self
      def run(host, boolean, plain)
        @host = host
        @show_all = boolean
        @plain = plain

        list_schedule
      end

      def list_schedule
        schedule_exists?
        output
      end
  
      #Check if a schedule exists for the host
      def schedule_exists?
        @schedule = File.join(Adminware.root, 'var', "#{@host}_schedule.yaml")
        if File.exist?(@schedule)
          return true
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
        @file = Schedule.new(@host)
        @schedule = @file.load_array
        puts "Host\tJob\tStatus\tExit Code\tQueued\tSchedule Date\tRun Date"
        (0..(@schedule.length-1)).each do |i|
          s = @schedule[i]
          if s[:scheduled] or @show_all
            print "#{@host}"
            print "\t#{s[:job]}"
            print "\t#{s[:status]}"
            print "\t#{s[:exit]}"
            print "\t#{s[:scheduled]}"
            print "\t#{s[:schedule_date]}"
            print "\t#{s[:run_date]}"
          elsif i == (@schedule.length-1)
            puts "\t> There are no scheduled jobs to list. Use adminware schedule-list --all to see history"
            exit 1
          end
        end 
      end

      #Output the schedule in a table for the given host
      def table_output
        @file = Schedule.new(@host)
        @schedule = @file.load_array
        table = Terminal::Table.new :title => 'Scheduled Jobs' do |rows|
          rows.headings = ['Host', 'Job', 'Status', 'Exit Code', 'Queued', 'Schedule Date', 'Run Date']
          (0..(@schedule.length-1)).each do |i|
            s = @schedule[i]
            
            #Separate queued and unqueued jobs
            if @show_all
              if s[:scheduled] and !@schedule[i-1][:scheduled]
                rows.add_separator
              end
            end

            if s[:scheduled] or @show_all 
              rows << [@host, s[:job], s[:status], s[:exit], s[:scheduled], s[:schedule_date], s[:run_date]]
            elsif i == (@schedule.length-1)
              puts "\t> There are no scheduled jobs to list. Use adminware schedule-list --all to see history"
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
