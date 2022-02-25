# -*- coding: utf-8 -*-
"""
This script quantifies the impact of uncertain parameters on the model output.
To be used in RHEIA library.

@author: Jonathan Dumas
"""

import matplotlib.pyplot as plt
import pandas as pd

import rheia.UQ.uncertainty_quantification as rheia_uq
import rheia.POST_PROCESS.post_process as rheia_pp

dict_uq_no_model = {'case':         'ES_einv',
           'pol order':             1,
           'objective names':       ['EROI', 'cost'],
           'objective of interest': 'EROI',
           'results dir':           'results_1',
           'sampling method':       'SOBOL',
           'create only samples': True,
            # 'draw pdf cdf': [True, 1000],
           }

if __name__ == '__main__':

    dict_uq = dict_uq_no_model #, dict_uq_order_2, dict_uq_no_model
    rheia_uq.run_uq(dict_uq, design_space='design_space')

    case = 'ES_einv'
    pol_order = dict_uq['pol order']
    my_post_process_uq = rheia_pp.PostProcessUQ(case, pol_order)
    result_dir = dict_uq['results dir']
    objective = 'EROI'
    names, sobol = my_post_process_uq.get_sobol(result_dir, objective)
    plt.barh(names, sobol)
    plt.show()

    loo = my_post_process_uq.get_loo(result_dir, objective)

    x_pdf, y_pdf = my_post_process_uq.get_pdf(result_dir, objective)
    plt.plot(x_pdf, y_pdf)
    plt.xlabel('EROI')
    plt.ylabel('probability density')
    plt.show()