conda-offline-channel
******************************************************************

A conda subcommand to build an offline channel which contains all requirements.


Requirements
==================================================================

- conda
- conda-build


Usage
==================================================================
::

  # Build an offline channel for 'django' in 'channel' directory
  conda offline-channel django

  # Build an offline channel for 'numpy' and 'matplotlib' in 'offline_channel' directory
  conda offline-channel numpy matplotlib --root-dir offline_channel
