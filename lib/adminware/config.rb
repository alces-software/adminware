require 'yaml'
require 'fileutils'

module Adminware
  class Config
    #Set default values for config settings
    DEFAULT_CENTRAL_JOBDIR = 'jobs/'
    DEFAULT_LOCAL_JOBDIR = 'var/adminware/jobs/'
    DEFAULT_LOGFILE = 'logs/adminware.log'
    DEFAULT_STATEDIR = 'var/state.yaml'

    #Load the config file
    def initialize
      configfile = File.join(Adminware.root, 'etc/config.yaml')
      @config = YAML.load_file(configfile)
    end

    #These methods return their respective files/directories
    def central_jobdir
      @centraljobdir ||= resolve_path(@config['centraljobdir'] || DEFAULT_CENTRAL_JOBDIR)
    end

    def local_jobdir
      @localjobdir ||= resolve_path(@config['localjobdir'] || DEFAULT_LOCAL_JOBDIR)
    end

    def logfile
      @logfile = resolve_path(@config['logfile'] || DEFAULT_LOGFILE) 
      create_if_necessary(@logfile)
      @logfile
    end

    def statedir
      @statedir ||= resolve_path(@config['statedir'] || DEFAULT_STATEDIR)
    end

    private

    #Create the file if it doesn't exist
    def create_if_necessary(file)
      if !File.exist?(file)
        FileUtils.touch(file)
      end
    end

    #Sets the path for the given config setting
    def resolve_path(path)
      #Checks if the path is absolute or relative
      File.exist?(path) ? path : File.join(Dir.home, path)
    end
  end
end
