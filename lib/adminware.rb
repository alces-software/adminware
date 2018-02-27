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
  end
end
