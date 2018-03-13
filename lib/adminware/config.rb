require 'yaml'
require 'fileutils'

module Adminware
  class Config
    #Set default values for config settings
    DEFAULT_CENTRAL_JOBDIR = 'jobs/'
    DEFAULT_LOCAL_JOBDIR = 'var/lib/adminware/jobs/'
    DEFAULT_LOGFILE = 'logs/adminware.log'
    DEFAULT_STATEDIR = 'var/state.yaml'

    #Load the config file
    def initialize
      @path = Adminware.root 
      configfile = File.join(@path, 'etc/config.yaml')
      @config = YAML.load_file(configfile)

      #If no path given in config then set them to their defaults
      @centraljobdir = @config['centraljobdir'] ||= DEFAULT_CENTRAL_JOBDIR
      @centraljobdir = set_path(@centraljobdir)

      @localjobdir = @config['localjobdir'] ||= DEFAULT_LOCAL_JOBDIR
      @localjobdir = set_path(@localjobdir)

      @logfile = @config['logfile'] ||= DEFAULT_LOGFILE
      @logfile = set_path(@logfile)

      @statedir = @config['statedir'] ||= DEFAULT_STATEDIR
      @statedir = set_path(@statedir)
    end

    #These methods return their respective files/directories
    def central_jobdir
      @centraljobdir
    end

    def local_jobdir
      @localjobdir
    end

    def logfile
      file_exist?(@logfile)
      @logfile
    end

    def statedir
      @statedir
    end

    private

    #Check if a file exists
    def file_exist?(file)
      if File.exist?(file)
        return true
      else
        #Create it if necessary
        FileUtils.touch "#{file}"
      end
    end

    #Sets the path for the given config setting
    def set_path(path)
      #Checks if the path is absolute or relative
      if File.exist?(path)
        path
      else
        path = File.join(Dir.home, path) 
      end
    end
  end
end
