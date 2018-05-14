"""
This module contains helper functions to create tables with the Information
Centre data.
"""
import pandas as pd
from pprint import pprint
from odictliteral import odict
from reportcompiler_ic_tools.markers import \
    source_markers, note_markers, method_markers, year_markers


def generate_table(data_dict,
                   selected_columns=None,
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
    table_footer = {
        'sources': [],
        'notes': [],
        'methods': [],
        'years': [],
    }

    for ref_type, markers in ref_types.items():
        ref_data = data_dict[ref_type]
        _build_global_refs(ref_data['global'],
                           table_footer[ref_type],
                           markers,
                           ref_type)
        column_names = _build_column_refs(marker_data,
                                          column_names,
                                          ref_data['column'],
                                          table_footer[ref_type],
                                          markers, ref_type)
        _build_row_refs(marker_data,
                        ref_data['row'],
                        row_id_column,
                        table_footer[ref_type],
                        markers,
                        ref_type)
        _build_cell_refs(marker_data,
                         ref_data['cell'],
                         table_footer[ref_type],
                         markers,
                         ref_type)

    referenced_data = _build_table(data, marker_data, format)
    referenced_data = referenced_data[selected_columns]
    for ref_type, _ in ref_types.items():
        table_footer[ref_type] = [{'marker': _marker, 'text': _ref}
                                  for _marker, _ref
                                  in table_footer[ref_type]]

    return (referenced_data, column_names, table_footer)


def merge_references(*data_dicts):
    # TODO: Implementation
    pass


def _build_table(data, marker_data, format):
    type_functions = {
        'latex': _build_latex_table,
    }

    try:
        return type_functions[format](data, marker_data)
    except KeyError:
        raise ValueError("'{}' table type is not defined")


def _build_latex_table(data, marker_data):
    marker_data = marker_data.applymap(
        lambda lst: r'$^{' + ','.join(lst) + '}$' if lst != [] else ''
    )
    data = data.applymap(
        lambda val: str(val)
    )
    return data + marker_data


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


def _build_cell_refs(marker_data, ref_data, table_footer, markers, ref_type):
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

__all__ = ['generate_references']
