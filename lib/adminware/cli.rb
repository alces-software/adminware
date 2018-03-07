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

      command :'job-run' do |c|
        c.syntax = 'adminware job-run [options]'
        c.description = 'Run a script locally or on another machine via SSH'
        c.example 'Run forward script for a job', 'adminware run --name NAME --forward'
        c.example 'Run forward script on another machine', 'adminware run --name NAME --host HOST --forward'
        c.option '-n', '--name NAME', String, 'Specify the job to run'
        c.option '--host HOST', String, 'Specify the host to run the job on'
        c.option '-f', '--forward', 'Run the forward script for <name>'
        c.option '-r', '--rewind', 'Run the rewind script for <name>'
        c.action do |args, options|
          options.default \
            :forward => false,
            :rewind => false
          Commands::Run.execute(args, options)
        end
      end

      command :'job-list' do |c|
        c.syntax = 'adminware job-list [options]'
        c.description = 'Lists details about jobs'
        c.example 'List values for NAME', 'adminware list --name NAME'
        c.example 'List values for every job', 'adminware list -all'
        c.example 'List values for NAME in a tab delimited format', 'adminware list --name NAME --plain'
        c.option '-a', '--all', 'Lists all available jobs'
        c.option '-n', '--name NAME', String, 'Specify the name of the job to list'
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
     
      command :'state-list' do |c|
        c.syntax = 'adminware state-list [options]'
        c.description = 'List the state values for all run jobs'
        c.option '-n', '--name NAME', String, 'Filter for a specific job'
        c.option '--host HOST', String, 'Filter for a specific host'
        c.action do |args, options|
        end
      end
 
      command :'schedule-add' do |c|
        c.syntax = 'adminware schedule-add [options]'
        c.description = 'Schedule a job for a host'
        c.example 'Add a job to the schedule', 'adminware schedule-add <name> --host HOST --forward'
        c.option '-n', '--name NAME', String, 'Specify the job to add'
        c.option '--host HOST', String, 'Specify the host to schedule jobs for'
        c.option '-f', '--forward', 'Schedule the forward script for <name> on <host>'
        c.option '-r', '--rewind', 'Schedule the rewind script for <name> on <host>'
        c.action do |args, options|
          Commands::ScheduleCommands.add(args, options)
        end
      end

      command :'schedule-apply' do |c|
        c.syntax = 'adminware schedule-apply [options]'
        c.description = 'Apply the schedule for a host'
        c.option '--host HOST', String, 'Specify a host to apply the schedule for'
        c.action do |args, options|
          Commands::ScheduleCommands.apply(args, options)
        end
      end
      
      command :'schedule-clear' do |c|
        c.syntax = 'adminware schedule-clear [options]'
        c.description = 'Clear the schedule for a host'
        c.option '--host HOST', String, 'Specify a host to clear the schedule for'
        c.action do |args, options|
          Commands::ScheduleCommands.clear(args, options)    
        end
      end

      command :'schedule-list' do |c|
        c.syntax = 'adminware schedule-list [options]'
        c.description = 'List the schedule for a host'
      end

      run!
    end
  end
end
