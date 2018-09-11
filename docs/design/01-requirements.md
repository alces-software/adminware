
# Core requirements

1. Adminware should be runnable both as a stand-alone command and in a
   'sandbox' REPL mode, similar to `controller`, `monitor`, and
   `directory`/`userware` CLIs.

2. Adminware needs to allows you to run various tools on singular or multiple
   nodes (depends on the tool type, see below), and which nodes a tool is run on
   should always be configurable by the user at run-time.

3. Tools may be recursively namespaced to group similar ones together to avoid
   overwhelming the user and make things more discoverable, e.g. `admin run
   modify motd`/`admin run modify slurm.conf` or `admin run my special
   namespace tool5` (though exact syntax for running a tool may be different,
   see below).

4. The available tools should be entirely configurable, i.e. none are
   hard-coded into Adminware, even if we may often ultimately pull many of them
   from the same sources for many customers.

5. Adminware should initially pick up these tools from a single directory
   hierarchy on the machine running Adminware.

6. The tools Adminware allows you to run may be entirely custom scripts,
   standard system packages, as well as some combination of these such as
   wrappers around system tools to lock down access or give a nicer UI.

7. Adminware should sync across everything needed to run each tool to the node
   it is to be run on at the point it is to run, to ensure the latest version
   of all required files are present.

8. For now, Adminware should have no special handling about which user it
   should run all, or individual, tools as - every tool should be run as the
   user Adminware is run as (which will likely initially be `root`). Later this
   may become configurable in some way on a global or individual tool basis.

9. Initially we want to support 3 types of tools:

    a. 'exit code scripts' - which I will call a `job`
      - call `batch` now, and combined with `batch` below (see question below)
      - run across many nodes and make a change
      - report which nodes the change worked for, possibly in a similar way to
        `batch` tools (see below)
      - also record this information long-term (unlike other types of tools), so
        this can later be retrieved and inspected
        - want to be able to see:
          - history of all `job`s run, possibly filtered by `job` or node
          - current status of individual (or many?) nodes, e.g. jobs which have
            been run on each and whether these last succeeded
          - output from individual past jobs

      - @question: do we want to allow specifying these as not rerunnable, i.e.
        cannot be run again after having succeeded (not sure if a core
        requirement)? If we do need this, may want to also allow specifying a
        `reverse` command to undo the change, so can then rerun the original
        command if needed.
	  - `rerunnable`/`reverse` not required initially

      - @question: should the nodes this is run across be able to be limited to
        those of a particular type, e.g. a tool can specify that it is only for
        `compute` nodes and then cannot be run on a `login` node?
        - not required initially

    b. 'batch/report scripts' - which I will call a `batch` tool (as this is more
    general, e.g. `pkill` across many nodes isn't really a report and changes the
    state of the cluster)
      - following is mostly relevant for reference of the kinds of use cases
        we'll have for some tool types, but 'batch' and 'job' tool types are
        now being combined (see question below)

      - run across many nodes
      - should give you informative output which makes it easy to tell at a
        glance which nodes the command succeeded/failed on, what exit code each
        had
      - would be useful to have the ability to drill down and see full `stdout`
        and/or `stderr` output for an individual node
        - possible ways this could be done:
          - temporarily save all output for a `batch` command, and until another
            one is run allow additional commands to be run to investigate this
            output
          - have a TUI mode entered when a `batch` is run, maybe using something
            like https://github.com/pfalcon/picotui, which allows the user to
            page through the batch output in a table-like interface, but then
            drill-down and back up to inspect the output of individual commands

      - @question: Is it actually key to have `job` vs `batch` distinction? They
        seem similar, and combining them would make implementation simpler.
        Saving all output for `batch` tools would not necessarily be bad; would
        allow us to inspect what people have done later to e.g. tell them that a
        process died on a node because they ran a `pkill` across all nodes which
        killed it.
        - not key distinction initially

    c. 'interactive scripts' - which I will call `interactive`
      - run interactively on any single node, including potentially the machine
        Adminware is running on
      - take over the terminal and let the user interact fully with the tool
        being run, then hand back control to Adminware when they exit

      - call `open` now

