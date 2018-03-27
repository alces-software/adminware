require 'adminware/schedule_apply'
require 'adminware/schedule_remove'
require 'adminware/schedule'
require 'highline'

module Adminware
  module Commands
    module ScheduleCommands
      class << self
        def add(args, options)
          name = options.name
          host = options.host 
          forward = options.forward
          rewind = options.rewind
          group = options.group

          if name.nil?
            puts "\t> Please enter a job to schedule. See adminware schedule-add --help for more info"
            exit 1
          end
 
          if host.nil? && group.nil?
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
          
          schedule = Schedule.new(host, group)

          if schedule.valid?(name, command)
            schedule.add_job(name, command)
            schedule.save!
          end
        end
        
        def remove(args, options)
          name = options.name
          host = options.host
          id = options.id
          group = options.group

          if options.all 
            clear(args, options)
          elsif host.nil? && group.nil?
            puts "\t> Please enter a host or group to remove from the schedule of"
            exit 1
          elsif name.nil? && id.nil?
            puts "\t> Please enter the name or ID of job(s) to remove from the schedule" 
            exit 1
          elsif !name.nil? && !id.nil?
            puts "\t> Please enter either the name or the ID of the job(s) you wish to remove from the schedule" 
          else
            ScheduleRemove.run(host, group, name, id)
          end
        end
        
        def apply(args, options)
          host = options.host
          group = options.group 

          if host.nil? && group.nil?
            puts "\t> Please enter a host or group to apply the schedule for"
            exit 1
          elsif !host.nil? && !group.nil?
            puts "\t> Please enter either a host or a group to apply the schedule for"
            exit 1 
          end
          
          ScheduleApply.run(host, group)
        end
        
        def clear(args, options)
          host = options.host
          cli = HighLine.new
 
          if host.nil?
            puts "\t> Please enter a host to clear the schedule for"
            exit 1
          end
          
          unless options.force
            exit unless cli.agree("\t> Clear schedule for #{host}? (y/n)")
          end

          file = Schedule.new(host, nil)
          file.clear_schedule
        end
      end
    end
  end
end
