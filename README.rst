Report Compiler HPV Information Centre generator tools
######################################################

|docs|

The Report Compiler HPV Information Centre generator tools provide methods to easily take advantage 
of the data fetched by the Report Compiler IC Fetcher in a context generation module using python. 
This includes an easier way to generate latex tables and figures with the appropriate annotations
(global, column, row and cell references).

This project is being developed by the ICO/IARC Information Centre on HPV and Cancer 
and will be used in our report generation tasks.

.. image:: HPV_infocentre.png
   :height: 50px
   :align: center
   :target: http://www.hpvcentre.net

.. |docs| image:: https://readthedocs.org/projects/reportcompiler-ic-tools-python/badge/?version=stable
    :alt: Documentation Status
    :scale: 100%
    :target: https://reportcompiler-ic-tools-python.readthedocs.io/en/stable/?badge=stable

Features
============

* Helper functions to effectively use the references returned by the Information Centre data fetcher.
* Create latex tables and figures with the appropriate annotations for global, row, column and cell references.
* Structured output so tables can be tuned for custom requirements.

Installation
============

Dependencies
------------

For linux the installation process should automatically pull all required dependencies via pip. In windows systems, some packages require
manual installation:

* Visual Studio Build Tools: http://landinghub.visualstudio.com/visual-cpp-build-tools
* Shapely: https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely
* Fiona: https://www.lfd.uci.edu/~gohlke/pythonlibs/#fiona

Package
-------

.. code:: bash

 git clone https://github.com/hpv-information-centre/reportcompiler-ic-tools
 cd reportcompiler-ic-tools/scripts
 ./install_package.sh


Documentation
-------------

To generate HTML documentation:

.. code:: bash

 scripts/compile_docs.sh

This project uses Sphinx for documentation, so for other formats please use 'make' with the 
appropriate parameters on the doc directory.


Git hooks setup
---------------

.. code:: bash

 scripts/prepare_hooks.sh