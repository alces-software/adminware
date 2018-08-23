
class Command

  def initialize
    @allowed_commands = Adminware.config['diag'].keys + Adminware.config['manage'].keys
  end

  def run(command, arg, options)
    @arg = arg
    @options = options

    # Run command
    if respond_to?(command)
      send(command)
    else
      run_command(command)
    end
  end

  def valid?(command)
    unless @allowed_commands.include? command
      return false
    end
    return true
  end

  def run_command(command)
    args = [@arg, *@options.split(' ')]
    exec(command, *args.compact)
  end

  def view_log
    if @arg.nil?
      puts "Must pass a logfile name"
      exit 1
    end

    unless File.file? @arg
      unless File.file? "/var/log/#{@arg}"
        puts "No such file or directory: #{@arg} or /var/log/#{@arg}"
        exit 1
      end
      @arg = "/var/log/#{@arg}"
    end

    args = [@arg, *@options.split(' ')]
    exec({'LESSSECURE' => '1' }, 'less', *args.compact)
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
