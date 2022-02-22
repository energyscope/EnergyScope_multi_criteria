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

import rheia.UQ.uncertainty_quantification as rheia_uq

import multiprocessing as mp


import rheia.OPT.optimization as rheia_opt
import rheia.POST_PROCESS.post_process as rheia_pp

dict_uq_order_2 = {'case':          'H2_FUEL',
           'n jobs':                int(mp.cpu_count()/2),
           'pol order':             2,
           'objective names':       ['lcoh','mh2'],
           'objective of interest': 'lcoh',
           'draw pdf cdf':          [True, 1e5],
           'results dir':           'opt_design_tutorial'
           }


dict_uq_order_1 = {'case':          'H2_FUEL',
           'n jobs':                int(mp.cpu_count()/2),
           'pol order':             1,
           'objective names':       ['lcoh','mh2'],
           'objective of interest': 'lcoh',
           'draw pdf cdf':          [True, 1e5],
           'results dir':           'opt_design_tutorial_order_1'
           }


dict_uq_no_model = {'case':                  'NO_MODEL',
           'pol order':             1,
           'objective names':       ['output_1', 'output_2', 'output_3'],
           'objective of interest': 'output_2',
           'results dir':           'results_1',
            'sampling method':       'RANDOM',
            'create only samples': False,
           }

if __name__ == '__main__':
    dict_uq = dict_uq_no_model #, dict_uq_order_2, dict_uq_no_model
    rheia_uq.run_uq(dict_uq, design_space='design_space')
    # df_sample = pd.read_csv('/home/jdumas/PycharmProjects/EnergyScope_multi_criteria/venv/lib/python3.8/site-packages/rheia/RESULTS/NO_MODEL/UQ/results_1/samples', sep='                  ')
    #
    # for i in range(len(df_sample)):
    #     df_sample['output_1'].loc[i] = df_sample['var_1'].loc[i] + df_sample['   par_1'].loc[i]
    #     df_sample['output_2'].loc[i] = 2* df_sample['var_1'].loc[i] + df_sample['   par_1'].loc[i]
    #     df_sample['output_3'].loc[i] = 3 * df_sample['var_1'].loc[i] + df_sample['   par_1'].loc[i]

    case = 'NO_MODEL'
    pol_order = dict_uq['pol order']
    my_post_process_uq = rheia_pp.PostProcessUQ(case, pol_order)
    result_dir = dict_uq['results dir']
    objective = 'output_2'
    names, sobol = my_post_process_uq.get_sobol(result_dir, objective)
    plt.barh(names, sobol)
    plt.show()

    # loo = my_post_process_uq.get_loo(result_dir, objective)
    #
    # x_pdf, y_pdf = my_post_process_uq.get_pdf(result_dir, objective)
    # plt.plot(x_pdf, y_pdf)
    # plt.xlabel('lcoh')
    # plt.ylabel('probability density')
    # plt.show()