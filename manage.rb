
class Manage

  attr_reader :allowed_commands

  def initialize
    @allowed_commands = ["kill", "pkill"]
  end

  def run(command, arg, options)
    @disallowed_users = ["root", "alces", "alces-cluster"]
    @arg = arg
    @options = options
    self._check_command_valid(command)

    # Run command
    send(command)
  end

  def _check_command_valid(command)
    unless @allowed_commands.include? command
      puts "Invalid command: #{command}"
      puts "Allowed commands: #{@allowed_commands.join(', ')}"
      exit 1
    end
  end

  def _check_process_valid(pid)
    # Something like ps u -p PID not equals root or alces
    pid_user = `ps -p #{pid} u --no-heading |awk '{print $1}'`.tr("\n", "")

    if pid_user.empty?
      puts "No such process #{pid}"
      exit 1
    end

    if @disallowed_users.include? pid_user
      puts "Cannot kill processes for user #{pid_user}"
      exit 1
    end

  end

  def kill
    if @arg.nil?
      puts "Must provide a process ID"
      exit 1
    end

    self._check_process_valid(@arg)
    args = [@arg, *@options.split(' ')]
    exec('kill', *args.compact) 

  end

  def pkill
    puts "pkill is currently not supported"
  end

end
