# Alces Adminware

A set of tools to improve the ease of use for running and scheduling jobs on nodes

## Prerequisites

The install scripts handle the installation of all required packages and will install on a minimal base.

## Installation

### TLDR

One line installation - 

```bash
curl https://git.io/adminware-installer | /bin/bash
```

### Basic Installation

Adminware is a system-lvel package and must be installed by the `root` user.

1. Make yourself root
  
  ```bash
  sudo -s
  ```
2. Invoke installation by piping the output from `curl` to `bash`

  ```bash
  curl https://git.io/adminware-installer | /bin/bash
  ```

  Alternatively you can download the script so you can inspect what it will do before installing

  ```bash
  curl https://git.io/adminware-installer > /tmp/install.sh
  less /tmp/install.sh
  bash /tmp/install.sh
  ```
3. After it has installed you can either relog to set the shell configuration correctly or you can source the shell configuration manually

  ```bash
  source /etc/profile.d/alces-adminware.sh
  ```
## Usage

Once Adminware is installed and the shell configuration is set you can access the Adminware tools via the `adminware` command e.g.

```
[root@localhost ~]# adminware --help

  NAME:

   adminware

  DESCRIPTION:

    adminware

  COMMANDS:

    help           Display global or [command] help documentation
    job-list       Lists all available jobs for a host
    job-run        Run a script locally or on another machine via SSH
    schedule-add   Schedule a job for a host
    schedule-apply Apply the schedule for a host
    schedule-clear Clear the schedule for a host
    schedule-list  List the schedule for a host
    state-list     List the state values for all run jobs

  GLOBAL OPTIONS:

    -h, --help
        Display help documentation

    --version
        Display version information

    --trace
        Display backtrace when an error occurs
```

You can find more detailed help for each command by using this command structure `adminware COMMAND --help` e.g.

```
[root@localhost ~]# adminware job-list --help

  NAME:

    job-list

  SYNOPSIS:

    adminware job-list [options]

  DESCRIPTION:

    Lists all available jobs for a host

  EXAMPLES:

    # List all jobs for a host
    adminware job-list --host HOST

  OPTIONS:

    -p, --plain
        Output in a tab delimited format

    -H, --host HOST
        Specify the host you wish to view the jobs for
```

## Copyright and Licenses

GNU Affero General Public License v3.0, see [LICENSE.txt](LICENSE.txt) for details

