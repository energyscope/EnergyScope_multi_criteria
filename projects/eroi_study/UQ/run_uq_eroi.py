# -*- coding: utf-8 -*-
"""
This script quantifies the impact of uncertain parameters on the model output.

@author: Jonathan Dumas
"""

import yaml
import os

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt

from sys import platform

from energyscope import get_total_einv
from energyscope.utils import load_config
from projects.eroi_study.utils_res import get_gwp, get_cost, compute_fec

ID_sample = 1 # from 1 to 5
# sample_i = 0 # from to 0 to N
gwp_tot_max = 56900 # ktCO2/y -> constraint on the GWP_tot

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    df_eud_samples = pd.read_csv('data_uq_copy/demand-samples-' + str(ID_sample) + '.csv', index_col=0)
    df_res_samples = pd.read_csv('data_uq_copy/resources-samples-' + str(ID_sample) + '.csv', index_col=0)
    df_tech_samples = pd.read_csv('data_uq_copy/tech-samples-' + str(ID_sample) + '.csv', index_col=0)
    df_cpt_samples = pd.read_csv('data_uq_copy/cpt-samples-' + str(ID_sample) + '.csv', index_col=0)
    df_other_samples = pd.read_csv('data_uq_copy/other-samples-' + str(ID_sample) + '.csv', index_col=0)

    # loop on all sampled parameters
    for sample_i in range(2, 1+1):
        print('run %s in progress' % (sample_i))

        # Load configuration into a dict
        config = load_config(config_fn='config_uq.yaml')

        # Loading data
        all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
        # Modify the minimum capacities of some technologies
        for tech in config['Technologies']['f_min']:
            all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

        demand_keys = [key.split('-') for key in df_eud_samples.columns]
        res_keys = [key.split('-') for key in df_res_samples.columns]
        tech_keys = [key.split('-') for key in df_tech_samples.columns]
        cpt_keys = [key.split('-') for key in df_cpt_samples.columns]

        # replace the parameters values by the sampled parameters
        for key in demand_keys:
            all_data['Demand'].at[key[0], key[1]] = df_eud_samples.loc[sample_i][key[0] + '-' + key[1]]
        for key in res_keys:
            all_data['Resources'].at[key[1], key[0]] = df_res_samples.loc[sample_i][key[0] + '-' + key[1]]
        for key in tech_keys:
            all_data['Technologies'].at[key[1], key[0]] = df_tech_samples.loc[sample_i][key[0] + '-' + key[1]]
        for key in cpt_keys:
            all_data['Time_series'][key[1]] = all_data['Time_series'][key[1]] * df_cpt_samples.loc[sample_i][key[0] + '-' + key[1]] / all_data['Time_series'][key[1]].mean()
        for param in ['import_capacity', 'i_rate']:
            config['system_limits'][param] = df_other_samples.loc[sample_i]['other-'+param]
        for share_max in ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max', 'share_heat_dhn_max']:
            config['system_limits']['technologie_shares'][share_max] = df_other_samples.loc[sample_i]['other-' + share_max]
        for loss_network in ['ELECTRICITY', 'HEAT_LOW_T_DHN']:
            config['system_limits']['loss_network'][loss_network] = df_other_samples.loc[sample_i]['other-' + loss_network]

        # Set the GWP limit
        config["system_limits"]['GWP_limit'] = gwp_tot_max

        # Saving data to .dat files into the config['temp_dir'] directory
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(out_path=estd_out_path, data=all_data, system_limits=config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        # WARNING: check if STEP1 is done
        if not os.path.isfile(config["step1_output"]):
            print('WARNING: the STEP1 that consists of generating the 12 typical days must be conducted'
                  ' before to compute the TD_of_days.out file located in %s' % (config["step1_output"]))
        es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

        # Running EnergyScope
        dir_name = 'einv_uq_' + str(ID_sample)
        mod_fns = [f"{config['ES_path']}/ESTD_model.mod"]
        cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, [estd_out_path, td12_out_path], config['temp_dir'], dump_res_only=True)
        # es.draw_sankey(sankey_dir=f"{cs}/output/sankey")

        # # Compute the FEC from the year_balance.csv
        # cost_val = get_cost(cs=cs) /1000 # bEUR/y
        # df_year_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0)
        # fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
        # fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
        # einv = get_total_einv(cs) / 1000  # TWh
        # print('run %s EROI %.2f cost %.2f [bEUR/y]' % (sample_i, fec_tot_val / einv, cost_val.sum()))