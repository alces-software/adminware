
class Manage

  attr_reader :allowed_commands

  def initialize
    @allowed_commands = Adminware.config['manage'].keys
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
    args = [@arg, *@options.split(' ')]
    exec('kill', *args.compact) 
  end

  def pkill
    args = [@arg, *@options.split(' ')]
    exec('pkill', *args.compact)
  end

  def mount
    args = [@arg, *@options.split(' ')]
    exec('mount', *args.compact)
  end

  def umount
    args = [@arg, *@options.split(' ')]
    exec('umount', *args.compact)
  end

  def _sudoedit(file)
    tmpfile = "/tmp/#{File.basename(file)}.#{('a'..'z').to_a.shuffle[0,8].join}"

    # Create copy of file
    system("cp #{file} #{tmpfile}")
    # Set ownership to SUDO_USER
    system("chown #{ENV['SUDO_USER']} #{tmpfile}")
    # Open for editing by SUDO_USER
    system("su - #{ENV['SUDO_USER']} -c 'vim #{tmpfile}'")
    # Replace if diff
    unless system("diff -q #{file} #{tmpfile} >> /dev/null")
      system("cp -f --no-preserve=mode,ownership #{tmpfile} #{file}")
    else
      puts "No changes made"
    end

    # Remove tmpfile
    system("rm -f #{tmpfile}")
  end

  def limits
    self._sudoedit('/etc/security/limits.conf')
  end

  def motd
    self._sudoedit('/opt/clusterware/etc/motd')
  end

end
