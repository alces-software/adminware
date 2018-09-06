require 'adminware/commands/run'

RSpec.describe Adminware::Commands::Run do
  it "executes `run` command successfully" do
    output = StringIO.new
    tool = nil
    options = {}
    command = Adminware::Commands::Run.new(tool, options)

    command.execute(output: output)

    expect(output.string).to eq("OK\n")
  end
end
