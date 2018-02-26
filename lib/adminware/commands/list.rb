require 'adminware/list'
require 'adminware/state'

module Adminware
  module Commands
    module List 
    class << self
      def execute(args, options)
        name = options.name
        all = options.all
        state = State.new
        
        #Assign the requested command      
        if all == true
          command = 'all'
        elsif name.empty? == false
          command = 'job'
        end
        
        #Run the command
        ListCommands::run(name, command, state)     
      end
    end
    end
  end
end
