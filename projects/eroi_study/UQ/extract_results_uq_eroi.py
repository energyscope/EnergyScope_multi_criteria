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
from energyscope.sankey_input import generate_sankey_file
from energyscope.step2_output_generator import save_results
from energyscope.utils import load_config
from projects.eroi_study.utils_res import get_gwp, get_cost, compute_fec

def extract_result_step2(case_study_dir: str) -> None:
    """
    Extract results.

    :param case_study_dir: path to the case study directory.
    """


    # Create AMPL environment
    # ampl_trans = amplpy.AMPL(environment=amplpy.Environment(ampl_path))

    # Load results
    with open(f"{case_study_dir}/output/results.pickle", 'rb') as handle:
        results = pickle.load(handle)

    with open(f"{case_study_dir}/output/parameters.pickle", 'rb') as handle:
        parameters = pickle.load(handle)

    with open(f"{case_study_dir}/output/sets.pickle", 'rb') as handle:
        sets = pickle.load(handle)

    logging.info("Saving results")
    save_results(results, parameters, sets, f"{case_study_dir}/output/")

    logging.info("Creating Sankey diagram input file")
    generate_sankey_file(results, parameters, sets, f"{case_study_dir}/output/sankey/")

    logging.info('End of run')


ID_sample = 1  # from 1 to 5
# sample_i = 0 # from to 0 to N
gwp_tot_max = 56900  # ktCO2/y -> constraint on the GWP_tot

N_samples = 362

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config_uq.yaml')
    dir_name = 'einv_uq_' + str(ID_sample)

    # loop on all sampled parameters to extract results from pickle files
    for sample_i in range(361, 363+1):
    # for sample_i in range(0, N_samples+1):
        print('run %s in progress' % (sample_i))
        cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
        extract_result_step2(cs)

    # loop on all sampled parameters to compute EROI
    l = list(range(0, N_samples+1))
    # remove cases where problem was not solved
    if ID_sample ==1:
        for i in [42, 114, 167, 267, 271, 279, 319, 349, 352]:
            l.remove(i)
    elif ID_sample ==2:
        for i in [31, 187, 211, 251, 334, 346, 351]:
            l.remove(i)
    res_list = []
    for sample_i in l:
        cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
        # es.draw_sankey(sankey_dir=f"{cs}/output/sankey")

        # Compute the FEC from the year_balance.csv
        cost_val = get_cost(cs=cs) /1000 # bEUR/y
        df_year_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0)
        fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
        fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
        einv = get_total_einv(cs) / 1000  # TWh
        print('run %s EROI %.2f cost %.2f [bEUR/y]' % (sample_i, fec_tot_val / einv, cost_val.sum()))
        res_list.append([fec_tot_val / einv, cost_val.sum()])
    df_res = pd.DataFrame(data=np.asarray(res_list), columns=['EROI', 'cost'], index=[i for i in l])

    df_samples = pd.read_csv('data_uq_copy/all-samples-'+str(ID_sample)+'.csv', index_col=0)
    df_concat = pd.concat([df_samples, df_res], axis=1).dropna()
    df_concat.drop(['f_max-PHS'], axis=1).to_csv('data_uq_copy/res-samples-' + str(ID_sample) + '.csv', sep=' ', index=False)