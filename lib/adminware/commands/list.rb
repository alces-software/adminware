require 'adminware/state'
require 'adminware/cli'
require 'adminware/job_list'
require 'adminware/state_list'
require 'adminware/schedule_list'

module Adminware
  module Commands
    module ListCommands 
      class << self
        def job(args, options)
          name = options.name
          host = options.host
          plain = options.plain

          #Run the command
          JobList.run(name, host, plain)
        end

        def state(args, options) 
          name = options.name
          host = options.host
          plain = options.plain
 
          StateList.run(name, host, plain)
        end

        def schedule(args, options)
          host = options.host
          show_all = options.all

          ScheduleList.run(host, show_all)
        end
      end
    end
  end
end
