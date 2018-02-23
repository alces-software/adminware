require 'config'
module Adminware
  module EventLogger
    class Log
      #Configure the logger
      def initialize
          @logger = Logger.new(config.logfile)
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

    #Returns/Creates the logger
    def self.log
      @log ||= Log::new
    end

    def log(level, message)
      @logger = EventLogger::log
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
  end
end    
