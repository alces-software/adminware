# frozen_string_literal: true

require_relative '../command'

module Adminware
  module Commands
    class Run < Adminware::Command
      def initialize(tool, options)
        @tool = tool
        @options = options
      end

      def execute(input: $stdin, output: $stdout)
        # Command logic goes here ...
        output.puts "OK"
      end
    end
  end
end
