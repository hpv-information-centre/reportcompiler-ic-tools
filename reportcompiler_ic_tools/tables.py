"""
This module contains helper functions to create tables with the Information
Centre data.
"""
import pandas as pd
from pprint import pprint
from odictliteral import odict
from reportcompiler_ic_tools.markers import \
    source_markers, note_markers, method_markers, year_markers


def generate_references(data_dict,
                        column_names=None,
                        row_id_column=None,
                        format='latex'):
    """
    Generates a new dataframe with the markers corresponding to the defined
        references (sources, notes, ...), alongside a list of the markers'
        meaning.
    :param dict data_dict: Dictionary returned by the IC data fetcher
    :param list column_names: List with the column names in the dataframe
    :param row_id_column: Column name that will contain the marks for row
        references
    :param str format: Format that the returned dataframe should comply with
    :returns: Original dataframe with necessary reference markers and a list
        of each marker with the reference text
    :rtype: tuple (dataframe, list)
    """
    data = data_dict['data']
    if column_names is None:
        column_names = data.columns
    if row_id_column is None:
        row_id_column = data.columns[0]
    if len(column_names) != len(data.columns):
        raise ValueError(
            'column_names must have the same lengths as the number of '
            'columns in data_dict')
    ref_types = odict[
        'sources': source_markers(),
        'notes': note_markers(),
        'methods': method_markers(),
        'years': year_markers(),
    ]

    marker_data = pd.DataFrame(data=None,
                               columns=data.columns,
                               index=data.index)
    for col in marker_data.columns:
        marker_data[col] = marker_data[col].astype(object)
        for row in marker_data.index:
            marker_data.loc[row, col] = []
    table_footer = []

    for ref_type, markers in ref_types.items():
        ref_data = data_dict[ref_type]
        _build_global_refs(ref_data['global'],
                           table_footer,
                           markers,
                           ref_type)
        column_names = _build_column_refs(marker_data,
                                          column_names,
                                          ref_data['column'],
                                          table_footer,
                                          markers, ref_type)
        _build_row_refs(marker_data,
                        ref_data['row'],
                        row_id_column,
                        table_footer,
                        markers,
                        ref_type)
        _build_cell_refs(marker_data,
                         ref_data['cell'],
                         table_footer,
                         markers,
                         ref_type)

    referenced_data = _merge_refs(data, marker_data, format)
    referenced_data.columns = column_names
    return (referenced_data, table_footer)


def _merge_refs(data, marker_data, format):
    type_functions = {
        'latex': _build_latex_items,
    }

    try:
        return type_functions[format](data, marker_data)
    except KeyError:
        raise ValueError("'{}' table type is not defined")


def _build_latex_items(data, marker_data):
    marker_data = marker_data.applymap(
        lambda lst: '$^{' + ','.join(lst) + '}$' if lst != [] else ''
    )
    data = data.applymap(
        lambda val: str(val)
    )
    return data + marker_data


def _build_global_refs(ref_data, table_footer, markers, ref_type):
    for ref in [ref.text for ref in ref_data.itertuples()]:
        marker = next(markers)
        if marker is None:
            raise EnvironmentError(
                "No more '{}' markers are available.".format(ref_type))
        table_footer.append((marker, ref))


def _build_column_refs(marker_data,
                       column_names,
                       ref_data,
                       table_footer,
                       markers,
                       ref_type):
    _column_names = column_names.copy()
    for i, column in enumerate(marker_data.columns):
        refs = [ref.text
                for ref in ref_data.itertuples()
                if ref.column == column]
        col_markers = []
        for ref in refs:
            marker = next(markers)
            if marker is None:
                raise EnvironmentError(
                    "No more '{}' markers are available.".format(ref_type))
            col_markers.append(marker)
            table_footer.append((marker, ref))
        if len(col_markers) > 0:
            joined_markers = ','.join(col_markers)
            _column_names[i] = \
                _column_names[i] + '$^{{{}}}$'.format(joined_markers)
    return _column_names


def _build_row_refs(marker_data,
                    ref_data,
                    row_id_column,
                    table_footer,
                    markers,
                    ref_type):
    for row_index in marker_data.index:
        refs = [ref.text
                for ref in ref_data.itertuples()
                if ref.row == row_index]
        row_markers = marker_data.loc[row_index, row_id_column]
        for ref in refs:
            marker = next(markers)
            if marker is None:
                raise EnvironmentError(
                    "No more '{}' markers are available.".format(ref_type))
            row_markers.append(marker)
            table_footer.append((marker, ref))


def _build_cell_refs(marker_data, ref_data, table_footer, markers, ref_type):
    for row_index in marker_data.index:
        for column in marker_data.columns:
            refs = [ref.text
                    for ref in ref_data.itertuples()
                    if ref.row == row_index and ref.column == column]
            for ref in refs:
                marker = next(markers)
                if marker is None:
                    raise EnvironmentError(
                        "No more '{}' markers are available.".format(ref_type))
                marker_data.loc[row_index, column].append(marker)
                table_footer.append((marker, ref))

__all__ = ['generate_references']
