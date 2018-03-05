require 'commander'
require 'adminware/commands/run'
require 'adminware/commands/list'
require 'adminware/commands/schedule'

module Adminware
  class CLI
    include Commander::Methods
      
    def run
      program :name, 'adminware'
      program :version, '0.0.1'
      program :description, 'adminware'

      command :run do |c|
        c.syntax = 'adminware run <name> [options]'
        c.description = 'Run a script locally or on another machine via SSH'
        c.example 'Run forward script for a job', 'adminware run <name> --forward'
        c.example 'Run forward script on another machine', 'adminware run <name> --connect HOST --forward'
        c.option '-c', '--connect HOST', String, 'Specify the host to run the job on'
        c.option '-f', '--forward', 'Run the forward script for <name>'
        c.option '-r', '--rewind', 'Run the rewind script for <name>'
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
        c.example 'List values for NAME', 'adminware list --job NAME'
        c.example 'List values for every job', 'adminware list -all'
        c.example 'List values for NAME in a tab delimited format', 'adminware list --job NAME --plain'
        c.option '-a', '--all', 'Lists all available jobs'
        c.option '-j', '--job NAME', String, 'Specify the name of the job to list'
        c.option '-p', '--plain', 'Output in a tab delimited format'
        c.option '--host HOST', String, 'Specify the host you wish to view the jobs for'
        c.action do |args, options|
          options.default \
            :host => 'local',
            :plain => false,
            :all => false
          Commands::ListCommands.execute(args, options)
        end
      end
      
      command :'schedule-add' do |c|
        c.syntax = 'adminware schedule-add <name> [options]'
        c.description = 'Schedule a job for a host'
        c.option '--host HOST', String, 'Specify the host to schedule jobs for'
        c.option '-f', '--forward', 'Schedule the forward script for <name> on <host>'
        c.option '-r', '--rewind', 'Schedule the rewind script for <name> on <host>'
        c.action do |args, options|
          Commands::ScheduleCommands.add(args, options)
        end
      end

      command :'schedule-apply' do |c|
        c.syntax = 'adminware schedule-apply <host>'
        c.description = 'Apply the schedule for a host'
        c.action do |args, options|
          Commands::ScheduleCommnands.apply(args, options)
        end
      end

      run!
    end
  end
end
