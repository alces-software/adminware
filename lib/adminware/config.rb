require 'yaml'
require 'fileutils'

module Adminware
  class Config
    #Set default values for config settings
    DEFAULT_CENTRAL_JOBDIR = 'jobs/'
    DEFAULT_LOCAL_JOBDIR = 'var/adminware/jobs/'
    DEFAULT_LOGFILE = 'logs/adminware.log'
    DEFAULT_STATEDIR = 'var/'

    #Load the config file
    def initialize
      @config = YAML.load_file(File.join(Adminware.root, 'etc/config.yaml'))
    end

    #These methods return their respective file/directory
    def central_jobdir
      @centraljobdir ||= File.expand_path(@config['centraljobdir'] || DEFAULT_CENTRAL_JOBDIR)
    end

    def local_jobdir
      @localjobdir ||= File.expand_path(@config['localjobdir'] || DEFAULT_LOCAL_JOBDIR)
    end

    def logfile
      @logfile = File.expand_path(@config['logfile'] || DEFAULT_LOGFILE) 
      create_if_necessary(@logfile)
      @logfile
    end

    def statedir
      @statedir ||= File.expand_path(@config['statedir'] || DEFAULT_STATEDIR)
    end

    private

    #Create the file if it doesn't exist
    def create_if_necessary(file)
      if !File.exist?(file) then FileUtils.touch(file) end
    end
  end
end
