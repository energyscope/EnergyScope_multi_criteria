# -*- coding: utf-8 -*-
"""
Created on Jan 18 2022

Contains functions to retrieve results from an AMPL run

@author: Paolo Thiran, Antoine Dubois
"""
from typing import Dict

import pandas as pd

import amplpy


def to_pd(amplpy_df: amplpy.DataFrame) -> pd.DataFrame:
    """
    Transform an amplpy.DataFrame into pandas.DataFrame for easier manipulation

    Parameters
    ----------
    amplpy_df : amplpy.DataFrame
        amplpy dataframe to transform

    Returns
    -------
    df : pandas.DataFrame
        DataFrame transformed as 'long' dataframe (can be easily pivoted later)
    """
    headers = amplpy_df.getHeaders()
    columns = {header: list(amplpy_df.getColumn(header)) for header in headers}
    return pd.DataFrame(columns)


def get_results(ampl_trans: amplpy.AMPL) -> Dict[str, pd.DataFrame]:
    """
    Extract the values of each variable after running the optimization problem

    Parameters
    ----------
    ampl_trans : amplpy.AMPL
        AMPL translator containing the results of the aggregation

    Returns
    -------
    results: Dict[str, pd.DataFrame]
        Dictionary containing the values of each output variable

    """
    # function to get the results of ampl under the form of a dict filled with one df for each variable
    amplpy_sol = ampl_trans.getVariables()
    results = dict()
    for name, var in amplpy_sol:
        results[name] = to_pd(var.getValues())
    return results


def get_parameters(ampl_trans: amplpy.AMPL) -> Dict[str, pd.DataFrame]:
    """
    Extract the values of each parameter

    Parameters
    ----------
    ampl_trans : amplpy.AMPL
        AMPL translator containing the parameters values

    Returns
    -------
    results: Dict[str, pd.DataFrame]
        Dictionary containing the values of each parameter

    """
    # function to get the results of ampl under the form of a dict filled with one df for each variable
    amplpy_sol = ampl_trans.getParameters()
    parameters = dict()
    for name, param in amplpy_sol:
        parameters[name] = to_pd(param.getValues())
    return parameters


def get_subset(my_set: amplpy.set.Set) -> Dict:
    """
    Function to extract the subsets of set containing sets from the AMPL() object

    Parameters
    ----------
    my_set : amplpy.set.Set
        2-dimensional set to extract

    Returns
    -------
    d : Dict
       dictionary containing the subsets as lists
    """
    d = dict()
    for n, o in my_set.instances():
        try:
            d[n] = o.getValues().toList()
        except Exception:
            d[n] = list()
    return d


def get_sets(ampl_trans: amplpy.AMPL) -> Dict:
    """
    Function to get sets of the LP optimization problem
    """
    sets = dict()
    for name, s in ampl_trans.getSets():
        if len(s.instances()) <= 1:
            sets[name] = s.getValues().toList()
        else:
            sets[name] = get_subset(s)
    return sets


def simplify_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.set_index("index0")
    df.index.name = 'Name'
    df.columns = [c.split('.')[0] for c in df.columns]
    return df


def time_to_pandas(sets: Dict) -> pd.Series:
    """
    Aggregate time sets 'HOUR_OF_PERIOD' and 'TYPICAL_DAY_OF_PERIOD' into a pandas Series

    Parameters
    ----------
    sets: Dict
        Dictionary containing all the sets 'PERIODS', 'HOUR_OF_PERIOD' and 'TYPICAL_DAY_OF_PERIOD'

    Returns
    -------
    pd.Series
        Series with index 'PERIODS' and values which are tuples combining 'HOUR_OF_PERIOD' and 'TYPICAL_DAY_OF_PERIOD'
    """

    # Convert 'time' sets to pandas
    hs = [sets['HOUR_OF_PERIOD'][t][0] for t in sets['PERIODS']]  # corresponding hour of the day
    tds = [sets['TYPICAL_DAY_OF_PERIOD'][t][0] for t in sets['PERIODS']]  # corresponding number of the typical day
    hs_tds = list(zip(hs, tds))
    return pd.Series(hs_tds, index=sets['PERIODS'])