require 'adminware/config'
require 'logger'

module Adminware
  module EventLogger
    #Returns/Creates the logger    
    def self.return
      @log ||= Log::new
    end
    
    def self.log(level, message)
      @logger = EventLogger::return
      case level
      when 'info'
        @logger.info message
        puts message
      when 'error'
        @logger.error message
        $stderr.puts message
      when 'debug' 
        @logger.debug message
      end
    end

    class Log
      #Configure the logger
      def initialize
          @logger = Logger.new(ConfigFile::config.logfile)
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
      def log
        @logger
      end
    end
  end
end    
