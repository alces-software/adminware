RSpec.describe "`admin run` command", type: :cli do
  it "executes `admin help run` command successfully" do
    output = `admin help run`
    expected_output = <<-OUT
Usage:
  admin run TOOL...

Options:
  -h, [--help], [--no-help]  # Display usage information

Command description...
    OUT

    expect(output).to eq(expected_output)
  end
end
