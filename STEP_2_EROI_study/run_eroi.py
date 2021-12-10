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
from energyscope.misc.utils import make_dir
from energyscope.postprocessing.utils import get_total_einv


def load_config(config_fn: str):
    """
    Load the configuration into a dict.
    :param config_fn: configuration file name.
    :return: a dict with the configuration.
    """

    # Load parameters
    cfg = yaml.load(open(config_fn, 'r'), Loader=yaml.FullLoader)

    if platform == "linux":
        cfg['energyscope_dir'] = '/home/jdumas/PycharmProjects/EnergyScope_multi_criteria/'
        cfg['AMPL_path'] = '/home/jdumas/PycharmProjects/ampl_linux-intel64/ampl'
    else:
        cfg['energyscope_dir'] = '/Users/dumas/PycharmProjects/EnergyScope_multi_criteria/'
        cfg['AMPL_path'] = '/Users/dumas/PycharmProjects/ampl_macos64/ampl'
        cfg['solver'] = "cplex"

    # Extend path
    for param in ['case_studies_dir', 'user_data', 'developer_data', 'temp_dir', 'ES_path', 'step1_output']:
        cfg[param] = os.path.join(cfg['energyscope_dir'], cfg[param])

    return cfg


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

    # Saving data to .dat files into the config['temp_dir'] directory
    estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
    es.print_estd(out_path=estd_out_path, data=all_data, import_capacity=config["import_capacity"], system_limits=config["system_limits"])
    td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
    # WARNING
    if not os.path.isfile(config["step1_output"]):
        print('WARNING: the STEP1 that consists of generating the 12 typical days must be conducted before to compute the TD_of_days.out file located in %s' %(config["step1_output"]))
    es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

    # Print run file
    run_fn = f"{config['ES_path']}/master.run"
    mod_fns = [f"{config['ES_path']}/ESTD_model.mod"]
    es.print_run(run_fn, mod_fns, [estd_out_path, td12_out_path], config['options'], f"{config['temp_dir']}/output")

    # Running EnergyScope
    cs = f"{config['case_studies_dir']}/{config['case_study_name']}"
    run_fn = f"{config['ES_path']}/master.run"
    es.run_energyscope(cs, run_fn, config['AMPL_path'], config['temp_dir'])

    # Example to print the sankey from this script
    output_dir = f"{config['case_studies_dir']}/{config['case_study_name']}/output/"
    es.drawSankey(path=f"{output_dir}/sankey")

    # TODO: check if it is ok to use the GWP_op as limit
    # Get the GWP op
    cs = f"{config['case_studies_dir']}/{'run100'}"
    gwp = pd.read_csv(f"{cs}/output/gwp_breakdown.csv", index_col=0, sep=',')
    gwp_op_tot = gwp.sum()['GWP_op']

    # Get the EROI
    total_demand = 388 # TWh
    # TODO: check if total demand is 388 TWh
    einv_tot = get_total_einv(cs)/1000 # TWh
    eroi_ini = total_demand/einv_tot
    print('EROI %.2f GWP op MtC02eq %.2f' %(eroi_ini, gwp_op_tot))

    # LOOP on several GWP maximum values and compute the related EROI
    eroi_list = []
    eroi_list.append(eroi_ini)
    for gwp_limit, cs_name in zip(np.asarray([i for i in range(5, 100, 5)]) * gwp_op_tot,['run_'+str(i) for i in range(5, 100, 5)]):
        print('RUN in progess %s' %(cs_name))
        # Update the GWP limit
        config["system_limits"]['GWP_limit'] = gwp_limit
        # Saving data to .dat files into the config['temp_dir'] directory
        out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(out_path=out_path, data=all_data, import_capacity=config["import_capacity"],  system_limits=config["system_limits"])
        out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(out_path=out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

        # Running EnergyScope
        cs = f"{config['case_studies_dir']}/{cs_name}"
        run_fn = f"{config['ES_path']}/master.run"
        es.run_energyscope(cs, run_fn, config['AMPL_path'], config['temp_dir'])

        # Example to print the sankey from this script
        output_dir = f"{config['case_studies_dir']}/{config['case_study_name']}/output/"
        es.drawSankey(path=f"{output_dir}/sankey")

        # Compute the EROI
        einv_temp = get_total_einv(cs) / 1000  # TWh
        eroi_temp = total_demand / einv_temp
        print('EROI %.2f GWP op MtC02eq %.2f' % (eroi_temp, gwp_limit))
        eroi_list.append(eroi_temp)

    # TODO: plot with EROI vs GWP and save plot