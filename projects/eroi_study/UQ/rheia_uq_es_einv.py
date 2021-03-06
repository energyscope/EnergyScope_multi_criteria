# -*- coding: utf-8 -*-
"""
This script quantifies the impact of uncertain parameters on the model output.

@author: Jonathan Dumas
"""

import matplotlib.pyplot as plt
# import pandas as pd

import rheia.UQ.uncertainty_quantification as rheia_uq
import rheia.POST_PROCESS.post_process as rheia_pp

gwp_tot = 100300  # 100300, 85400, 56900, 42700, 28500, 19000
batch = 1
pol_order = 2
# # ES_einv_order_1_56900, ES_einv_order_1_28500, ES_einv_order_2_56900, ES_einv_order_2_28500
# case = 'ES_einv_order_'+str(pol_order)+'_'+str(gwp_tot)
# ES_einv_order_1_56900, ES_einv_order_1_28500, ES_einv_order_2_56900, ES_einv_order_2_28500
case = 'ES_einv_order_'+str(pol_order)+'_'+str(gwp_tot) + '-new'

dict_uq = {'case': case,
           'pol order': pol_order,
           'objective names': ['EROI', 'cost'],
           'objective of interest': 'EROI',
           'results dir': 'batch_' + str(batch),
           'sampling method': 'SOBOL',
           'create only samples': False,
           'draw pdf cdf': [True, 100000],
           }
if __name__ == '__main__':

    # If sampling only:
    # set: 'create only samples': True
    # comment the line 'draw pdf cdf': [True, 1000]

    # For extracting results:
    # set: 'create only samples': False
    # uncomment the line 'draw pdf cdf': [True, 1000]

    rheia_uq.run_uq(dict_uq, design_space='design_space')

    my_post_process_uq = rheia_pp.PostProcessUQ(dict_uq['case'], dict_uq['pol order'])
    objective = 'EROI'
    names, sobol = my_post_process_uq.get_sobol(dict_uq['results dir'], objective)
    plt.barh(names, sobol)
    plt.show()

    loo = my_post_process_uq.get_loo(dict_uq['results dir'], objective)

    eroi_mean = my_post_process_uq.get_mean_std(dict_uq['results dir'], objective)[0]
    eroi_std = my_post_process_uq.get_mean_std(dict_uq['results dir'], objective)[1]

    if gwp_tot == 56900:
        eroi_deterministic = 6.2
    elif gwp_tot == 28500:
        eroi_deterministic = 4.4
    elif gwp_tot == 19000:
        eroi_deterministic = 3.9
    elif gwp_tot == 85400:
        eroi_deterministic = 7.9
    elif gwp_tot == 42700:
        eroi_deterministic = 5.2
    elif gwp_tot == 100300:
        eroi_deterministic = 8.9

    x_pdf, y_pdf = my_post_process_uq.get_pdf(dict_uq['results dir'], objective)
    plt.plot(x_pdf, y_pdf,  linewidth=3)
    plt.ylim(0, 1)
    plt.vlines(x=eroi_mean, ymin=-1, ymax=1, colors='r',
               label='PCE %.1f -/+ %.1f [2*std]' % (eroi_mean, 2*eroi_std), linewidth=3)
    plt.vlines(x=eroi_deterministic, ymin=-1, ymax=1, colors='g',
               label='deterministic: '+str(eroi_deterministic), linewidth=3)
    # plt.vlines(x=eroi_mean + 2*eroi_std, ymin=-1, ymax=1, colors='k',
    #            label='mean + 2*std', linestyles=':', linewidth=3)
    # plt.vlines(x=eroi_mean - 2*eroi_std, ymin=-1, ymax=1, colors='k',
    #            label='mean - 2*std', linestyles=':', linewidth=3)
    plt.xlabel(objective, fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.ylabel('probability density', fontsize=15)
    plt.tight_layout()
    plt.savefig(my_post_process_uq.result_path + '/' + dict_uq['results dir'] + '/eroi-pdf-' + str(gwp_tot) + '.pdf')
    plt.show()
