# -*- coding: utf-8 -*-
"""
This script quantifies the impact of uncertain parameters on the model output.

@author: Jonathan Dumas
"""

import yaml
import os
import logging
import shutil
import pickle
from subprocess import CalledProcessError, run
from typing import Dict, List

import amplpy
import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt

from sys import platform

from energyscope import get_total_einv
from energyscope.utils import load_config
from energyscope.step2_output_generator import extract_results_step2
from projects.eroi_study.utils_res import get_gwp, get_cost, compute_fec


ID_sample = 1  # from 1 to 5
gwp_tot_max = 85400 # ktCO2/y -> constraint on the GWP_tot, 85400, 56900, 28500, 19000

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config_uq.yaml')

    # second-order PCE extraction
    df_samples = pd.read_csv('data_samples/samples-order-2-'+ str(gwp_tot_max)+'.csv', index_col=0)
    # df_samples3 = pd.read_csv('data_samples/samples-order-3.csv', index_col=0)
    # df_samples.loc[2945] = df_samples3.loc[len(df_samples)]

    dir_name = 'einv_uq_order_2_gwp_' + str(gwp_tot_max)
    # loop on all sampled parameters to extract results from pickle files
    # for sample_i in range(0, len(df_samples)):
    for sample_i in range(2000, len(df_samples)):
        print('run %s in progress' % (sample_i))
        cs = f"{config['case_studies_dir']}/{dir_name + '/sample_' + str(sample_i)}"
        extract_results_step2(cs)

    # first-order PCE extraction
    # df_samples = pd.read_csv('data_samples/samples.csv', index_col=0)
    # M_var = len(df_samples.columns)
    # n_samples = 2 * (M_var + 1)
    #
    # for batch in [5]:
    #     dir_name = 'einv_uq_'+str(batch) + '_gwp_' + str(gwp_tot_max)
    #
    #     # loop on all sampled parameters to extract results from pickle files
    #     for sample_i in range(150, n_samples):
    #     # for sample_i in range(0, n_samples+1):
    #         print('batch %s run %s in progress' % (batch, sample_i))
    #         cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
    #         extract_results_step2(cs)


    # Compute EROI first-order PCE
    # loop on all sampled parameters to compute EROI
    # for batch in [1, 2, 3, 4, 5]:
    #     df_samples_batch = df_samples.loc[n_samples * (batch - 1):n_samples * batch - 1].copy()
    #     df_samples_batch.index = [i for i in range(n_samples)]
    #     dir_name = 'einv_uq_' + str(batch)+ '_gwp_' + str(gwp_tot_max)
    #
    #     res_list = []
    #     for sample_i in range(0, n_samples):
    #         cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
    #         # es.draw_sankey(sankey_dir=f"{cs}/output/sankey")
    #
    #         # Compute the FEC from the year_balance.csv
    #         cost_val = get_cost(cs=cs) /1000 # bEUR/y
    #         df_year_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0)
    #         fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
    #         fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
    #         einv = get_total_einv(cs) / 1000  # TWh
    #         print('batch %s run %s EROI %.2f cost %.2f [bEUR/y]' % (batch, sample_i, fec_tot_val / einv, cost_val.sum()))
    #         res_list.append([fec_tot_val / einv, cost_val.sum()])
    #     df_res = pd.DataFrame(data=np.asarray(res_list), columns=['EROI', 'cost'], index=[i for i in range(0, n_samples)])
    #     df_concat = pd.concat([df_samples_batch, df_res], axis=1).dropna()
    #     df_concat.to_csv('data_samples/res-samples-' +str(gwp_tot_max)+ '-' + str(batch) + '.csv', sep=' ', index=False)


    # # Compute EROI second-order PCE
    # dir_name = 'einv_uq_order_2_gwp_' + str(gwp_tot_max)
    # res_list = []
    # for sample_i in range(0, len(df_samples)):
    #     cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
    #     # es.draw_sankey(sankey_dir=f"{cs}/output/sankey")
    #
    #     # Compute the FEC from the year_balance.csv
    #     cost_val = get_cost(cs=cs) /1000 # bEUR/y
    #     df_year_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0)
    #     fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
    #     fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
    #     einv = get_total_einv(cs) / 1000  # TWh
    #     print('run %s EROI %.2f cost %.2f [bEUR/y]' % (sample_i, fec_tot_val / einv, cost_val.sum()))
    #     res_list.append([fec_tot_val / einv, cost_val.sum()])
    # df_res = pd.DataFrame(data=np.asarray(res_list), columns=['EROI', 'cost'], index=[i for i in range(0, len(df_samples))])
    # df_concat = pd.concat([df_samples, df_res], axis=1).dropna()
    # df_concat.to_csv('data_samples/res-samples-order-2-' +str(gwp_tot_max)+ '.csv', sep=' ', index=False)