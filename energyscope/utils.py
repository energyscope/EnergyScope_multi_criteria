# -*- coding: utf-8 -*-

import os
from sys import platform
from typing import List
from pathlib import Path

import yaml
import pandas as pd
import numpy as np
import pickle

from energyscope.step2_output_generator import time_to_pandas


# TODO: remove ?
def make_dir(path: str):
    """Create the directory if it does not exist."""
    if not os.path.isdir(path):
        os.mkdir(path)


def load_config(config_fn: str):
    """
    Load the configuration into a dict.
    :param config_fn: configuration file name.
    :return: a dict with the configuration.
    """

    # Load parameters
    cfg = yaml.load(open(config_fn, 'r'), Loader=yaml.FullLoader)

    # TODO: the user must adapt its paths
    if platform == "linux":
        cfg['energyscope_dir'] = '/home/jdumas/PycharmProjects/EnergyScope_multi_criteria/'
        cfg['AMPL_path'] = '/home/jdumas/PycharmProjects/ampl_linux-intel64'
    else:
        cfg['energyscope_dir'] = '/Users/dumas/PycharmProjects/EnergyScope_multi_criteria/'
        cfg['AMPL_path'] = '/Users/dumas/PycharmProjects/ampl_macos64'
        cfg['options']['solver'] = "cplex"

    # Extend path
    for param in ['case_studies_dir', 'user_data', 'developer_data', 'temp_dir', 'ES_path', 'step1_output']:
        cfg[param] = os.path.join(cfg['energyscope_dir'], cfg[param])

    return cfg


def get_colors(elements: List[str], element_type: str, data_path: str) -> pd.Series:
    """
    Return the list of colors (in hexadecimal) corresponding to the resources or techs passed
    :param elements: List of resources or technologies
    :param element_type: 'resource' or 'technologies'
    :param data_path: Path to Data directory
    """

    accepted_types = ['resources', 'technologies']
    assert element_type in accepted_types, f'Error: element_type must be one of {accepted_types}.'

    fn = os.path.join(data_path, f"User_data/aux_{element_type}.csv")
    colors = pd.read_csv(fn, index_col=0)["Color"]

    for element in elements:
        assert element in colors.index, f'Error: element {element} has no associated color.'

    return colors.loc[elements]


def get_names(elements: List[str], element_type: str, data_path: str) -> pd.Series:
    """
    Return the list of names corresponding to the resources or techs passed
    :param elements: List of resources or technologies
    :param element_type: 'resource' or 'technologies'
    :param data_path: Path to Data directory
    """

    accepted_types = ['resources', 'technologies']
    assert element_type in accepted_types, f'Error: element_type must be one of {accepted_types}.'

    fn = os.path.join(data_path, f"User_data/aux_{element_type}.csv")
    colors = pd.read_csv(fn, index_col=0)["Name"]

    for element in elements:
        assert element in colors.index, f'Error: element {element} has no associated color.'

    return colors.loc[elements]


# TODO: would be cooler to be able to compute it from the inputs directly
def compute_max_production(results_dir_name: str):

    # Load results
    with open(f"{results_dir_name}/output/parameters.pickle", 'rb') as handle:
        parameters = pickle.load(handle)

    with open(f"{results_dir_name}/output/sets.pickle", 'rb') as handle:
        sets = pickle.load(handle)

    # Resources breakdown
    f_max = parameters['f_max'].set_index(['index0']).squeeze()
    c_p_t = parameters['c_p_t'].set_index(['index0', 'index1', 'index2']).squeeze()
    times = time_to_pandas(sets)
    technologies = sorted(sets['TECHNOLOGIES'])
    print(type(f_max['BATT_LI']))

    max_production = pd.Series(0., index=technologies)
    for tech in technologies:
        if f_max[tech] < 1e100:
            max_production[tech] = (f_max[tech] * c_p_t.loc[tech].loc[times]).sum()

    return max_production[max_production != 0]


def compute_max_production_old():

    ts = pd.read_csv(
        "/home/duboisa1/Global_Grid/code/EnergyScope_multi_criteria/Data_v2/Developer_data/Time_series.csv",
        index_col=0)

    tech = "PV"
    ts = ts[tech].squeeze()
    capacities = {'PV': 59.2,
                  'Hydro_river': 0.115,
                  'Wind_offshore': 6,
                  'Wind_onshore': 10,
                  'PHS': 6.5}
    capacity = capacities[tech]
    print(ts.sum()*capacity)

    # TODO: this is disgusting and still not correct
    ts = ts.reset_index()
    ts.columns = ['old_index', tech]
    ts.index = [int(np.ceil(i/24)) for i in ts['old_index']]
    ts = ts[tech]
    ts.index.name = 'index'
    ts = ts.groupby('index').sum()
    norm = ts.sum()
    print(ts.sum() * capacity)

    repr_day = pd.read_csv(
        "/home/duboisa1/Global_Grid/code/EnergyScope_multi_criteria/energyscope/step1_io/TD_of_days_12.out",
        header=None).squeeze()
    # print(repr_day)

    ts = ts.loc[repr_day.values]
    norm_td = ts.groupby('index').sum()
    # print(norm_td)
    print((ts*norm/norm_td).sum()*capacity)
    # print(ts)
    # print(np.unique(ts.values))
    print(ts.sum()*capacity)


def get_fec_from_sankey(case_study_dir: str, col: str):
    """
    Compute the Final Energy Consumption (FEC) from the Sankey data.
    :param case_study_dir: path to the case study directory.
    :param col: case study name.
    Return the FEC [TWh] by end use demand: 'Non-energy demand', 'Loss DHN', 'Heat LT DHN', 'Exp & Loss', 'Mob public', 'Heat LT Dec', 'Elec demand', 'Freight', 'Mob priv', 'Heat HT'.
    """
    df_sankey = pd.read_csv(f"{case_study_dir}/output/sankey/input2sankey.csv", index_col=0, sep=',')
    ef_list = ['Non-energy demand', 'Loss DHN', 'Heat LT DHN', 'Exp & Loss', 'Mob public', 'Heat LT Dec', 'Elec demand',
               'Freight', 'Mob priv', 'Heat HT']
    ef_final_val = []
    for final_demand in ef_list:
        ef_final_val.append(df_sankey[df_sankey['target'] == final_demand]['realValue'].sum())

    return pd.DataFrame(index=ef_list, data=ef_final_val, columns=[col])