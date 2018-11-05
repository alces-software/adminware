
# Getting Started
`adminware` must be installed within `/opt` using:
```
cd /opt
git clone https://github.com/alces-software/adminware.git
cd adminware
make setup
```

# Commands' Structure
The command line interface of Adminware is laid out as follows:

exit - exits the CLI.

help - displays help for the current level's commands.

run - command group used for running tools - works in parallel across nodes.
 - run tool NODE(S) [NAMESPACE(S)] TOOL [ARGUMENTS]
    - Runs tool TOOL on NODE(S).
    - A tool's namespaces must be specified before its name.
    - If a tool is selected for a single node it will be automatically ran
      in interactive mode.
    - If a tool marked as being interactive only (see 'Adding Tools') and it is 
      attempted to run it on more than one node it will cancel and an error will
      be thrown.
    - Optionally, arguments can be provided.
 - run family NODE(S) FAMILY
    - Runs family FAMILY on NODE(S).

view - inspect execution history, statuses, groups, and tools.
 - view groups
    - Lists every group set-up in the system's genders file
 - view group GROUP
    - Lists all the nodes in group GROUP
 - view tool [NAMESPACE(S)] [TOOL]
    - Shows info about the tool at NAMESPACE(S)/TOOL
    - Displays the tool's name, description, command, families, whether it must
      be ran interactively and the contents of its working directory
    - If no tool is given, the command's help display it lists the availible tools
      and sub-namespaces the given namespace(s).
    - If NAMESPACE(S) is not given, it lists at the highest level `tools` directory.
 - view family [FAMILY]
    - Displays the members of the tool family FAMILY, as well as their order of
      execution
    - If FAMILY is not given, it lists all the system's tool families.
 - view result JOB-ID
    - Shows the result (exit code, stdout, stderr) of an instance of a single
      tool running on a single node.
 - view node-status NODE
    - Shows the last execution of each tool on NODE.
    - Includes the date, exit code, job ID, arguments used and the total number
      of times ran.
 - view tool-status TOOL
    - Shows the last execution of TOOL on each node TOOL has been run on.
    - Includes the date, exit code, job ID, arguments used and the total number
      of times ran.
 - view node-history NODE
    - Shows all past executions of all tools on the given node.
    - Displays the tool, the job ID, exit code, arguments and date.
 - view tool-history TOOL
    - Shows all past executions of the given tool across all nodes.
    - Displays the tool, the job ID, exit code, arguments and date.

# Error Codes

The exit code for the remote command is saved within the database. The meaning
of the exit code is determined by the underlying command and will range from
0-255.

All negative exit codes indicate an internal `Adminware` error. The exit codes
and their meanings are as follows:

| Error Code | Description             |
| ---------- | ----------------------- |
| -1         | SSH Connection Error    |
| -2         | General Error           |
| -3         | Interactive Job         |
| -4         | Abandoned Job Error     |

## -1: SSH Connection Error
An initial SSH connection could not be established with the node.

NOTE: This error code will only be issued for handled errors. It is still
possible for unhandled SSH errors to be issued a different error code.

## -2: General Error
An error has occurred that concerns the job. See the jobs `STDERR` for more
details.

## -3: Interactive Job
The tool has been ran in an interactive shell. The `STDOUT`, `STDERR`, and
exit code are not available. This does not mean the job failed, instead its
status is undetermined.

## -4: Abandoned Job Error
The job has been created and queued to be ran but has since been abandoned.
This indicates the job was never ran, but this can not been known for
certain.

Possible Causes:
1. `Adminware` was sent an interrupt,
2. An uncaught SSH connection error has occurred,
3. The connection was lost to the `adminware` appliance, or
4. An unexpected error occurred before the job was started.

# Adding Tools
Tools can be ran interactively and non-interactively; a tool will automatically
be ran interactively if selected with a single node. Interactive mode establishes
an interactive shell session, this allows for full screen applications
(e.g. `vi`, `top`, `bash`). Interactive mode does not save anything to the database.
Non-interactive mode allows for multiple tools to be ran over mutliple nodes with
single line output. The full results are logged to the database.

Tools are automatically picked up from config files stored at:

`/var/lib/adminware/tools/[<optional-namespace>/].../<command-name>/config.yaml`

The config.yaml files cannot have directories as their siblings, although
there can be other files in the same directories.

The config files should follow the following format:
```
# Could be system command like `uptime` or tool dir command like
# `./script.rb`.
command: command_to_run

# Full help text for this tool, it will be picked up and displayed in full when `help` is
# displayed for this tool, or the first line will be displayed when `help` is displayed for
# its corresponding parent commands (see http://click.pocoo.org/5/documentation/#help-texts)
help: command_help

# A list of any families that the tool is in. A family is a group of tools that
# can be executed with a single statement using `run family`. Tools within a
# family are executed in alphanumeric order and each tool is executed on every node
# before the second tool is executed on any.
families:
 - family1
 - family2
 - etc..

# A flag stating that this tool's command should never be ran in a non-interactive
# shell. It's value must be "True" for this to take effect. If a tool is marked as
# interactive only it will be excluded from tool families and from being run on more
# than one node at once. If it is attempted to run in on more than one node an error
# will be thrown.
interactive: True
```

# Development setup

It is recommended that Adminware is developed locally (so you have all your
local development tools available) and synced, run, and tested in a clean
remote environment (to be in an environment close to what it will normally use
in production, and to avoid polluting or depending on things in your local
environment).

You can try adapting this setup, but this is what I'm doing (which works):

1. Have remote CentOS/RedHat EL7 machine available to sync and develop on, with
   `root` access available - I have:
  ```bash
  [root@bob adminware]# uname -a
  Linux bob 3.10.0-862.11.6.el7.x86_64 #1 SMP Tue Aug 14 21:49:04 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux
  ```

2. Then locally:
  ```bash
  make rsync PASSWORD="password for machine" IP="ip of machine"
  ```

3. Remotely:
  ```bash
  cd /tmp/adminware
  make development-setup
  ```

# Development process

- To keep remote machine as setup above constantly in sync with local changes
  (leave this running):
  ```bash
  gem install rerun # If you don't have this already.
  make watch-rsync PASSWORD="password for machine" IP="ip of machine"
  ```

- To run synced, development `admin` CLI remotely:
  ```bash
  cd /tmp/adminware
  bin/starter [ADMIN_COMMANDS_AND_ARGS]
  ```

- To run tests remotely:
  ```bash
  make unit-test
  ```
