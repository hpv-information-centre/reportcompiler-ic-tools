"""
This module contains utility functions to be used with the rest of this
libraries' functionality.
"""
import pandas as pd

__all__ = ['wrap_empty_references']


def wrap_empty_references(data):
    """
    Convenience function that wraps a dataframe in a dictionary with the
    required structure for methods using data references (e.g. the
    reportcompiler_ic_tools.tables module). This is useful, for example,
    when a dataframe needs to be built manually and then used as input
    for the tables.generate_table_data method, which expects this kind
    of structure.
    """
    return {
        'data': data,
        'sources': {},
        'notes': {},
        'methods': {},
        'years': {},
        'date': {},
    }
