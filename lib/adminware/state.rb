require 'adminware'
require 'adminware/config'
require 'yaml'

module Adminware
  class State
    def initialize(host)
      @host = host
      @config = Adminware.config
      @statefile = File.join(@config.statedir, "#{@host}_state.yaml")

      load_state
    end

    #Checks the current state of the given job
    def status(name)
      @state[name][:status] rescue nil
    end

    #Toggles state of current job
    def toggle(name, command)
      jobstate(name)[:status] = command
    end
    
    #Set the exit code of the job
    def set_exit(name, code)
      jobstate(name)[:exit] = code
    end

    #Save the job's state to file
    def save!
      File.write(@statefile, @state.to_yaml)
    end
    
    #Return the state file
    def file
      @state
    end

    private

    def jobstate(name)
      @state[name] ||= {}
    end
    
    #Loads the state file
    def load_state
      @state = YAML.load_file(@statefile) rescue {}
    end
  end
end

