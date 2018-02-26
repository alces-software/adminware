require 'commander'
require 'adminware/commands/run'
require 'adminware/commands/list'

module Adminware
class CLI
  include Commander::Methods
    
  def run
    program :name, 'adminware'
    program :version, '0.0.1'
    program :description, 'adminware'
    global_option '-n', '--name NAME', String, 'Specify the name of the job'

    command :run do |c|
      c.syntax = 'adminware run [options]'
      c.description = 'Run a script locally or on another machine via SSH'
      c.example 'Run forward script for a job', 'adminware run --name NAME --forward'
      c.example 'Run forward script on another machine', 'adminware run --name NAME --connect HOST --forward'
      c.option '-c', '--connect HOST', String, 'Specify the host to run the job on'
      c.option '-f', '--forward', 'Run the forward script for NAME'
      c.option '-r', '--rewind', 'Run the rewind script for NAME'
      c.action do |args, options|
        options.default \
          :connect => 'local',
          :forward => false,
          :rewind => false
        Commands::Run.execute(args, options)
      end
    end

    command :list do |c|
      c.syntax = 'adminware list [options]'
      c.description = 'Lists details about jobs'
      c.example 'List values for NAME', 'adminware list --name NAME'
      c.option '-a', '--all', 'Lists all available jobs'
      c.action do |args, options|
        options.default \
          :all => false
        Commands::List.execute(args, options)
      end
    end

    run!
  end
end
end
