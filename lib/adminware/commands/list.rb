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
              
        if all == true
          listcmd = 'all'
        elsif name.empty? == false
          listcmd = 'job'
        end

        list = ListCommands::new(name, listcmd, state)
        list.run     
      end
    end
    end
  end
end
