# -*- coding: utf-8 -*-
"""
This script quantifies the impact of uncertain parameters on the model output.

@author: Jonathan Dumas
"""

import os
import shutil
import pickle

import pandas as pd

from energyscope.utils import load_config


def remove_pickle(case_study_dir: str) -> None:
    """
    Extract results.

    :param case_study_dir: path to the case study directory.
    """

    # Create AMPL environment
    # ampl_trans = amplpy.AMPL(environment=amplpy.Environment(ampl_path))

    # Create an empty variable
    empty_list = []

    # Load results
    openfile = open(f"{case_study_dir}/output/results.pickle", 'wb')
    pickle.dump(empty_list, openfile)
    openfile.close()

    openfile = open(f"{case_study_dir}/output/parameters.pickle", 'wb')
    pickle.dump(empty_list, openfile)
    openfile.close()

    openfile = open(f"{case_study_dir}/output/sets.pickle", 'wb')
    pickle.dump(empty_list, openfile)
    openfile.close()


gwp_tot_max = 100300  # ktCO2/y -> constraint on the GWP_tot


if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Clean pickle first order PCE
    # df_samples = pd.read_csv('data_samples/samples.csv', index_col=0)
    # M_var = len(df_samples.columns)
    # n_samples = 2 * (M_var + 1)
    #
    # # Load configuration into a dict
    # config = load_config(config_fn='config_uq.yaml')
    # for batch in [1, 2, 3, 4, 5]:
    #     dir_name = 'einv_uq_' + str(batch) + '_gwp_' + str(gwp_tot_max)
    #
    #     # loop on all sampled parameters to extract results from pickle files
    #     for sample_i in range(0, n_samples):
    #         # for sample_i in range(0, n_samples+1):
    #         print('batch %s run %s in progress' % (batch, sample_i))
    #         cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
    #         remove_pickle(cs)

    # Clean pickle second order PCE
    df_samples = pd.read_csv('data_samples/samples-order-2-' + str(gwp_tot_max) + '.csv', index_col=0)

    # Load configuration into a dict
    config = load_config(config_fn='config_uq.yaml')
    dir_name = 'einv_uq_order_2_gwp_' + str(gwp_tot_max)

    # loop on all sampled parameters to extract results from pickle files
    for sample_i in range(0, len(df_samples)):
        print('run %s in progress' % sample_i)
        cs = f"{config['case_studies_dir']}/{dir_name+'/sample_'+str(sample_i)}"
        remove_pickle(cs)
        if os.path.isdir(f"{cs}/output/hourly_data/"):
            shutil.rmtree(f"{cs}/output/hourly_data/")
