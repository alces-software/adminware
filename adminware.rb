#!/usr/bin/env ruby

$LOAD_PATH << File.dirname(__FILE__)

require 'cli'
require 'diag'
require 'manage'
require 'yaml'

module Adminware
  
  def self.config
    @config ||= YAML.load_file("#{File.dirname(__FILE__)}/commands.yaml")
  end

end

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
  puts "    sudo /opt/adminware/adminware.rb diag view_log messages"
  puts ""
  puts "  Kill process normally"
  puts "    sudo /opt/adminware/adminware.rb manage kill 1234"
  puts ""
  puts "  Kill process forcefully"
  puts "    sudo /opt/adminware/adminware.rb manage kill -9 1234"
  puts ""
  exit 1
end

cmd.run(subcommand, arg, options)
