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

__all__ = ['generate_map', 'DEFAULT_TOLERANCES', 'DOT_THRESHOLD',
           'REGION_BOUNDS', 'PROJECTION_DICT']

PROJECTION_DICT = {
    'robinson': {
        'proj': 'robin'
    },
    'epsg4326': {}
}
''' Pyproj projections. '''

REGION_BOUNDS = {
    'robinson': {
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
        'XOX': None  # Uncapable of wrapping in this projection, disabled
    },
    'epsg4326': {
        'XWX': (
            [-163, 80],
            [163, -60]
        ),
        'XFX': (
            [-25, 38],
            [56, -38]
        ),
        'XMX': (
            [-165, 80],
            [-15, -60]
        ),
        'XSX': (
            [28, 57],
            [155, -16]
        ),
        'XEX': (
            [-32, 80],
            [103, 35]
        ),
        'XOX': (  # In EPSG:4326 coordinates
            [110.049387, 23.214162],
            [-118.454180 + 360, -51.583946, ]
        )
    }
}
''' Region bounds by projection coordinates '''

DEFAULT_TOLERANCES = {
    'robinson': {
        'XWX': 40000,
        'XFX': 26000,
        'XMX': 40000,
        'XSX': 32000,
        'XEX': 13000,
        'XOX': None  # Uncapable of wrapping in this projection, disabled
    },
    'epsg4326': {
        'XWX': .6,
        'XFX': .2,
        'XMX': .4,
        'XSX': .2,
        'XEX': .1,
        'XOX': .4,  # In EPSG:4326 coordinates
    }
}
''' Default tolerances for polygon simplification in different regions by
projection. '''

DOT_THRESHOLD = .00001
''' A dot will be plotted for countries with areas below this percentage of
the total shown map area. '''


def generate_map(data,
                 region,
                 value_field,
                 iso_field='iso',
                 scale_params=None,
                 plot_na_dots=False,
                 tolerance=None,
                 plot_size=8,
                 out_region_color='#f0f0f0',
                 na_color='#aaaaaa',
                 line_color='#666666',
                 projection=None):
    """
    This function returns a map plot with the specified options.

    :param pandas.DataFrame data: Data to be plotted.
    :param str region: Region to center the map around. Countries outside
        the chosen region will be obscured.
    :param str value_field: Column of *data* with the values to be plotted.
    :param str iso_field: Column of *data* with the ISO3 codes for each
        country.
    :param dict scale_params: Dictionary of parameters to be passed to the
        ggplot corresponding color scale (continuous or discrete).
    :param bool plot_na_dots: Whether to plot the dots for small countries
        if said country doesn't have data available.
    :param int tolerance: Coordinate tolerance for polygon simplification,
        a higher number will result in simpler polygons and faster
        rendering (see DEFAULT_TOLERANCES).
    :param int plot_size: Size of the plot, which determines the relative sizes
        of the elements within.
    :param str out_region_color: Hex color of the countries that are out of the
        specified region.
    :param str na_color: Hex color of the countries with no data available.
    :param str line_color: Color of the country borders.
    :param str projection: Kind of map projection to be used in the map.
        Currently, Oceania (XOX) is only available in ESPG:4326 to enable
        wrapping.
    :returns: a ggplot-like plot with the map
    :rtype: plotnine.ggplot
    """
    if projection is None:
        if region == 'XOX':
            projection = 'epsg4326'
        else:
            projection = 'robinson'

    if projection not in PROJECTION_DICT.keys():
        raise ValueError('Projection "{}" not valid'.format(projection))

    if scale_params is None:
        scale_params = {}

    if region not in REGION_BOUNDS[projection]:
        raise ValueError(
            '"region" not available. Valid regions are: {}'.format(
                ', '.join(REGION_BOUNDS[projection].keys())
            ))

    if tolerance is None:
        tolerance = DEFAULT_TOLERANCES[projection][region]

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
        if projection != 'epsg4326':
            countries = countries.to_crs(PROJECTION_DICT[projection])
            centroids = countries.apply(
                lambda row: row['geometry'].centroid,
                axis=1)
            countries['lon'] = [c.x for c in centroids]
            countries['lat'] = [c.y for c in centroids]

    countries['geometry'] = countries['geometry'].simplify(tolerance)

    upper_left, lower_right = REGION_BOUNDS[projection][region]
    limits_x = [upper_left[0], lower_right[0]]
    limits_y = [lower_right[1], upper_left[1]]
    ratio = (limits_x[1] - limits_x[0]) / (limits_y[1] - limits_y[0])

    plot_data = pd.merge(countries,
                         data,
                         how='left',
                         left_on='iso',
                         right_on=iso_field)
    map_bounds = REGION_BOUNDS['epsg4326'][region]
    map_area = (
        (map_bounds[1][0] - map_bounds[0][0]) *
        (map_bounds[0][1] - map_bounds[1][1])
    )
    plot_data['plot_dot'] = (plot_data['pol_area'] <
                             DOT_THRESHOLD * map_area)

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
        out_region = np.repeat(False, len(plot_data))

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
                    size=0.3) +
           geom_map(plot_data_missing,
                    aes(color='plot_dot'),
                    fill=na_color,
                    size=0.3) +
           geom_map(plot_data_out_region,
                    fill=out_region_color,
                    color=line_color,
                    size=0.3) +
           geom_point(dots_region,
                      aes(x='lon', y='lat', fill=value_field),
                      size=3,
                      stroke=.1,
                      color=line_color) +
           geom_point(dots_region_missing,
                      aes(x='lon', y='lat'),
                      fill=na_color,
                      size=3,
                      stroke=.1,
                      color=line_color) +
           geom_point(dots_out_region,
                      aes(x='lon', y='lat'),
                      fill=out_region_color,
                      size=3,
                      stroke=.1,
                      color=line_color) +
           scale_x_continuous(breaks=[], limits=limits_x) +
           scale_y_continuous(breaks=[], limits=limits_y) +
           theme(figure_size=(plot_size*ratio, plot_size),
                 panel_background=element_rect(fill='white', color='black'),
                 #  panel_border=element_rect(fill='white',
                 #                            color='black',
                 #                            size=.1),
                 legend_background=element_rect(
                     fill="white",
                     color='black',
                     size=.5),
                 legend_box_just='left'
                 ) +
           xlab('') + ylab('')
          )

    if len(plot_data_values.index) > 0:
        plt += fill_scale

    plt += scale_color_manual(name=' ',
                              values=[line_color],
                              breaks=[False],
                              labels=['No data available'])

    if plot_data[value_field].dtype == 'object':
        plt += guides(fill=guide_legend(override_aes={'shape': None}))

    return {
        'plot': plt,
        'ratio': ratio,
    }