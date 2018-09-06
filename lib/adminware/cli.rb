# frozen_string_literal: true

require 'thor'

module Adminware
  # Handle the application command line parsing
  # and the dispatch to various command objects
  #
  # @api public
  class CLI < Thor
    class << self
      # Hackery. Take the run method away from Thor so that we can define a
      # command with this name. Stolen from
      # https://github.com/ddollar/foreman/blob/c0b178c164396d6afe6fc3874abfd22f6cddbeae/lib/foreman/cli.rb#L29,L35.
      def is_thor_reserved_word?(word, type)
        return false if word == "run"
        super
      end
    end

    # Error raised by this runner
    Error = Class.new(StandardError)

    desc 'version', 'adminware version'
    def version
      require_relative 'version'
      puts "v#{Adminware::VERSION}"
    end
    map %w(--version -v) => :version
  end
end
