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
          listcmd = 'all'
        elsif name.empty? == false
          listcmd = 'job'
        end
        
        #Initialise the list
        #TODO Change ListCommands to a module?
        list = ListCommands::new(name, listcmd, state)
        
        #Run the command
        list.run     
      end
    end
    end
  end
end
