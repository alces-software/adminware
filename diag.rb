
class Diag 

  attr_reader :allowed_commands

  def initialize
    @allowed_commands = Adminware.config['diag'].keys
  end

  def run(command, arg, options)
    @arg = arg
    @options = options
    self._check_valid(command)

    # Run command
    send(command)
  end

  def _check_valid(command)
    unless @allowed_commands.include? command
      puts "Invalid command: #{command}"
      puts "Allowed commands: #{@allowed_commands.join(', ')}"
      exit 1
    end
  end

  def top
    args = [@arg, *@options.split(' ')]
    exec('top', *args.compact)
  end

  def iotop
    args = [@arg, *@options.split(' ')]
    exec('iotop', *args.compact)
  end

  def ps
    args = [@arg, *@options.split(' ')]
    exec('ps', *args.compact)
  end

  def dmidecode
    args = [@arg, *@options.split(' ')]
    exec('dmidecode', *args.compact)
  end

  def dmesg
    args = [@arg, *@options.split(' ')]
    exec('dmesg', *args.compact)
  end

  def lsof
    args = [@arg, *@options.split(' ')]
    exec('lsof', *args.compact)
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

end
