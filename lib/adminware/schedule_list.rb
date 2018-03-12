require 'adminware'
require 'adminware/schedule'
require 'fileutils'
require 'terminal-table'

module Adminware
  module ScheduleList
    class << self
      def run(host, boolean)
        @host = host
        @show_all = boolean

        list_schedule
      end

      def list_schedule
        schedule_exists?
        print_schedule
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

      #Output the schedule in a table for the given host
      def print_schedule
        @file = Schedule.new(@host)
        @schedule = @file.load_array
        table = Terminal::Table.new :title => 'Scheduled Jobs' do |rows|
          rows.headings = ['Host', 'Job', 'Status', 'Exit Code', 'Queued']
          (0..(@schedule.length-1)).each do |i|
            s = @schedule[i]
            
            #Separate queued and unqueued jobs
            if @show_all
              if s[:scheduled] and !@schedule[i-1][:scheduled]
                rows.add_separator
              end
            end

            if s[:scheduled] or @show_all 
              rows << [@host, s[:job], s[:status], s[:exit], s[:scheduled]]
            elsif i == (@schedule.length-1)
              puts "\t> There are no scheduled jobs to list. Use adminware schedule-list --all to see history"
              exit 1
            end
          end
          rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
        end
        puts table
      end
    end
  end
end