10. Adminware should allow arguments to be passed to tools, e.g. a pattern to
    be `pkill`ed (across many nodes) would need to be passed to a `pkill` batch
    tool. Ideally feedback on what arguments/options are available/required for
    each tool would be given.

11. It should be possible for users to easily discover what tools of each type
    are available, so they can run them.

# Incoming but not initial requirements

1. It should be possible for site admins to specify their own node groupings
   and then use these when running commands.

   @question: should groups/other custom groupings be able to be included in a
   custom grouping (so e.g. adding a node to a group at one level could cascade
   to other levels depending on this)?
     - nope, not initially

   @question: do we need some support for specifying that a group should have
   some commands run on it (e.g. the custom grouping `slurm_nodes` should have
   the `enable-slurm` job run on it, and this will be in particular indicated
   to the user in some way)? Either way possibly simpler to get other things
   implemented before considering this in detail.

     - not important for now

@question: any core/additional requirements not covered?
- make sure getting list of nodes in group isn't tightly coupled to looking in
  genders file - do in just one place etc. - so can swap out later

@question: Do we need to have commands in Adminware for displaying available
nodes/groups, so users can target these? Since, in particular in `sandbox`
mode, they won't necessarily be able to know what's available. How will we know
what nodes are available?
- yes, `group list` (don't show all nodes in groups), `group show` (show nodes
  in group)
  - come from genders but don't tell anyone this in case we want to change it

# Implementation

For brevity I'm mostly going to cover what I think is the best approach here,
and not all the options in each case that I considered and discounted; I can
expand on each decision if requested though.


## Technology

