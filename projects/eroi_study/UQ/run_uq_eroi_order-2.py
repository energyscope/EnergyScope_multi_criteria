# -*- coding: utf-8 -*-
"""
This script quantifies the impact of uncertain parameters on the model output.

@author: Jonathan Dumas
"""
import os
import json

import pandas as pd
import energyscope as es
# import numpy as np
# import matplotlib.pyplot as plt

from energyscope.utils import load_config

gwp_tot_max = 100300  # 100300, 85400, 56900, 42700, 28500, 19000 ktCO2/y -> constraint on the GWP_tot

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))
    dir_name = 'einv_uq_order_2_gwp_' + str(gwp_tot_max)

    # Load samples generated by RHEIA
    df_samples = pd.read_csv('data_samples/samples-order-2-' + str(gwp_tot_max) + '.csv', index_col=0)
    # df_samples3 = pd.read_csv('data_samples/samples-order-3.csv', index_col=0)
    # specific case for run 2945 where the computation reaches the timelimit with gwp_tot_max = 56900, PCE order 2
    # df_samples.loc[2945] = df_samples3.loc[len(df_samples)]
    M_var = len(df_samples.columns)
    n_samples = 2 * (M_var + 2) * (M_var + 1) / 2

    param_list = json.load(open('data_samples/param_list_order_2-'+ str(gwp_tot_max)+'.json'))

    count_tot = 0
    for key, item in param_list.items():
        count_tot += len(item)

    if M_var != count_tot:
        print('ERROR M_var %s count_tot %s' %(M_var, count_tot))
        quit()

    demand_keys = [key.split('-') for key in param_list['demand']]
    df_eud_samples = df_samples[param_list['demand']].copy()
    avail_keys = [key.split('-') for key in param_list['avail']]
    df_avail_samples = df_samples[param_list['avail']].copy()
    einv_op_keys = [key.split('-') for key in param_list['einv_op']]
    df_einv_op_samples = df_samples[param_list['einv_op']].copy()
    f_max_keys = [key.split('-') for key in param_list['f_max']]
    df_f_max_samples = df_samples[param_list['f_max']].copy()
    einv_constr_keys = [key.split('-') for key in param_list['einv_constr']]
    df_einv_constr_samples = df_samples[param_list['einv_constr']].copy()
    c_pt_keys = [key.split('-') for key in param_list['c_pt']]
    df_c_pt_samples = df_samples[param_list['c_pt']].copy()
    df_other_samples = df_samples[param_list['other']].copy()
    n_other_parameters = len(df_other_samples.columns)
    # FIXME to update for each new param_list (depending on the GWP constrain)
    if gwp_tot_max == 56900:
        other_l1 = [] # ['import_capacity', 'i_rate']
        other_l2 = ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max'] # ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max','share_heat_dhn_max']
        other_l3 = []  # ['ELECTRICITY', 'HEAT_LOW_T_DHN']
    elif gwp_tot_max == 85400:
        other_l1 = [] # ['import_capacity', 'i_rate']
        other_l2 = ['share_mobility_public_max', 'share_freight_boat_max'] # ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max','share_heat_dhn_max']
        other_l3 = ['ELECTRICITY']  # ['ELECTRICITY', 'HEAT_LOW_T_DHN']
    elif gwp_tot_max == 19000:
        other_l1 = [] # ['import_capacity', 'i_rate']
        other_l2 = ['share_mobility_public_max', 'share_heat_dhn_max'] # ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max','share_heat_dhn_max']
        other_l3 = []  # ['ELECTRICITY', 'HEAT_LOW_T_DHN']
    elif gwp_tot_max == 28500:
        other_l1 = ['import_capacity'] # ['import_capacity', 'i_rate']
        other_l2 = ['share_mobility_public_max'] # ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max','share_heat_dhn_max']
        other_l3 = ['ELECTRICITY']  # ['ELECTRICITY', 'HEAT_LOW_T_DHN']
    elif gwp_tot_max == 42700:
        other_l1 = [] # ['import_capacity', 'i_rate']
        other_l2 = ['share_mobility_public_max', 'share_freight_boat_max'] # ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max','share_heat_dhn_max']
        other_l3 = ['ELECTRICITY']  # ['ELECTRICITY', 'HEAT_LOW_T_DHN']
    elif gwp_tot_max == 100300:
        other_l1 = [] # ['import_capacity', 'i_rate']
        other_l2 = ['share_mobility_public_max', 'share_freight_boat_max'] # ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max','share_heat_dhn_max']
        other_l3 = ['ELECTRICITY']  # ['ELECTRICITY', 'HEAT_LOW_T_DHN']

    if n_other_parameters != len(other_l1) + len(other_l2) + len(other_l3):
        print('ERROR: define manually the other parameters')
        quit()

    # loop on all sampled parameters
    # for sample_i in range(1892, 2000+1):
    for sample_i in range(0, len(df_samples)):

        print('run %s in progress' % sample_i)

        # Load configuration into a dict
        config = load_config(config_fn='config_uq.yaml')
        # Set the gwp limit
        config["system_limits"]['GWP_limit'] = gwp_tot_max

        # Loading data
        all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
        # Modify the minimum capacities of some technologies
        for tech in config['Technologies']['f_min']:
            all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

        # replace the parameters values by the sampled parameters
        for key in demand_keys:
            all_data['Demand'].at[key[1], key[0]] = df_eud_samples.loc[sample_i][key[0] + '-' + key[1]]
        for key in avail_keys:
            all_data['Resources'].at[key[1], key[0]] = df_avail_samples.loc[sample_i][key[0] + '-' + key[1]]
        for key in einv_op_keys:
            all_data['Resources'].at[key[1], key[0]] = df_einv_op_samples.loc[sample_i][key[0] + '-' + key[1]]
        for key in f_max_keys:
            all_data['Technologies'].at[key[1], key[0]] = df_f_max_samples.loc[sample_i][key[0] + '-' + key[1]]
        for key in einv_constr_keys:
            all_data['Technologies'].at[key[1], key[0]] = df_einv_constr_samples.loc[sample_i][key[0] + '-' + key[1]]
        for key in c_pt_keys:
            all_data['Time_series'][key[1]] = all_data['Time_series'][key[1]] * df_c_pt_samples.loc[sample_i][
                key[0] + '-' + key[1]] / all_data['Time_series'][key[1]].mean()
        for param in other_l1:
            config['system_limits'][param] = df_other_samples.loc[sample_i]['other-' + param]
        for share_max in other_l2:
            config['system_limits']['technologie_shares'][share_max] = df_other_samples.loc[sample_i][
                'other-' + share_max]
        for loss_network in other_l3:
            config['system_limits']['loss_network'][loss_network] = df_other_samples.loc[sample_i][
                'other-' + loss_network]

        # Saving data to .dat files into the config['temp_dir'] directory
        es.print_estd(out_path=f"{config['temp_dir']}/ESTD_data.dat", data=all_data,
                      system_limits=config["system_limits"])
        es.print_12td(out_path=f"{config['temp_dir']}/ESTD_12TD.dat", time_series=all_data['Time_series'],
                      step1_output_path=config["step1_output"])

        # Running EnergyScope
        cs = f"{config['case_studies_dir']}/{dir_name + '/sample_' + str(sample_i)}"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], [f"{config['ES_path']}/ESTD_model.mod"],
                         [f"{config['temp_dir']}/ESTD_data.dat", f"{config['temp_dir']}/ESTD_12TD.dat"],
                         config['temp_dir'], dump_res_only=True)
        # es.draw_sankey(sankey_dir=f"{cs}/output/sankey")
