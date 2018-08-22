require 'optparse'

class MainParser

  def self.parse(args)

    options = {}

    opt_parser = OptionParser.new do |opt|
      opt.banner = "Usage: diag COMMAND [OPTIONS]"
      opt.separator ""
      opt.separator "Commands:"
      opt.separator "    diag: Run diagnostic command"
      opt.separator "    manage: Run management command"
      opt.separator ""
      opt.separator "Options:"

      opt.on("-v","--verbose","Print additional debugging information") do |verbose|
        options["verbose"] = verbose
      end


    end
    opt_parser.parse!(args)
    return options
  end
end
