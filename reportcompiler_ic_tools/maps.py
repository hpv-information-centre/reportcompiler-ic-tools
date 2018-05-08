"""
This module contains helper functions to plot maps from the HPV Information
Centre data.
"""
import pandas as pd
import numpy as np
import pyproj
import os
from pprint import pprint
from geopandas import GeoDataFrame
from odictliteral import odict
from plotnine import ggplot, aes, scale_fill_brewer, scale_fill_gradient, \
    scale_color_manual, scale_x_continuous, scale_y_continuous, geom_point, \
    theme, guides, guide_colorbar, xlab, ylab, element_rect, element_text, \
    theme_bw, guide_legend
from plotnine.geoms.geom_map import geom_map


# Pyproj projections
PROJECTION_DICT = {
    'robinson': {
        'proj': 'robin'
    }
}

# Robinson coordinates, except Oceania (EPSG:4326)
REGION_BOUNDS = {
    'XWX': (
        [-16000000, 8000000],
        [16000000, -6000000]
    ),
    'XFX': (
        [-1580000, 3800000],
        [5580000, -4040000]
    ),
    'XMX': (
        [-14500000, 8000000],
        [-1000000, -5700000]
    ),
    'XSX': (
        [2500000, 5800000],
        [13000000, -970000]
    ),
    'XEX': (
        [-2500000, 8200000],
        [5000000, 3800000]
    ),
    'XOX': (  # In EPSG:4326 coordinates
        [110.049387, 23.214162],
        [-118.454180 + 360, -51.583946, ]
    ),
}

# A dot will be plotted for countries with areas below this value
DOT_THRESHOLD = 35


def generate_map(data,
                 region,
                 value_field,
                 iso_field='iso',
                 scale_params=None,
                 plot_na_dots=False,
                 out_region_color='#f0f0f0',
                 na_color='#aaaaaa',
                 line_color='#666666',
                 projection='robinson'):
    if scale_params is None:
        scale_params = {}

    if region not in REGION_BOUNDS:
        raise ValueError(
            '"region" not available. Valid regions are: {}'.format(
                ', '.join(REGION_BOUNDS.keys())
            ))

    countries = GeoDataFrame.from_file(
        os.path.join(os.path.dirname(__file__), 'data/world-countries.shp'))

    # To plot Oceania we need the original EPSG:4326 to wrap around the 180º
    # longitude. In other cases transform to the desired projection.
    if region == 'XOX':
        countries.crs['lon_wrap'] = '180'  # Wrap around longitude 180º

        XOX_countries = countries['continent'] == 'XOX'
        countries[XOX_countries] = countries[XOX_countries].to_crs(
            countries.crs)
        centroids = countries[XOX_countries].apply(
            lambda row: row['geometry'].centroid,
            axis=1)
        countries.loc[XOX_countries, 'lon'] = [c.x for c in centroids]
        countries.loc[XOX_countries, 'lat'] = [c.y for c in centroids]
    else:
        countries = countries.to_crs(PROJECTION_DICT[projection])

    upper_left, lower_right = REGION_BOUNDS[region]
    limits_x = [upper_left[0], lower_right[0]]
    limits_y = [lower_right[1], upper_left[1]]
    ratio = (limits_x[1] - limits_x[0]) / (limits_y[1] - limits_y[0])

    plot_data = pd.merge(countries,
                         data,
                         how='left',
                         left_on='iso',
                         right_on=iso_field)
    plot_data['plot_dot'] = (plot_data['area'] < DOT_THRESHOLD)

    if not plot_na_dots:
        plot_data['plot_dot'] &= ~pd.isnull(plot_data[value_field])

    if region != 'XWX':
        in_region = ((~pd.isnull(plot_data[value_field])) &
                     (plot_data['continent'] == region))
        in_region_missing = ((pd.isnull(plot_data[value_field])) &
                             (plot_data['continent'] == region))
        out_region = plot_data['continent'] != region
    else:
        in_region = ~pd.isnull(plot_data[value_field])
        in_region_missing = pd.isnull(plot_data[value_field])
        out_region = np.empty_like(plot_data)

    if plot_data[value_field].dtype == 'object':
        # Assume discrete values
        fill_scale = scale_fill_brewer(**scale_params, drop=False)
    else:
        # Assume continuous values
        fill_scale = scale_fill_gradient(**scale_params)

    plot_data_values = plot_data[in_region]
    plot_data_missing = plot_data[in_region_missing]
    plot_data_out_region = plot_data[out_region]

    dots_region = plot_data_values[plot_data_values['plot_dot']]
    dots_region_missing = plot_data_missing[plot_data_missing['plot_dot']]
    dots_out_region = plot_data_out_region[plot_data_out_region['plot_dot']]

    plt = (
           ggplot() +
           geom_map(plot_data_values,
                    aes(fill=value_field),
                    color=line_color,
                    size=0.2) +
           geom_map(plot_data_missing,
                    aes(color='plot_dot'),
                    fill=na_color,
                    size=0.2) +
           geom_map(plot_data_out_region,
                    fill=out_region_color,
                    color=line_color,
                    size=0.2) +
           geom_point(dots_region,
                      aes(x='lon', y='lat', fill=value_field),
                      size=5,
                      color=line_color) +
           geom_point(dots_region_missing,
                      aes(x='lon', y='lat'),
                      fill=na_color,
                      size=5,
                      color=line_color) +
           geom_point(dots_out_region,
                      aes(x='lon', y='lat'),
                      fill=out_region_color,
                      size=5,
                      color=line_color) +
           scale_x_continuous(breaks=[], limits=limits_x) +
           scale_y_continuous(breaks=[], limits=limits_y) +
           fill_scale +
           scale_color_manual(name=' ',
                              values=[line_color],
                              breaks=[False],
                              labels=['No data available']) +
           theme(figure_size=(10*ratio, 10),
                 panel_background=element_rect(fill='white', color='black'),
                 panel_border=element_rect(fill='white', color='black')) +
           xlab('') + ylab('')
          )

    if plot_data[value_field].dtype == 'object':
        plt += guides(fill=guide_legend(override_aes={'shape': None}))

    return plt
