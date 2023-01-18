.. py:currentmodule:: configurator

Installation
============

Configurator is available on the `Python Package Index`__ and can be installed
with any tools for managing Python environments. The package has no hard
dependencies beyond the standard library, but you will need extra libraries for most
file formats from which you may want to read configuration information. As a result,
you may wish to install Configurator with the appropriate extra requirement to meet
your needs:

__ https://pypi.org

.. code-block:: bash

  pip install configurator[toml]
  pip install configurator[yaml]

Configurator is also available as a conda package installable from `conda-forge`__:

__ https://anaconda.org/conda-forge/configurator

.. code-block:: bash

  conda install -c conda-forge configurator

.. note::

  Conda does not support the notion of "optional extras" so you will need to manually
  install the package(s) required to parse the config file formats you need.

