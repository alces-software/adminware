require 'adminware/job'
require 'adminware/state'
require 'adminware/firstrun'

module Adminware
  module Commands
    module Run
      class << self
        def execute(args, options)
          name = options.name
          host = options.host
          forward = options.forward
          rewind = options.rewind
          state = State.new(host)

          if options.firstrun
            FirstRun.start
          else
            #Check a job name has been given
            if name.nil?
              puts "\t> Please enter a job name. See adminware job-run --help for more info"
              exit 1
            end

            #Check a host name has been given
            if host.nil?
              puts "\t> Please enter a host to run the job on. See adminware job-run --help for more info"
              exit 1
            end

            #Assign the requested script
            if forward && rewind
              puts "\t> Only specify one script to run for a job at a time"
              exit 1
            elsif forward
              command = 'forward'
            elsif rewind
              command = 'rewind'
            else
              puts "\t> Please enter an option for the job. See adminware job-run --help for more info"
              exit 1
            end

            #Initialise the job
            job = Job.new(name, command, host)
            job.state = state

            #Attempt to validate the command
            if job.valid?
              #Run the script for the job
              job.run
              state.save!
            end
          end
        end
      end
    end
  end
end
