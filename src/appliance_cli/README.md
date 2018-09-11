
This directory contains code which should be shared between all appliance CLIs,
but no longer is due to CLIs now existing in different repos. Other, similar,
but possibly slightly tweaked versions of this code also exist at
https://github.com/alces-software/imageware/tree/67d1c814335486f5643aeb359ab98d7c9bdade4a/share/appliance_cli/src
and
https://github.com/alces-software/userware/tree/d8a6fc96a90ea70cc6dc4ed8a1500ced7ff3c226/share/appliance_cli/src.

Avoid updating things in here which can be done in the main Adminware codebase
instead, and if we do find we often need to update things within this shared
code it's probably worth extracting a shared library for this instead.
