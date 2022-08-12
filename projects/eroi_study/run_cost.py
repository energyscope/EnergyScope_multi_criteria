# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model.

@author: Paolo Thiran, Matija Pavičević, Antoine Dubois, Jonathan Dumas
"""

# import yaml
import os

import pandas as pd
import energyscope as es
import numpy as np

# from sys import platform

from energyscope.utils import make_dir, get_fec_from_sankey
from energyscope.postprocessing import get_total_einv, get_gwp, get_cost, compute_fec
from projects.eroi_study.utils import load_config


def loop_cost_computation(range_val, dir_name: str, gwp_op_ini: float, config: dict):
    """
    Minimize the system Cost for several GWP_tot <= p * gwp_op_ini with p a percentage.
    :param range_val: range of p.
    :param dir_name: directory name.
    :param gwp_op_ini: GWP_op initial value.
    :param config: configuration file.
    """
    for gwp_tot_max, cs_name in zip(np.asarray([i for i in range_val]) * gwp_op_ini / 100,
                                    ['run_' + str(i) for i in range_val]):
        print('Case in progress %s' % cs_name)
        cs = f"{config['case_studies_dir']}/{dir_name + '/' + cs_name}"
        # Update the GWP limit
        config["system_limits"]['GWP_limit'] = gwp_tot_max
        # Saving data to .dat files into the config['temp_dir'] directory
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(out_path=estd_out_path, data=all_data, system_limits=config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'],
                      step1_output_path=config["step1_output"])

        mod_fns = [f"{config['ES_path']}/ESTD_model_cost.mod"]
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, [estd_out_path, td12_out_path],
                         config['temp_dir'])
        es.draw_sankey(sankey_dir=f"{cs}/output/sankey")


config_name_file = 'config_2035_5_6_GW_nuc'  # config_2035, config_2035_2_GW_nuc, config_2035_5_6_GW_nuc

if __name__ == '__main__':

    # Get the current working directory
    cwd = os.getcwd()
    # Print the current working directory
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config_ = load_config(config_fn=config_name_file+'.yaml')

    if config_name_file == 'config_2035_2_GW_nuc':
        dir_name_ = 'einv_GWP_tot_2_GW_nuc_0'
    elif config_name_file == 'config_2035_5_6_GW_nuc':
        dir_name_ = 'einv_GWP_tot_5_6_GW_nuc_0'
    else:
        dir_name_ = 'cost_GWP_tot_0'

    ###################################################################################################################
    # 1. Run ES-TD without constrain on the GWP_tot
    ###################################################################################################################

    # Create the temp_dir if it does not exist
    make_dir(config_['temp_dir'])

    # Loading data
    all_data = es.import_data(user_data_dir=config_['user_data'], developer_data_dir=config_['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config_['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config_['Technologies']['f_min'][tech]
    # Modify the maximal capacities of some technologies
    if 'f_max' in config_['Technologies']:
        for tech in config_['Technologies']['f_max']:
            all_data['Technologies']['f_max'].loc[tech] = config_['Technologies']['f_max'][tech]

    # Saving data to .dat files into the config['temp_dir'] directory
    estd_out_path_ = f"{config_['temp_dir']}/ESTD_data.dat"
    es.print_estd(out_path=estd_out_path_, data=all_data, system_limits=config_["system_limits"])
    td12_out_path_ = f"{config_['temp_dir']}/ESTD_12TD.dat"
    # WARNING: check if STEP1 is done
    if not os.path.isfile(config_["step1_output"]):
        print('WARNING: the STEP1 that consists of generating the 12 typical days must be conducted'
              ' before to compute the TD_of_days.out file located in %s' % (config_["step1_output"]))
    es.print_12td(out_path=td12_out_path_, time_series=all_data['Time_series'],
                  step1_output_path=config_["step1_output"])

    # Running EnergyScope
    mod_fns_ = [f"{config_['ES_path']}/ESTD_model_cost.mod"]
    cs_ = f"{config_['case_studies_dir']}/{dir_name_+'/'+config_['case_study_name']}"
    es.run_step2_new(cs_, config_['AMPL_path'], config_['options'], mod_fns_, [estd_out_path_, td12_out_path_],
                     config_['temp_dir'])
    es.draw_sankey(sankey_dir=f"{cs_}/output/sankey")

    ################################################
    # Compute the EROI "final":
    # -> compute the FEC from the year_balance.csv
    # -> get the Einv
    # -> EROI "final" = Eout/Einv, with Eout = FEC
    ################################################

    # Compute the FEC from the year_balance.csv
    GWP_val = get_gwp(cs=cs_)
    cost_val = get_cost(cs=cs_) / 1000.  # bEUR/y
    df_year_balance = pd.read_csv(f"{cs_}/output/year_balance.csv", index_col=0)
    fec_details, fec_tot = compute_fec(year_balance=df_year_balance, user_data_dir=config_['user_data'])
    fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
    # Compute the FEC from SANKEY
    ef = get_fec_from_sankey(case_study_dir=cs_, col=config_['case_study_name'])
    fec_sankey = ef.sum()
    einv = get_total_einv(cs_) / 1000  # TWh
    print('FEC SANKEY %.2f vs year_balance %.2f [TWh/y]' % (fec_sankey, fec_tot_val))
    print('EROI SANKEY %.2f vs year_balance %.2f' % (fec_sankey / einv, fec_tot_val / einv))
    print('GWP_tot %.1f GWP_constr %.1f GWP_op %.1f [ktC02/y]'
          % (GWP_val.sum(), GWP_val['GWP_constr'], GWP_val['GWP_op']))
    print('C_tot %.1f C_inv %.1f C_maint %.1f C_op %.1f [bEUR/y]'
          % (cost_val.sum(), cost_val['C_inv'], cost_val['C_maint'], cost_val['C_op']))

    ###################################################################################################################
    # 2. Run ES-TD with a constrain on the GWP_tot
    ###################################################################################################################

    # -----------------------------------------------
    # Min Cost
    # s.t. GWP_tot <= p * GWP_op^i with p a percentage and GWP_op^i computed by Min Einv without constraint on GWP_tot
    # -----------------------------------------------
    # FIXME: WARNING is the case 100 is already computed, adapt the range_val to start at 95.
    gwp_op_ini_ = get_gwp(cs=f"{config_['case_studies_dir']}/{'einv_GWP_tot_0/run_100'}")['GWP_op']
    print('GWP_limit initial %.1f [MtC02/y]' % (gwp_op_ini_/1000))
    range_val_ = range(95, 0, -5)
    loop_cost_computation(range_val=range_val_, dir_name=dir_name_, gwp_op_ini=gwp_op_ini_, config=config_)
