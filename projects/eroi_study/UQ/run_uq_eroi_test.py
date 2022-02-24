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

gwp_tot_max = 56900 # ktCO2/y -> constraint on the GWP_tot

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config_uq.yaml')

    df_samples = pd.read_csv('samples.csv', index_col=0)
    samples_keys = [key.split('-') for key in df_samples.columns]

    dir_name = 'einv_uq_test'
    mod_fns = [f"{config['ES_path']}/ESTD_model.mod"]

    res_list = []
    # loop on all sampled parameters
    for sample_i in range(0, 10):
    # for sample_i in range(0, N_run):
        print('run %s in progress' % (sample_i))

        # # Loading data
        # all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
        # # Modify the minimum capacities of some technologies
        # for tech in config['Technologies']['f_min']:
        #     all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]
        #
        # # replace the parameters values by the sampled parameters
        # for key in samples_keys:
        #     all_data['Technologies'].at[key[1], key[0]] = df_samples.loc[sample_i][key[0] + '-' + key[1]]
        #     # print(all_data['Technologies'].at[key[1], key[0]])
        #
        # # Set the GWP limit
        # config["system_limits"]['GWP_limit'] = gwp_tot_max
        #
        # # Saving data to .dat files into the config['temp_dir'] directory
        # estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        # es.print_estd(out_path=estd_out_path, data=all_data, system_limits=config["system_limits"])
        # td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        # # WARNING: check if STEP1 is done
        # if not os.path.isfile(config["step1_output"]):
        #     print('WARNING: the STEP1 that consists of generating the 12 typical days must be conducted'
        #           ' before to compute the TD_of_days.out file located in %s' % (config["step1_output"]))
        # es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

        # Running EnergyScope
        cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
        # es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, [estd_out_path, td12_out_path], config['temp_dir'], dump_res_only=False)
        # es.draw_sankey(sankey_dir=f"{cs}/output/sankey")

        # Compute the FEC from the year_balance.csv
        cost_val = get_cost(cs=cs) /1000 # bEUR/y
        df_year_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0)
        fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
        fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
        einv = get_total_einv(cs) / 1000  # TWh
        print('run %s EROI %.2f cost %.2f [bEUR/y]' % (sample_i, fec_tot_val / einv, cost_val.sum()))
        res_list.append([fec_tot_val / einv, cost_val.sum()])

    df = pd.DataFrame(data=np.asarray(res_list), columns=['EROI', 'cost'])
    df_res = pd.concat([df_samples, df], axis=1)
    df_res.to_csv('res-samples-test.csv', sep=' ', index=False)