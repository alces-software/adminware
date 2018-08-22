#!/usr/bin/env ruby

$LOAD_PATH << File.dirname(__FILE__)

require 'cli'
require 'diag'
require 'manage'

# Setup args
command = ARGV.shift
subcommand = ARGV.shift
arg = ARGV.shift
options = ARGV.join(' ')

# Run command
case command
when "diag"
  cmd = Diag.new
when "manage"
  cmd = Manage.new
else
  puts "Invalid command: #{command}"
  puts "Usage"
  puts "  adminware diag/manage SUBCOMMAND [ARG] [OPTIONS]"
  puts ""
  puts "Subcommands"
  puts ""
  puts "  diag"
  puts "    top - Run the top command. ARG/OPTIONS will be passed as"
  puts "          arguments to the top command"
  puts "    iotop - Run the iotop command. ARG/OPTIONS will be passed as"
  puts "            arguments to the iotop command"
  puts "    ps - Run the ps command. ARG/OPTIONS will be passed as"
  puts "         arguments to the ps command"
  puts "    view_log - View a log file. If full path isn't provided it"
  puts "               will be searched for under /var/log"
  puts "" 
  puts "  manage"
  puts "    kill - Run the kill command on process ARG. OPTIONS will"
  puts "           be passed to the kill command"
  puts ""
  puts "Examples"
  puts ""
  puts "  Kill process normally"
  puts "    /opt/adminware/adminware.rb manage kill 1234"
  puts ""
  puts "  Kill process forcefully"
  puts "    /opt/adminware/adminware.rb manage kill 1234 -4"
  puts ""
  exit 1
end

cmd.run(subcommand, arg, options)
