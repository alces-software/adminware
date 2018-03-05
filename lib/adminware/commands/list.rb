require 'adminware/list'
require 'adminware/state'
require 'adminware/cli'
module Adminware
  module Commands
    module ListCommands 
      class << self
        def execute(args, options)
          name = options.job
          all = options.all
          host = options.host
          plain = options.plain

          #Assign the requested command      
          if all
            command = 'all'
          elsif !name.nil?
            command = 'job'
          else
            puts "Please enter a valid command. See adminware list --help for more info"
            exit 1
          end
          
          #Run the command
          List::run(name, command, host, plain)
        end
      end
    end
  end
end
