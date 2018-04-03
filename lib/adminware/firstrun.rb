require 'adminware/config'
require 'adminware/state'
require 'adminware/job'
require 'adminware'
require 'open3'
require 'yaml'

module Adminware
  module FirstRun
    class << self
      def start 
        file = Adminware.log
        config = Adminware.config
        @state = State.new('local')
        @jobs = []
        
        file.log('info', '-- FirstRun: Start  --') 
        get_firstrun_jobs(config.central_jobdir) if Dir.exist?(config.central_jobdir)
        get_firstrun_jobs(config.local_jobdir) if Dir.exist?(config.local_jobdir)
        run_jobs
        file.log('info', '-- FirstRun: Finish --')
      end
    
      def get_firstrun_jobs(directory)
        Dir.foreach(directory) do |item|
          next if item == '.' or item == '..'
         
          file_path = File.join(directory, item, 'job.yaml')
          if File.exist?(file_path)
            metadata = YAML.load_file(file_path)
            @jobs << item if metadata['firstrun']
          end
        end  
      end

      def run_jobs
        @jobs.each do |job|
          job = Job.new(job, 'forward', 'local')
          job.state = @state

          if job.valid?
            job.run
            @state.save!
          end
        end
      end
    end
  end
end
