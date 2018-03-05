require 'adminware/schedule_apply'
require 'adminware/schedule'

module Adminware
  module Commands
    module ScheduleCommands
      class << self
        def add(args, options)
          name = args[0]
          host = options.host ||= nil
         
          if name.nil?
            puts "\t> Please enter a job to schedule. See adminware schedule-add --help for more info"
            exit 1
          end
 
          if host.nil?
            puts "\t> Please enter a host to schedule for. See adminware schedule-add --help for more info"
            exit 1
          end
 
          if options.forward 
            command = 'forward'
          elsif options.rewind 
            command = 'rewind'
          else
            puts "\t> Please enter a script to schedule. See adminware schedule-add --help for more more info"
            exit 1
          end
          
          file = Schedule.new(host)
          file.name = name
          file.command = command

          if file.validate!
            file.add_job
            file.save!
          else
            puts "\t> Failed to validate!"
          end
        end
        
        def apply(args, options)
          host = args[0]
          
          ScheduleApply::run(host)
        end
      end
    end
  end
end
