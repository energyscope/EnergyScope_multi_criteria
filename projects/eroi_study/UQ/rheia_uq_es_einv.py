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

batch = 3
pol_order = 1

dict_uq = {'case': 'ES_einv',
                    'pol order': pol_order,
                    'objective names': ['EROI', 'cost'],
                    'objective of interest': 'EROI',
                    'results dir': 'batch_' + str(batch),
                    'sampling method': 'SOBOL',
                    'create only samples': False,
                    'draw pdf cdf': [True, 1000],
                    }

if __name__ == '__main__':

    # If sampling only:
    # set: 'create only samples': True
    # comment the line 'draw pdf cdf': [True, 1000]

    # For extracting results:
    # set: 'create only samples': False
    # uncomment the line 'draw pdf cdf': [True, 1000000]

    rheia_uq.run_uq(dict_uq, design_space='design_space')

    my_post_process_uq = rheia_pp.PostProcessUQ(dict_uq['case'], dict_uq['pol order'])
    objective = 'EROI'
    names, sobol = my_post_process_uq.get_sobol(dict_uq['results dir'], objective)
    plt.barh(names, sobol)
    plt.show()

    loo = my_post_process_uq.get_loo(dict_uq['results dir'], objective)

    eroi_mean = my_post_process_uq.get_mean_std(dict_uq['results dir'], objective)[0]
    eroi_std = my_post_process_uq.get_mean_std(dict_uq['results dir'], objective)[1]

    x_pdf, y_pdf = my_post_process_uq.get_pdf(dict_uq['results dir'], objective)
    plt.plot(x_pdf, y_pdf,  linewidth=3)
    plt.ylim(0, 1)
    plt.vlines(x=eroi_mean, ymin=-1, ymax=1, colors='r', label='mean: %.1f'%(eroi_mean), linewidth=3)
    plt.vlines(x=6.2, ymin=-1, ymax=1, colors='g', label='deterministic: 6.2', linewidth=3)
    plt.vlines(x=eroi_mean + 2*eroi_std, ymin=-1, ymax=1, colors='k', label='mean + 2*std ', linestyles=':', linewidth=3)
    plt.vlines(x=eroi_mean - 2*eroi_std, ymin=-1, ymax=1, colors='k', label='mean - 2*std ', linestyles=':', linewidth=3)
    plt.xlabel(objective, fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.ylabel('probability density', fontsize=15)
    plt.tight_layout()
    plt.savefig(my_post_process_uq.result_path + '/' + dict_uq['results dir'] +'/eroi-pdf.pdf')
    plt.show()