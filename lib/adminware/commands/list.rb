require 'adminware/state'
require 'adminware/cli'
require 'adminware/job_list'
require 'adminware/state_list'
require 'adminware/schedule_list'

module Adminware
  module Commands
    module ListCommands 
      class << self
        #Handles command: adminware job-list 
        def job(args, options)
          name = options.name
          host = options.host
          plain = options.plain

          JobList.run(name, host, plain)
        end

        #Handles command: adminware state-list
        def state(args, options) 
          name = options.name
          host = options.host
          plain = options.plain
 
          StateList.run(name, host, plain)
        end

        #Handles command: adminware schedule-list
        def schedule(args, options)
          host = options.host
          show_all = options.all

          ScheduleList.run(host, show_all)
        end
      end
    end
  end
end
