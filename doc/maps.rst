.. _`maps`: 

Map generation
==============

This library provides a utility function to generate a map suitable for the HPV Information Centre purposes using the plotnine_ library. The idea is to provide the basic blueprint of a map plot while at the same time being able to refine it further with the ggplot-like functions applied to the plot object. 

These map plots are generated from a dataframe with country identifiers and are coloured it according to a particular value. These values can be discrete (e.g. continent) or continuous (e.g. cancer prevalence). Also, for small countries dots are plotted for an easier visualization. More specifically, dots appear when the country polygon area is smaller than a ``DOT_THRESHOLD`` proportion over the shown map area; e.g. if ``DOT_THRESHOLD=0.001`` and the map area is 1000, all countries whose polygon(s) area are smaller than 1 will be displayed with a dot.

The basic function to generate the map accepts the following parameters:

* **data**: Dataframe with, at least, the columns identifying the country and the values (mandatory).
* **region**: Region around the map will be bounded. It can be any of the five continent ISO3 codes (i.e. 'XFX', 'XSX', 'XMX', 'XEX', 'XOX' for Africa, Asia, America, Europe or Oceania respectively) or a world map ('XWX') (mandatory). Countries outside the specified *region* will be coloured with a different colour (*out_region_color*).
* **value_field**: Column of the dataframe *data* that represents the value to colour in the map (mandatory). If the column type is numeric the scale is assumed to be continuous and the countries will be coloured in a gradient. Otherwise the scale is assumed to be discrete and the countries will be coloured according to a palette. Both scales can be configured in the *scale_params* parameter.
* **iso_field**: Column of the dataframe *data* that represents the countries' ISO3 code. This value will be used to match the corresponding *value_field* to a particular country in the map. By default it will look for the column 'iso'.
* **scale_params**: Dictionary with the parameters that will be passed to the ``scale_fill_*`` to configure the scale. Empty dictionary by default. For example:
  
  .. code-block:: python

    {
        'name': 'Prevalence (%)',
        'limits': [0,100],
        'breaks': [0, 25, 50, 75, 100],
        'labels': ['0%', '25%', '50%', '75%', '100%']
    }

  For more information please check the plotnine_ documentation.

* **plot_na_dots**: True if the dots for small countries should be plotted if the country has no data available, false otherwise. False by default.
* **tolerance**: Coordinate measure on how much error in the coordinates is allowed after polygon simplification is performed. By default sensible values are applied depending on the region. There is a tradeoff between fidelity to the original map and rendering performance.
* **plot_size**: (Relative) size of the plot. Since its actual size depends on how the plot is saved, this value is only relevant when deciding the relative size of the rest of plot components (labels, dots, legends, ...). The default value of 8 is reasonable when the map is embedded in a regular A4-wide PDF file.
* **out_region_color**: Hexadecimal colour value of the countries that are out of the chosen region. They are coloured differently to focus only on those from the region. By default is '#f0f0f0'.
* **na_color**: Hexadecimal colour value of the countries with no available data. The dots for small countries will also be coloured in this color unless *plot_na_dots* is False. By default is '#aaaaaa'.
* **line_color**: Hexadecimal colour value of the borders between countries. By default is '#666666'.
* **projection**: The map projection used. The projections implemented are the EPSG4326 ('epsg4326') and the robinson ('robinson'). Maps centered on Oceania cannot be projected appropriately using 'robinson' for wrapping reasons, so it is disabled for this particular case.

.. _plotnine: http://plotnine.readthedocs.io
