# frozen_string_literal: true

require 'logger'
require 'terrapin'
require 'tty-command'
require 'yaml'

require_relative '../command'


# XXX Move/refactor/test all the things
class Tool
  attr_reader :tool_path, :config

  def initialize(tool_parts)
    @tool_path = File.join('tools', tool_parts)
    config_path = File.join(@tool_path, 'config.yaml')
    @config = YAML.load_file(config_path)
  end

  def run
    command = @config['command']
    c = TTY::Command.new(uuid: false)
    # c.run(command, chdir: @tool_path, pty: true) # XXX `pty` allows top to work but no input accepted
    c.run(command, chdir: @tool_path)
  end
end

module Adminware
  module Commands
    class Run < Adminware::Command
      attr_reader :tool

      def initialize(tool_parts, options)
        @tool = Tool.new(tool_parts)

        @options = options
      end

      def execute(input: $stdin, output: $stdout)
        @tool.run
      end
    end
  end
end
