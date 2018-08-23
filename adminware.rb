#!/usr/bin/env ruby

$LOAD_PATH << File.dirname(__FILE__)

require 'cli'
require 'command'
require 'yaml'

module Adminware
  
  def self.config
    @config ||= YAML.load_file("#{File.dirname(__FILE__)}/commands.yaml")
  end

end

# Setup args
command = Command.new

subcommand = ARGV.shift
arg = ARGV.shift
options = ARGV.join(' ')

# Run command
if command.valid?(subcommand)
  command.run(subcommand, arg, options)
else
  puts "Usage"
  puts "  adminware diag/manage SUBCOMMAND [ARG] [OPTIONS]"
  puts ""
  puts "Subcommands"
  puts ""
  Adminware.config.each do |mode, subcommands|
    puts "  #{mode}"
    subcommands.each do |mode_cmd, details|
      puts "    - #{mode_cmd}: #{details['description']}"
    end
  end
  puts ""
  puts "Examples"
  puts ""
  puts "  View log file /var/log/messages"
  puts "    admin view_log messages"
  puts ""
  puts "  Kill process normally"
  puts "    admin kill 1234"
  puts ""
  puts "  Kill process forcefully"
  puts "    admin kill -9 1234"
  puts ""
  exit 1
end

cmd.run(subcommand, arg, options)
