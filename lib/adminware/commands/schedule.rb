require 'adminware/schedule_add'
require 'adminware/schedule_apply'

module Adminware
  module Commands
    module ScheduleCommands
      class << self
        def add(args, options)
          name = args[0]
          host = options.host ||= nil
          
          if host == nil
            puts 'Please enter a host to schedule for. See adminware schedule-add --help for more info'
            exit 1
          end
 
          if options.forward 
            command = 'forward'
          elsif options.rewind 
            command = 'rewind'
          else
            puts 'Please enter a script to schedule. See adminware schedule-add --help for more more info'
            exit 1
          end

          ScheduleAdd::run(name, host, command)
        end
        
        def apply(args, options)
          host = args[0]

          ScheduleApply::run(host)
        end
      end
    end
  end
end
