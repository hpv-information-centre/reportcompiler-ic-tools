.. _`tables`: 

Table generation
================

Using the regular `Report Compiler`_ library, a data fetcher usually returns (a collection of) dataframes to be processed. With the addition of the `Report Compiler IC Fetcher`_, these dataframes are returned with additional information relevant to our data: sources, notes, methods, years of estimates and dates. Furthermore, these references can be applied globally, in a row, in a column or in a cell. This utility library provides the ``generate_table_data`` function to assist in all this formatting to a document table.

This function accepts five parameters:

* **data_dict**: The data dictionary as returned by the `Report Compiler IC Fetcher`_ (mandatory). In case the source dataframe needs to be built manually (e.g. for customized tables) and the references are not necessary, the utils module includes a ``wrap_empty_references`` as a convenience shortcut to obtain this dictionary. For more information on the structure of this dictionary please check its documentation.
* **selected_columns**: Column names from ``data_dict['data']`` that will be shown in the output table. By default all columns will be shown but in the case of ID columns, even if it is necessary their presence to index possible references, it is probably not desirable to show them.
* **column_names**: Display names of the columns as will be shown in the document table header. Its length must be equal to the *selected_columns* parameter's length.
* **row_id_column**: Column that will be used as the representative of the row for referencing purposes. This column will contain the reference markers associated with that row. For example, a table about different study indicators might have the name of the study as the *row_id_column*. By default the first column is chosen.
* **format**: Format of the output table. This is necessary mostly for the syntax that will be used when attaching markers to the table values. By default the format is 'latex' (the only one currently implemented).

It returns a dictionary with four items:

* **table**: A dataframe with the content of the table with the reference markers embedded. Each cell of the dataframe is a dictionary with two values:

   * **value**: The original value of the cell; e.g. "Spain".
   * **markers**: A list with the markers that should be displayed in that cell; e.g. ['a', 'b', '1'].
   * **color**: (Optional) The fill color of that cell; e.g. '#ff0000'.

* **columns**: A list of the column names that should go into the table header, along with the associated reference markers. Each item is a dictionary with two values:

   * **name**: Name of the column to be displayed; e.g. "Country".
   * **markers** A list with the markers that should be displayed in that column header; e.g. ['a', 'b'].
  
  Example:

  .. code-block:: javascript

    [
        { "name": "Country", "markers": ["a"] },
        { "name": "Study", "markers": ["1", "\\alpha"] },
        { "name": "Prevalence", "markers": [] }
    ]

* **footer**: A dictionary with the reference list that should be displayed as the table footer. The dictionary has four keys, one for each reference type: ``sources``, ``notes``, ``methods`` and ``years``. Each one of these is a list of two-key dictionaries:

   * **marker**: Marker associated to that reference; e.g. "1".
   * **text**: Text of the reference; e.g. "de Martel C et al. Lancet Oncol 2012;13(6):607-1"

  Example:

  .. code-block:: javascript

    {
        "sources": [
            { "marker": "1", "text": "First example source" },
            { "marker": "2", "text": "Second example source" }
        ],
        "notes": [
            { "marker": "a", "text": "First example note" }
        ],
        "methods": [
            { "marker": "\\alpha", "text": "First example method" }
        ],
        "years": [
        ]
    }

* **markers**: The reference marker generators for each of the types (sources, notes, methods, years). This allows the user to generate new markers following those already set by the IC data fetcher.

  Example:

  .. code-block:: python

    table_info = generate_table_data(data_dict)
    # Note a, b returned by the function
    new_note_marker = next(table_info['markers']['sources'])
    # new_note_markers = 'c'
    # Add new note with the marker...

This structured data returned by the function allows the user to customize and add any last touches on the data visualization (e.g. add coloured cells, merge headers into multicolumn cells, restructure the table layout, ...). Once ready, this structure can be passsed onto the template renderer and displayed according to the template.

To generalize and reuse table layouts, common templates are included in this library too. They can be used by the report compiler library setting the ``RC_TEMPLATE_LIBRARY_PATH`` to this project's ``templates`` path.

.. _Report Compiler: https://github.com/hpv-information-centre/reportcompiler
.. _Report Compiler IC Fetcher: https://github.com/hpv-information-centre/reportcompiler-ic-fetcher