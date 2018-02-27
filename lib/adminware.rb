require 'adminware/config'
require 'adminware/log'

module Adminware
  class << self
    def config
      @config ||= Config.new
    end
    
    def log
      @logger ||= Log.new
    end
    
    def root
      @root ||= File.expand_path(File.dirname(__FILE__))
    end
  end
end
