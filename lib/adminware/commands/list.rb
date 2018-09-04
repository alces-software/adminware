require 'adminware/state'
require 'adminware/cli'
require 'adminware/job_list'
require 'adminware/state_list'
require 'adminware/schedule_list'
require 'adminware/group_list'

module Adminware
  module Commands
    module ListCommands
      class << self
        #Handles command: adminware job-list
        def job(args, options)
          JobList.run(options.name, options.host, options.plain)
        end

        #Handles command: adminware state-list
        def state(args, options)
          StateList.run(options.name, options.host, options.plain)
        end

        #Handles command: adminware schedule-list
        def schedule(args, options)
          if options.group.nil?
            ScheduleList.run(options.host, options.all, options.plain)
          else
            GroupList.run(options.group, options.exit, options.all, options.plain)
          end
        end
      end
    end
  end
end
