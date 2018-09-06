RSpec.describe "`adminware run` command", type: :cli do
  it "executes `adminware help run` command successfully" do
    output = `adminware help run`
    expected_output = <<-OUT
Usage:
  adminware run TOOL...

Options:
  -h, [--help], [--no-help]  # Display usage information

Command description...
    OUT

    expect(output).to eq(expected_output)
  end
end
