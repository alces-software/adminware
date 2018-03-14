require 'adminware/schedule_apply'
require 'adminware/schedule'

module Adminware
  module Commands
    module ScheduleCommands
      class << self
        def add(args, options)
          name = options.name
          host = options.host 
          forward = options.forward
          rewind = options.rewind

          if name.nil?
            puts "\t> Please enter a job to schedule. See adminware schedule-add --help for more info"
            exit 1
          end
 
          if host.nil?
            puts "\t> Please enter a host to schedule for. See adminware schedule-add --help for more info"
            exit 1
          end
      
          if forward && rewind
            puts "\t> Only specify one script to schedule for a job at a time"
            exit 1
          elsif forward 
            command = 'forward'
          elsif rewind 
            command = 'rewind'
          else
            puts "\t> Please enter a script to schedule. See adminware schedule-add --help for more more info"
            exit 1
          end
          
          schedule = Schedule.new(host)
          schedule.name = name
          schedule.command = command

          if schedule.valid?
            schedule.add_job
            schedule.save!
          end
        end
        
        def apply(args, options)
          host = options.host
      
          if host.nil?
            puts "\t> Please enter a host to apply the schedule for"
            exit 1
          end 
          
          ScheduleApply.run(host)
        end
        
        def clear(args, options)
          host = options.host
          
          if host.nil?
            puts "\t> Please enter a host to clear the schedule for"
            exit 1
          end

          file = Schedule.new(host)
          file.clear_schedule
        end
      end
    end
  end
end
