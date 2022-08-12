# -*- coding: utf-8 -*-

from sys import platform
import os

import yaml


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
