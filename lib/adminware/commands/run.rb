require 'adminware/job'
require 'adminware/state'

module Adminware
  module Commands
    module Run
    class << self
      def execute(args, options)
        name = options.name
        host = options.connect
        forward = options.forward
        rewind = options.rewind
        state = State.new
        
        #Initialise the job
        job = Job.new(name, state)
        job.host = host

        #Assign the request script
        if forward == true
          job.command = 'forward'
        elsif rewind == true
          job.command = 'rewind'
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
