require 'adminware/job'
require 'adminware/state'

module Adminware
  module Commands
    module Run
    class << self
      def execute(args, options)
        name = args[0]
        host = options.connect
        forward = options.forward
        rewind = options.rewind
        state = State.new
         
        #Initialise the job
        job = Job.new(name, state)
        job.host = host
        
        #Check a job name has been given
        if name.nil?
          puts 'Please enter a job name. See adminware run --help for more info'
          exit 1
        end

        #Assign the requested script
        if forward
          job.command = 'forward'
        elsif rewind
          job.command = 'rewind'
        else
          puts "Please enter an option for the job. See adminware run --help for more info"
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
