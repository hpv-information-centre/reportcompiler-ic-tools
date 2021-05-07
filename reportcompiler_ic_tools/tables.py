"""
This module contains helper functions to create tables with the Information
Centre data.
"""
import pandas as pd
import numpy as np
from pprint import pprint
from odictliteral import odict
from reportcompiler_ic_tools.markers import \
    source_markers, note_markers, method_markers, year_markers

__all__ = ['generate_table_data']


def generate_table_data(data_dict,
                        selected_columns=None,
                        column_names=None,
                        row_id_column=None,
                        format='latex',
                        collapse_refs=True,
                        ref_type_markers=None,
                        footer=None,
                        markers=None):
    """
    Generates a new dataframe with the markers corresponding to the defined
        references (sources, notes, ...), alongside a list of the markers'
        meaning.

    :param dict data_dict: Dictionary returned by the IC data fetcher
    :param list selected_columns: List with the column names to be selected
        from the original dataframe
    :param list column_names: List with the column names of the selected
        dataframe columns
    :param str row_id_column: Column name that will contain the marks for row
        references
    :param str format: Format that the returned dataframe should comply with
    :param bool collapse_refs: Whether markers should be collapsed when
        appropriate (e.g. all cells of a column to the column header)
    :param dict footer: Dictionary with the footer information as returned from
        previous calls to this same function. This allows chaining several data
        sources in one single footer.
    :param dict markers: Dictionary with generators for markers for
        each type of reference ('sources', 'notes', 'methods', 'years'). If
        None, new generators will be initialized (starting at 1 with sources,
        'a' with notes, ...).
    :returns: Dictionary with four components: table, columns, footer, markers;
        where table is the original dataframe with the necessary reference
        markers, columns is the list with the table columns as will be
        displayed, footer is a nested structure: for each type (sources, notes,
        ...) there is a list of dictionaries with each ('marker' key) and
        associated reference ('text' key) and markers is a dictionary with the
        generators for the markers of each reference type.
    :rtype: dict
    """
    data = data_dict['data'].copy()
    if selected_columns is None:
        selected_columns = data.columns
    if column_names is None:
        column_names = data.columns
    if row_id_column is None:
        row_id_column = data.columns[0]
    if len(column_names) != len(selected_columns):
        raise ValueError(
            'column_names must have the same lengths as the number of '
            'columns in data_dict'
        )
    if not set(selected_columns).issubset(set(data.columns)):
        raise ValueError(
            'Selected columns must be included in the original dataframe'
        )
    data = data[selected_columns]
    if ref_type_markers is None:
        ref_type_markers = odict[
            'sources': source_markers(),
            'notes': note_markers(),
            'methods': method_markers(),
            'years': year_markers(),
        ]

    marker_data = pd.DataFrame(data=None,
                               columns=selected_columns,
                               index=data.index)
    for col in marker_data.columns:
        marker_data[col] = marker_data[col].astype(object)
        for row in marker_data.index:
            marker_data.loc[row, col] = []
    if footer is None:
        footer = {
            'sources': [],
            'notes': [],
            'methods': [],
            'years': [],
        }

    column_markers = [[] for col in selected_columns]
    for ref_type, markers in ref_type_markers.items():
        ref_data = data_dict[ref_type]
        _build_global_refs(ref_data['global'],
                           footer[ref_type],
                           markers,
                           ref_type)
        _column_markers = _build_column_refs(ref_data['column'],
                                             footer[ref_type],
                                             markers, ref_type,
                                             marker_data,
                                             selected_columns,
                                             column_names)
        for i, col in enumerate(column_markers):
            column_markers[i].extend(_column_markers[i])
        _build_row_refs(ref_data['row'],
                        footer[ref_type],
                        markers,
                        ref_type,
                        marker_data,
                        row_id_column)
        _build_cell_refs(ref_data['cell'],
                         footer[ref_type],
                         markers,
                         ref_type,
                         marker_data)

    column_info = [{'value': name, 'markers': markers}
                   for name, markers
                   in zip(column_names, column_markers)]

    referenced_table = _zip_table(data, marker_data, format)
    referenced_table = referenced_table[selected_columns]

    if collapse_refs:
        _collapse_common_refs(referenced_table, column_info)

    for ref_type, _ in ref_type_markers.items():
        footer[ref_type] = [{'marker': _marker, 'text': _ref}
                            for _marker, _ref
                            in footer[ref_type]]

    footer['date'] = data_dict['date']

    info_dict = {
        'table': referenced_table,
        'columns': column_info,
        'footer': footer,
        'markers': ref_type_markers
    }

    return info_dict


