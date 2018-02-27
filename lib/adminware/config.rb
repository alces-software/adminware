require 'yaml'
require 'fileutils'

module Adminware
  class Config
    #Set default values for config settings
    DEFAULT_JOBDIR = "jobs/"
    DEFAULT_LOGFILE = "logs/adminware.log"
    DEFAULT_STATEFILE = "var/state.yaml"

    #Load the config file
    def initialize
      @path = Adminware::root 
      configfile = File.join(@path, '../etc', 'config.yaml')
      @config = YAML.load_file(configfile)

      #If no path given in config then set them to their defaults
      @jobdir = @config['jobdir'] ||= DEFAULT_JOBDIR
      @jobdir = set_path(@jobdir)

      @logfile = @config['logfile'] ||= DEFAULT_LOGFILE
      @logfile = set_path(@logfile)

      @statefile = @config['statefile'] ||= DEFAULT_STATEFILE
      @statefile = set_path(@statefile)
    end

    #These methods return their respective files
    def jobdir
      @jobdir
    end

    def logfile
      file_exist?(@logfile)
      @logfile
    end

    def statefile
     @statefile
    end

    private

    #Check if a file exists
    def file_exist?(file)
      if File.exist?(file)
        return true
      else
        #Create it if necessary
        FileUtils::touch "#{file}"
      end
    end

    #Sets the path for the given config setting
    def set_path(path)
      #Checks if the path is absolute or relative
      if File.exist?(path) == false
        path = File.join(@path,"..", path)
      else
        path
      end
    end
  end
end