Given the requirement for there to be a `sandbox` mode available for the CLI,
and that it would be preferable for this to be consistent with our other
appliance CLIs with sandbox modes, it would seem best to use Python and
[Click](http://click.pocoo.org/6/), with
[click-repl](https://github.com/click-contrib/click-repl), for this CLI as well.


## CLI organisation

The following would seem the best structure to cover the current requirements
and be flexible to future requirements (this is also another reason to favour
Python/Click for implementation, as it makes this sort of very nested and
dynamic structure much simpler than any Ruby CLI library I've used):

- `admin`
  - `batch`
    - `run [--node|--group] [NAMESPACES...] TOOL [TOOL_ARGS]` - example jobs,
      will all be dynamic in reality:
      - `TOOL_ARGS` should just be passed straight through to tool command, no
        need for any validation around these initially

      - `enable-slurm`

      - `disable-slurm` (later this could be a `--reverse` of previous job, but
        making this possible is not a key requirement initially I believe)

      - `change-request` (namespace)
        - `bar123 FOO [--baz]` (args/options to be accepted at Adminware
          level and passed through to underlying tool)

    - `history [--node|--group|--job-id|possibly other things in future]`
      - gives pageable output with time-ordered table of all past jobs and
        nodes run on
      - row of table displayed for every JOB_ID and NODE combination, i.e.
        running a batch command across a group of 20 nodes will cause 20 new
        rows to appear in the table, with same JOB_ID and different NODE for
        each

      - columns of table:
        - full command run, e.g. `batch run --group mynodes pkill myjob` (will
          be same for each node job affects)
        - date and time
        - exit code
        - `job_id` (saved and incremented for each job run, allows us to later
          refer to this, used in `admin batch view` etc.)
        - node name
        each line has same columns as for `status` except that
        rows are shown time-ordered for every job run, rather than only for
        last run of particular job on particular node.
      - combine `status` and `history` (call it `history`), build up query to
        be run from args
      - user running command (not required for MVP, probably not available
        initially)

      - options allow table rows shown to be filtered, will probably be used to
        construct underlying query for table rows (unless we need to do the
        filtering in Python rather than SQL for some reason, but that's an
        implementation detail). E.g.:
        - `admin job history --node node05` - gives table of all batch jobs
          recorded for `node05`
        - `admin job history --job-id 4` - gives table with rows for all nodes
          effected by batch job with ID 4
        - `admin job history --group mynodes --job-id 3` - gives table with
          rows for all nodes in group mynodes effected by batch job with ID 3

    - `view JOB_ID NODE` - display output for job with given `job_id` on given
      node. Could display `stdout` and `stdout` intermingled, with `stderr` a
      different colour like red, possibly with exit code displayed at end in
      another colour (to indicate not output); and/or could have options to
      only show some of these.
      - not too bothered about how output is, whether `stdout`/`stderr` in one
        command, whether SSH will actually give useful `stderr` etc.

    - @question: are these commands for viewing job output all necessary and
      sufficient for use cases we want to cover?
      - yes, probably, for now

  - `open --node NODE [NAMESPACES...] TOOL [TOOL_ARGS]`

  - `group`
    - `list` - list all groups from genders file; do not show nodes in groups
    - `show GROUP` - list nodes in given group
    - groups come from genders file for now but don't tell anyone this in case
      we later want to change the implementation

For each command there will also be help available via the `--help` option
(automatically provided by Click). To be consistent with other appliance CLIs
(and many other Alces tools) the `help` command, allowing help to be accessed
like `alces help job run change-request bar123`, can also be implemented (see
https://github.com/alces-software/userware/blob/54144eb828c5940a839f9d20a495c2668747a3b1/share/appliance_cli/src/help.py).

Using help will also provide us with a logical place to provide info on the
available tools at each level, and full details on each tool, e.g.:

- `admin help batch run change-request` - will list all available jobs within the
  `change-request` job namespace, along with their short help (from each of
  their `config.yaml`s; see below)

- `admin help batch run pkill` - will give full help, available options etc.
  for `pkill` batch tool.

Later we could also provide command to give full tree of available namespaces
and tools for different tool types, to make an overview of everything possible;
initially this does not seem required though.

@question: What options for targeting nodes do we need for MVP - initially I
think `--node`, `--group`, `--all`, `--local`  should be sufficient (`--node`
and `--group` can be provided any number of times and are cumulative). Later as
needed we can add `--collection` (see below), `--exclude-*` options etc.
- just `--node` and `--group` - cumulative-ness not needed for MVP, though
  nice-to-have if simple


## Tool directory hierarchy

All tool configurations will initially be located under
`/var/lib/adminware/tools/`. Within this there will be three directories for
the three initial types of tools: `job`, `batch`, and `interactive`.

Within each of these, arbitrary numbers of directories (each representing a
namespace at this level) may be nested until ultimately a directory containing
a `config.yaml` file is present; this directory, and any child directories of
it, then specifies the full configuration and any other necessary files for a
particular tool. The only required file within this directory is `config.yaml`
(which is also what specifies that this directory will be picked up by
Adminware at all). The `config.yaml` file gives all needed configuration for
each tool; any other files within the directory can then be referenced by this
(or files referenced by these etc.).

## `config.yaml` format

```yaml
# Could be system command like `uptime` or tool dir command like
# `./script.rb`.
command: command_to_run

# Full help text for command, will be picked up and displayed in full when
# `help` displayed for command, or first line displayed when `help` displayed for
# parent command (see http://click.pocoo.org/5/documentation/#help-texts).
help: command_help


# 'job'-only, optional, and not sure if required for MVP (or at all):

# Whether command can be rerun for a node after having already been
# successfully run (default true).
rerunnable: true | false

# To be run to undo main command so can be redone, mostly useful when
# `rerunnable: false`.
reverse: reverse_command_to_run

# Array of gender groups this job is able to be run on; attempting to run it on
# nodes not in any of these groups will fail.
allowed_groups: [group1, group2]
```

@question: How important are the `rerunnable`, `reverse`, `allowed_groups`
options for jobs
- for MVP?
- at all?
- not important for now

@question: Anything you think should be configurable which isn't covered?
- add `published:` flag to config, default false, have to explicitly set to
  true for tool to be published
  - things which aren't published don't show up when in `sandbox`
  - when not in `sandbox`, things which aren't published give warning `WARNING:
    This tool is not published`.

## Running tools

Apart from when running tools on the `local` node (i.e. node Adminware is
installed/running on), Adminware will need to be able to run tools on other
nodes within the cluster. Since password-less SSH access should be available
from the Adminware machine to all cluster nodes, it would make sense to use
this for running jobs across nodes, and it would make sense to use a library
for this rather than shell-ing out;
[Paramiko](https://github.com/paramiko/paramiko/) seems a good choice in Python
for this.

Tools will also need to sync across all files they depend on to ensure these
are present before running the tool. One consideration with this is that
dependencies for a tool may not be available, e.g. if we want to write a script
in Ruby we may not be able to depend on this being installed on any node, or we
may not be able to depend on a particular RPM having been installed.

The simplest way to handle this, which should (at least initially) be
sufficient, is not to do anything special for the new Adminware: e.g. if we
want to write a tool in Ruby we can either write it with the entry point a
Shell script wrapper which checks all necessary dependencies, including Ruby,
are installed, and installs them if not, or we can write it assuming Ruby will
be available everywhere it is to be run if we know this is the case in the
current environment. Later if needed we could consider adding some kind of
dependency specification to Adminware, e.g. the RPMs or Forge/Gridware packages
which should be installed before the tool itself is run.

Putting this together, the rough initial algorithm for running a (`job` or
`batch`) tool across some number of nodes will be as follows, using `admin job
run --node node01 --node node04 --group foonodes change-request bar123` as an
example command:

- resolve the targeted node names, group names etc., by combining the passed
  arguments for these together and expanding gender groups, e.g.  `--node
  node01 --node node04 --group foonodes` -> `['node01', 'node04', 'foonode01',
  'foonode02', 'foonode03']`;
  - if resolving gender group fails, abort command and output error (since this
    is a pretty major issue and could be surprising if we carried on but with
    one group missing; user can then just correct/remove the group which
    doesn't exist)

- for each targeted node name (initially sequentially, later this could be
  parallelized):
  - SSH to node and create temporary directory
    - if this, or sync below, fails e.g. as node name doesn't resolve, it
      should be displayed as an error in final output, but should not stop
      things
  - sync across all files to the temporary directory (with `scp`?) - possibly
    `tar` and `gzip` first, or maybe this doesn't matter
  - in existing SSH connection, run command and capture stdout, stderr, and
    exit status
    - possibly worth adding a timeout when running the command; this should
      probably be low-ish

- appropriately display and/or save the collected details of running the tool
  across all targeted nodes

The algorithm for running an `interactive` tool will be similar, except exactly
one node may be targeted, and the connection will be left open for the user to
use in the interactive session on the targeted node, before control is passed
back to Adminware.

Later this process can be incrementally improved to provide in-progress
feedback on how many nodes a command has been run on, success/failure of each
etc.


## Collections

In order to support user groupings we will have the concept of 'collections'.
Unless requested (above) these will not initially be required, but worth
considering how they will be added at some point.

Nodes, and possibly groups and other collections, will be able to be added to
collections. Collections will then be able to be used when targeting nodes for
running tools, e.g. `admin job run --collection slurm_nodes enable-slurm`.

Possible commands for manipulating these:
- `admin collection create COLLECTION_NAME`
- `admin collection delete COLLECTION_NAME`
- `admin collection add NODE_NAME COLLECTION_NAME`
- `admin collection remove NODE_NAME COLLECTION_NAME`
- `admin collection list` - table of all collections and nodes within

- maybe needed, depending on whether we need to support adding groups/other
  collections to collections:
  - `admin collection add-group GROUP_NAME COLLECTION_NAME`
  - `admin collection remove-group GROUP_NAME COLLECTION_NAME`
  - `admin collection add-collection COLLECTION_TO_ADD_NAME COLLECTION_NAME`
  - `admin collection remove-collection COLLECTION_TO_ADD_NAME COLLECTION_NAME`
  - `admin collection view COLLECTION_NAME` - show collection, the direct
    members of this (nodes/groups/collections), and the expanded list of all
    nodes which will be targeted when this is used (this may be useful
    generally if `collection list` ends up giving very verbose output in
    practise, in which case a `--expand` option may be useful instead to give
    the expanded output)

@question: does this cover the initial use cases we want to support for user
groupings?
- maybe, not important for now

@question: importance of collection support?
- not important