def _collapse_common_refs(table, columns):
    for i, col in enumerate(table.columns):
        markers = [cell['markers'] for cell in table[col]]
        col_markers = set([ref
                           for cell_markers in markers
                           for ref in cell_markers])
        for marker in col_markers:
            if (np.all([marker in cell['markers'] for cell in table[col]])):
                # Include marker in column
                columns[i]['markers'] += marker
                # Remove markers from cells
                for cell in table[col]:
                    cell['markers'].remove(marker)


def _zip_table(data, marker_data, format):
    for col in data.columns:
        data[col] = [{'value': value, 'markers': markers}
                     for value, markers
                     in list(zip(data[col], marker_data[col]))]
    return data


def _build_global_refs(ref_data, table_footer, markers, ref_type):
    for ref in [ref.text for ref in ref_data.itertuples()]:
        marker = None
        try:
            marker = [_marker
                      for _marker, _ref
                      in table_footer
                      if _ref == ref][0]
        except IndexError:
            pass
        if marker is None:
            table_footer.append(('', ref))


def _build_column_refs(ref_data,
                       table_footer,
                       markers,
                       ref_type,
                       marker_data,
                       selected_columns,
                       column_names):
    column_markers = []
    for column in selected_columns:
        refs = [ref.text
                for ref in ref_data.itertuples()
                if ref.column == column]
        col_markers = []
        for ref in refs:
            marker = None
            try:
                marker = [_marker
                          for _marker, _ref
                          in table_footer
                          if _ref == ref][0]
            except IndexError:
                pass
            if marker is None:
                try:
                    marker = next(markers)
                except StopIteration:
                    raise EnvironmentError(
                        "No more '{}' markers are available.".format(ref_type))
                table_footer.append((marker, ref))
            if marker not in col_markers:
                col_markers.append(marker)
        column_markers.append(col_markers)
    return column_markers


def _build_row_refs(ref_data,
                    table_footer,
                    markers,
                    ref_type,
                    marker_data,
                    row_id_column):
    for row_index in marker_data.index:
        refs = [ref.text
                for ref in ref_data.itertuples()
                if ref.row == row_index]
        row_markers = marker_data.loc[row_index, row_id_column]
        for ref in refs:
            marker = None
            try:
                marker = [_marker
                          for _marker, _ref
                          in table_footer
                          if _ref == ref][0]
            except IndexError:
                pass
            if marker is None:
                try:
                    marker = next(markers)
                except StopIteration:
                    raise EnvironmentError(
                        "No more '{}' markers are available.".format(ref_type))
                table_footer.append((marker, ref))
            if marker not in row_markers:
                row_markers.append(marker)


def _build_cell_refs(ref_data, table_footer, markers, ref_type, marker_data):
    for row_index in marker_data.index:
        for column in marker_data.columns:
            refs = [ref.text
                    for ref in ref_data.itertuples()
                    if ref.row == row_index and ref.column == column]
            for ref in refs:
                marker = None
                try:
                    marker = [_marker
                              for _marker, _ref
                              in table_footer
                              if _ref == ref][0]
                except IndexError:
                    pass
                if marker is None:
                    try:
                        marker = next(markers)
                    except StopIteration:
                        raise EnvironmentError(
                            "No more '{}' markers are available.".format(
                                ref_type))
                    table_footer.append((marker, ref))
                if marker not in marker_data.loc[row_index, column]:
                    marker_data.loc[row_index, column].append(marker)
