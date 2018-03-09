require 'adminware/job'
require 'adminware/state'

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
           
          #Initialise the job
          job = Job.new(name, state)
          job.host = host
          
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
          if forward and rewind
            puts "\t> Only specify one script to run for a job at a time"
            exit 1
          end

          if forward
            job.command = 'forward'
          elsif rewind
            job.command = 'rewind'
          else
            puts "Please enter an option for the job. See adminware job-run --help for more info"
            exit 1
          end
         
          #Attempt to validate the command
          job.validate!
                  
          #Run the script for the job
          job.run
          state.save!
        end
      end
    end
  end
end
