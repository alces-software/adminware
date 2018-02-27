require 'adminware'
require 'adminware/config'
require 'yaml'

module Adminware
  class State
    def initialize
      @config = Adminware::config
      load_state(@config.statefile)
    end

    #Checks the current state of the given job
    def status(name)
      @state[name][:status] rescue nil
    end

    #Toggles state of current job
    def toggle(name, command)
      jobstate(name)[:status] = command
    end

    def set_exit(name, code)
      jobstate(name)[:exit] = code
    end

    #Save the job's state to file
    def save!
      File::write(@config.statefile, @state.to_yaml)
    end

    def print
      @state
    end

    private

    def jobstate(name)
      @state[name] ||= {}
    end

    def load_state(statefile)
      @state = YAML::load_file(statefile) rescue {}
    end
  end
end

