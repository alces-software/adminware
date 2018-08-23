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
  puts "  Diag:"
  Diag.new.allowed_commands.each do |cmd|
    puts "    - #{cmd}"
  end
  puts "" 
  puts "  Manage:"
  Manage.new.allowed_commands.each do |cmd|
    puts "    - #{cmd}" 
  end
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
