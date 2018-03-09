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
          which_output?(host)
        end
      end
      
      #Creates an array of hosts and sends them to be output to console
      def list_all_states
        hosts = []
        Dir["#{@config.statedir}*state.yaml"].each do |file|
          host = File.basename(file, '_state.yaml')
          hosts << host
        end

        if hosts.empty?
          puts "\t> No host state files to list, run a job first"
        else
          which_output?(hosts)
        end
      end
      
      #Checks if the -p option has been selected and outputs accordingly
      def which_output?(hosts)
        if @plain
          plain_output(hosts)
        else
          create_table(hosts)
        end
      end
      
      #Outputs state data in a tab delimited format
      def plain_output(hosts)
        puts "Host\tJob\tDescription\tStatus\tExit Code"
        (0..(hosts.length-1)).each do |i|
          state = State.new(hosts[i])
          state.file.each do |key, value|
            file = YAML.load_file(File.join(@config.jobdir, key, 'job.yaml'))
            if @name.nil? or key == @name
              print "#{hosts[i]}"
              print "\t#{key}"
              print "\t#{file['description']}"
              print "\t#{state.file[key][:status]}"
              print "\t#{state.file[key][:exit]}\n"
            else
              next
            end
          end
        end
      end 
      
      #Outputs state data in a table
      def create_table(hosts)
        table = Terminal::Table.new do |rows|
          rows.headings = ['Host', 'Job', 'Description', 'Status', 'Exit Code']
          (0..(hosts.length-1)).each do |i|
            state = State.new(hosts[i])
            state.file.each do |key, value|
              file = YAML.load_file(File.join(@config.jobdir, key, 'job.yaml'))       
              if @name.nil? or key == @name
                rows << [hosts[i], key, file['description'], state.file[key][:status], state.file[key][:exit]]
              else
                next
              end 
            end
            if hosts[i+1] != nil then rows.add_separator end
            rows.style = {:alignment => :center, :padding_left => 2, :padding_right => 2}
          end
        end
        puts table
      end
    end
  end
end
