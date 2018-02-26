require 'yaml'

module Adminware
  module ConfigFile
    #Returns/Creates the config object
    def self.return
      @config ||= Config::new
    end

    #Calls the config object
    def self.config
      ConfigFile::return
    end

    class Config
      #Set default values for config settings
      DEFAULT_JOBDIR = "jobs/"
      DEFAULT_LOGFILE = "logs/adminware.log"
      DEFAULT_STATEFILE = "var/state.yaml"

      #Load the config file
      def initialize
        @path = File.expand_path(File.dirname(__FILE__)) 
        configfile = File.join(@path, '../../bin', 'config.yml')
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
          system "touch", "#{file}"
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
end