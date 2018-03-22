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
      program :description, 'Set of tools for running and scheduliing jobs'

      command :'job-run' do |c|
        c.syntax = 'adminware job-run [options]'
        c.description = 'Run a script locally or on another machine via SSH'
        c.example 'Run forward script for a job', 'adminware run --host HOST --name NAME --forward'
        c.example 'Run rewind script for a job', 'adminware run --host HOST --name NAME --rewind'
        c.option '-n', '--name NAME', String, 'Specify the job to run'
        c.option '-H', '--host HOST', String, 'Specify the host to run the job on'
        c.option '-f', '--forward', 'Run the forward script for <name>'
        c.option '-r', '--rewind', 'Run the rewind script for <name>'
        c.action do |args, options|
          options.default( 
            forward: false,
            rewind:  false
          )
          Commands::Run.execute(args, options)
        end
      end

      command :'job-list' do |c|
        c.syntax = 'adminware job-list [options]'
        c.description = 'Lists all available jobs for a host'
        c.example 'List all jobs for a host', 'adminware job-list --host HOST'
        c.option '-p', '--plain', 'Output in a tab delimited format'
        c.option '-H', '--host HOST', String, 'Specify the host you wish to view the jobs for'
        c.action do |args, options|
          options.default(host: 'local') 
          Commands::ListCommands.job(args, options)
        end
      end
     
      command :'state-list' do |c|
        c.syntax = 'adminware state-list [options]'
        c.description = 'List the state values for all run jobs'
        c.example 'List all states for a specific job', 'adminware state-list --name NAME'
        c.example 'List all states for a specific host', 'adminware state-list --host HOST'
        c.option '-n', '--name NAME', String, 'Filter for a specific job'
        c.option '-H', '--host HOST', String, 'Filter for a specific host'
        c.option '-p', '--plain', 'Output in a tab delimited format'
        c.action do |args, options|
          Commands::ListCommands.state(args, options)
        end
      end
 
      command :'schedule-add' do |c|
        c.syntax = 'adminware schedule-add [options]'
        c.description = 'Schedule a job for a host'
        c.example 'Add a job to the schedule', 'adminware schedule-add --host HOST --name NAME --forward'
        c.option '-n', '--name NAME', String, 'Specify the job to add'
        c.option '-H', '--host HOST', String, 'Specify the host to schedule jobs for'
        c.option '-f', '--forward', 'Schedule the forward script for <name> on <host>'
        c.option '-r', '--rewind', 'Schedule the rewind script for <name> on <host>'
        c.action do |args, options|
          Commands::ScheduleCommands.add(args, options)
        end
      end
      
      command :'schedule-remove' do |c|
        c.syntax = 'adminware schedule-remove [options]'
        c.description = 'Remove job(s) from the schedule'
        c.option '-n', '--name NAME', String, 'Specify the job to remove'
        c.option '-H', '--host HOST', String, 'Specify the host to remove job(s) from'
        c.option '-i', '--id ID', Numeric, 'Specify the ID of the job to remove'
        c.option '-a', '--all', 'Clear the schedule for HOST'
        c.option '--force', 'Clear the schedule without a prompt'
        c.action do |args, options|
          Commands::ScheduleCommands.remove(args, options)
        end
      end

      command :'schedule-apply' do |c|
        c.syntax = 'adminware schedule-apply [options]'
        c.description = 'Apply the schedule for a host'
        c.example 'Apply the schedule for a given host', 'adminware schedule-apply --host HOST'
        c.option '-H', '--host HOST', String, 'Specify a host to apply the schedule for'
        c.action do |args, options|
          Commands::ScheduleCommands.apply(args, options)
        end
      end
      
      command :'schedule-list' do |c|
        c.syntax = 'adminware schedule-list [options]'
        c.description = 'List the schedule for a host'
        c.example 'List all items in the schedule', 'adminware schedule-list --host HOST --all'
        c.option '-H', '--host HOST', String, 'Specify a host to list the schedule for'
        c.option '-a', '--all', 'Show all jobs in the schedule, history included'
        c.option '-p', '--plain', 'Output in a tab delimited format'
        c.action do |args, options|
          options.default(host: 'local')
          Commands::ListCommands.schedule(args, options)
        end
      end

      run!
    end
  end
end
