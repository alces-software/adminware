module Adminware
  module Commands
    module Run
    class << self
      def execute(args, options)
        name = options.name
        host = options.connect
        forward = options.forward
        rewind = options.rewind

        puts "Name = #{name}. Host = #{host}. Forward = #{forward}. Rewind = #{rewind}"
      end
    end
    end
  end
end
