require 'adminware'
require 'adminware/config'
require 'adminware/state'
require 'fileutils'
require 'terminal-table'

module Adminware
  module StateList
    class << self
      def run(name, host, boolean)
        @name = name
        @host = host 
        @state = State.new(host)
        @config = Adminware.config
        @plain = boolean
        
        if @host.nil?
          list_all_states
        else
          host = [@host]
          output(host)
        end
      end
      
      #Creates an array of hosts and sends them to be output to console
      def list_all_states
        hosts = []
        Dir["#{@config.statedir}/*state.yaml"].each do |file|
          host = File.basename(file, '_state.yaml')
          hosts << host
        end

        if hosts.empty?
          puts "\t> No host state files to list, run a job first"
        else
          output(hosts)
        end
      end
      
      #Checks if the -p option has been selected and outputs accordingly
      def output(hosts)
        @plain ? plain_output(hosts) : table_output(hosts)
      end
      
      #Outputs state data in a tab delimited format
      def plain_output(hosts)
        puts "Host\tJob\tDescription\tStatus\tExit Code"
        (0..(hosts.length-1)).each do |i|
          state = State.new(hosts[i])
          state.file.each do |key, value|
            if @name.nil? or key == @name
              print "#{hosts[i]}"
              print "\t#{key}"
              print "\t#{get_description(hosts[i], key)}"
              print "\t#{state.file[key][:status]}"
              print "\t#{state.file[key][:exit]}\n"
            else
              next
            end
          end
        end
      end 
      
      #Outputs state data in a table
      def table_output(hosts)
        table = Terminal::Table.new do |rows|
          rows.headings = ['Host', 'Job', 'Description', 'Status', 'Exit Code']
          (0..(hosts.length-1)).each do |i|
            state = State.new(hosts[i])
            state.file.each do |key, value|
              if @name.nil? or key == @name
                s = state.file[key]
                rows << [hosts[i], key, get_description(hosts[i], key), s[:status], s[:exit]]
              else
                next
              end 
            end
            if hosts[i+1] != nil && @name.nil? then rows.add_separator end
            rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
          end
        end
        puts "\n#{table}"
      end

      def get_description(host, key)
        file = File.join(find_directory(key), 'job.yaml') rescue file = '' 
        if File.exist?(file)
          file = YAML.load_file(file)
          file['description']
        elsif check_remotely(host, key)
          @desc
        else
          'No description available'
        end
      end

      def find_directory(key)
        central = File.join(@config.central_jobdir, key)
        local = File.join(@config.local_jobdir, key)
        if Dir.exist?(central)
          central
        elsif Dir.exist?(local)
          local
        end
      end

      def check_remotely(host, key)
        stdout, stderr, status = Open3.capture3("ssh #{host} cat #{@config.local_jobdir}/#{key}/job.yaml")
        if status.success?
          @desc = stdout[18..-3]
        else
          false
        end
      end
    end
  end
end
