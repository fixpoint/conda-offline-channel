conda-offline-channel
******************************************************************
.. image:: https://anaconda.org/lambdalisue/conda-offline-channel/badges/version.svg
    :alt: Version

.. image:: https://anaconda.org/lambdalisue/conda-offline-channel/badges/license.svg
    :alt: MIT License

.. image:: https://anaconda.org/lambdalisue/conda-offline-channel/badges/downloads.svg
    :alt: Downloads

.. image:: https://anaconda.org/lambdalisue/conda-offline-channel/badges/installer/conda.svg
    :target: https://conda.anaconda.org/lambdalisue
    :alt: Install with

A conda subcommand to build an offline channel which contains all requirements.

.. note::

    I'm planning to add this feature into an official conda-bld repository.
    See https://github.com/conda/conda-build/issues/2387 for more detail.


Requirements
==================================================================

- conda
- conda-build


Install
==================================================================
::

  conda install -c lambdalisue conda-offline-channel 


Usage
==================================================================
::

  # Build an offline channel for 'django' in 'channel' directory
  conda offline-channel django

  # Build an offline channel for 'numpy' and 'matplotlib' in 'offline_channel' directory
  conda offline-channel numpy matplotlib --root-dir offline_channel
