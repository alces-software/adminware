
# Getting Started
`adminware` must be installed within `/opt` using:
```
cd /opt
git clone https://github.com/alces-software/adminware.git
cd adminware
make setup
```

# Error Codes

The exit code for the remote command is saved within the database. The meaning
of the exit code is determined by the underlining command and will range from
0-255.

All negative exit codes indicate an internal `Adminware` error. The exit code
meanings are as follows:

| Error Code | Description             |
| ---------- | ----------------------- |
| -1         | SSH Connection Error    |
| -2         | General Error           |
| -3         | Interactive Job         |
| -4         | Abandoned Job Error     |

## -1: SSH Connection Error
An initial ssh connection could not be established with the node.

NOTE: This error code will only be issued for handled errors. It is still
possible for unhandled ssh errors to be issued a different error code.

## -2: General Error
An error has occurred that concerns the job. See the jobs `STDERR` for more
details.

## -3: Interactive Job
The tool has been ran in an interactive shell. The `STDOUT`, `STDERR`, and
exit code are not available. This does not mean the Job failed, instead its
status is undetermined.

## -4: Abandoned Job Error
The job has been created and queue to be ran but has since been abandoned.
This indicates the `Job` was never ran, but this can not been known for
certain.

Possible Causes:
1. `Adminware` was sent an interrupt,
2. An uncaught SSH connection error has occurred,
3. The connection was lost to the `adminware` appliance, or
4. An unexpected error occurred before the `Job` was started.

# Adding Commands
Commands can be added to `batch run` and `open` features. `batch` runs the 
command over a single or group of nodes and stores results in a database.
`open` establishes and interactive session with a single node.  This allows
for full screen applications (e.g. `vi`, `top`, `bash`). `open` does not
save the anything to the database.

Commands are automatically picked up from config files stored within:

`/var/lib/adminware/tools/{batch,open}/[<optional-namespace>/].../<command-name>/config.yaml`

The config.yaml files cannot have directories as their siblings, although
there can be other files in the same directories.

The config files should follow the following format:
```
# Could be system command like `uptime` or tool dir command like
# `./script.rb`.
command: command_to_run

# Full help text for command, will be picked up and displayed in full when
# `help` displayed for command, or first line displayed when `help` displayed for
# parent command (see http://click.pocoo.org/5/documentation/#help-texts).
help: command_help

# A list of any families that the command is in. A family is a group of commands that
# can be executed with a single statement using `batch run-family`. Commands within a
# family are executed in alphabetical order and each command is executed on every node
# before the second command is executed on any.
# This field is optional and only valid for batch commands.
families:
 - family1
 - family2
 - etc..
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
