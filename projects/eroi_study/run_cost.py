# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model.

@author: Paolo Thiran, Matija Pavičević, Antoine Dubois, Jonathan Dumas
"""

import yaml
import os

import pandas as pd
import energyscope as es
import numpy as np

from sys import platform

from energyscope.utils import make_dir, load_config, get_fec_from_sankey
from energyscope.postprocessing import get_total_einv
from projects.eroi_study.res_RE_domestic_share import compute_fec
from projects.eroi_study.utils_res import get_gwp, get_cost


def loop_cost_computation(range_val, dir_name: str, GWP_op_ini: float, config: dict):
    """
    Minimize the system Cost for several GWP_tot <= p * GWP_op_ini with p a percentage.
    :param range_val: range of p.
    :param dir_name: directory name.
    :param GWP_op_ini: GWP_op initial value.
    :param config: configuration file.
    """
    for gwp_tot_max, cs_name in zip(np.asarray([i for i in range_val]) * GWP_op_ini / 100, ['run_' + str(i) for i in range_val]):
        print('Case in progress %s' % cs_name)
        cs = f"{config['case_studies_dir']}/{dir_name + '/' + cs_name}"
        # Update the GWP limit
        config["system_limits"]['GWP_limit'] = gwp_tot_max
        # Saving data to .dat files into the config['temp_dir'] directory
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(out_path=estd_out_path, data=all_data, system_limits=config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

        mod_fns = [f"{config['ES_path']}/ESTD_model_cost.mod"]
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, [estd_out_path, td12_out_path], config['temp_dir'])
        es.draw_sankey(sankey_dir=f"{cs}/output/sankey")


if __name__ == '__main__':

    # Get the current working directory
    cwd = os.getcwd()
    # Print the current working directory
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config.yaml')

    # Create the temp_dir if it does not exist
    make_dir(config['temp_dir'])

    # Loading data
    all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # -----------------------------------------------
    # Min Cost
    # s.t. GWP_tot <= p * GWP_op^i with p a percentage and GWP_op^i computed by Min Einv without contraint on GWP_tot
    # -----------------------------------------------
    dir_name = 'cost_GWP_tot'
    GWP_op_ini = get_gwp(cs=f"{config['case_studies_dir']}/{'einv_GWP_tot_0/run_100'}")['GWP_op']
    print('GWP_limit initial %.1f [MtC02/y]' %(GWP_op_ini/1000))
    range_val = range(100, 0, -5)
    loop_cost_computation(range_val=range_val, dir_name=dir_name, GWP_op_ini=GWP_op_ini, config=config)