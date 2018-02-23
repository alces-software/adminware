module Adminware
  module Commands
    module List 
    class << self
      def execute(args, options)
        name = options.name
        all = options.all

        puts "Name = #{name}. All = #{all}"
      end
    end
    end
  end
end
