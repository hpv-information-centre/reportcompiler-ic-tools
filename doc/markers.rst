.. _`markers`: 

Markers
=======

When using the :ref:`tables` functionality, each reference type (sources, notes, methods and years) needs to be differentiated from the rest. That is why each type has a different set of marker types, specifically:

* **Sources**: Numbers from 1 to 50 (e.g. 1, 2, ..., 50).
* **Notes**: The set of lowercase letters followed by the set of uppercase letters (e.g. a, b, ..., z, A, B, ..., Z).
* **Methods**: :math:`{\alpha}`, :math:`{\beta}`, :math:`{\gamma}`, :math:`{\delta}`, :math:`{\epsilon}`, :math:`{\zeta}`, :math:`{\eta}`, :math:`{\theta}`, :math:`{\iota}`, :math:`{\kappa}`, :math:`{\lambda}`, :math:`{\mu}`, :math:`{\nu}`, :math:`{\omicron}`, :math:`{\pi}`, :math:`{\rho}`, :math:`{\sigma}`, :math:`{\tau}`, :math:`{\upsilon}`, :math:`{\phi}`, :math:`{\chi}`, :math:`{\psi}`, :math:`{\omega}`, :math:`{\Gamma}`, :math:`{\Delta}`, :math:`{\Theta}`, :math:`{\Lambda}`, :math:`{\Pi}`, :math:`{\Sigma}`, :math:`{\Upsilon}`, :math:`{\Phi}`, :math:`{\Psi}`, :math:`{\Omega'}`
* **Years**: :math:`{\Diamond}`, :math:`{\triangle}`, :math:`{\nabla}`, :math:`{\S}`, :math:`{\bigstar}`, :math:`{\aleph}`, :math:`{\infty}`, :math:`{\Join}`, :math:`{\natural}`, :math:`{\mho}`, :math:`{\emptyset}`, :math:`{\partial}`, :math:`{\$}`, :math:`{\triangleright}`, :math:`{\triangleleft}`, :math:`{\bullet}`, :math:`{\star}`, :math:`{\dagger}`, :math:`{\ddagger}`, :math:`{\oplus}`, :math:`{\ominus}`, :math:`{\otimes}`, :math:`{\Box}`

Their number are deliberately limited to detect possible errors or document artifacts too large to reasonably display. In case more markers are needed, the functions in ``markers.py`` (``source_markers``, ``note_markers``, ``method_markers`` and ``year_markers``) can be overridden by a function with no arguments that returns an iterable of the custom markers.


.. code-block:: python

  from reportcompiler_ic_tools import tables
  
  df = ...

  tables.source_markers = lambda: range(1,1001)
  table, columns, footer = tables.generate_table_data(df)  # This table will support up to 1000 sources
  
