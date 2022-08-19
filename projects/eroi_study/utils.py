# -*- coding: utf-8 -*-

from sys import platform
import os

import yaml
import pandas as pd


def load_config(config_fn: str):
    """
    Load the configuration into a dict.
    :param config_fn: configuration file name.
    :return: a dict with the configuration.
    """

    # Load parameters
    cfg = yaml.load(open(config_fn, 'r'), Loader=yaml.FullLoader)

    # TODO: the user must adapt its paths
    # TODO: AD: this should not be made this way
    # if platform == "linux":
    #     cfg['energyscope_dir'] = '/home/jdumas/PycharmProjects/EnergyScope_multi_criteria/'
    #     cfg['AMPL_path'] = '/home/jdumas/PycharmProjects/ampl_linux-intel64'
    # else:
    #     cfg['energyscope_dir'] = '/Users/dumas/PycharmProjects/EnergyScope_multi_criteria/'
    #     cfg['AMPL_path'] = '/Users/dumas/PycharmProjects/ampl_macos64'
    #     cfg['options']['solver'] = "cplex"

    # Extend path
    for param in ['case_studies_dir', 'user_data', 'developer_data', 'temp_dir', 'ES_path', 'step1_output']:
        cfg[param] = os.path.join(cfg['energyscope_dir'], cfg[param])

    return cfg


def rename_columns(df: pd.DataFrame, old_col: list, new_col: list):
    """
    Rename columns of a pd.DataFrame.
    """
    new_cols = list(df.columns)
    for item_old, item_new in zip(old_col, new_col):
        new_cols = replace_item_in_list(target_list=new_cols, item_old=item_old, item_new=item_new)
    df.columns = new_cols
    return df


def replace_item_in_list(target_list: list, item_old: str, item_new: str):
    """
    Replace a specific item into a list.
    """
    for i in range(len(target_list)):
        if target_list[i] == item_old:
            target_list[i] = item_new
    return target_list
