require 'adminware/config'
require 'logger'

module Adminware
  class Log
    #Configure the logger
    def initialize
      @config = Adminware.config
      @logger = Logger.new(@config.logfile)
      @logger.level = Logger::DEBUG
      @logger.formatter = proc do |severity, datetime, progname, msg|
        date_format = datetime.strftime("%d-%m-%Y %H:%M:%S")
        "[#{date_format}]  #{severity.ljust(5)}: #{msg}\n"
      end
    end

    def method_missing(m,*args,&block)
      log.send(m,*args,&block)
    end

    #Return the logger
    def log(level, message)
      case level
      when 'info'
        @logger.info message
        puts "\t> #{message}"
      when 'error'
        @logger.error message
        $stderr.puts "\t> #{message}"
      when 'debug'
        @logger.debug message
      end  
    end
  end
end
