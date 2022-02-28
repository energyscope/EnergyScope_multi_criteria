# -*- coding: utf-8 -*-
"""
Plot the total Sobol indices following the first-order PCE.

@author: Jonathan Dumas
"""
import json

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

if __name__ == '__main__':

    df_list = []
    for batch in range(1, 5+1):
        df_list.append(pd.read_csv('first_order_res/full_pce_order_1_EROI_Sobol_indices-'+str(batch)+'.csv', index_col=0)['Total-order Sobol indices'])

    param_list_order_1 = list(df_list[0].index)
    res_list = []
    for param in param_list_order_1:
        res_list.append([df.loc[param] for df in df_list])

    df_res = pd.DataFrame(index=param_list_order_1, data=np.asarray(res_list))

    plt.figure()
    for col in df_res.columns:
        plt.plot(df_res[col].values, '.', label='run '+str(col))
    plt.plot(df_res.mean(axis=1).values, 'k', label='mean')
    plt.hlines(y=1/len(param_list_order_1), xmin=0, xmax=len(param_list_order_1), colors='k', label='negligible', linestyles=':')
    plt.xlabel('parameters')
    plt.ylabel('Total-order Sobol indices')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Retrieve parameters which have at least one total Sobol indice > 1 / nb parameters
    param_sel_one =  list(df_res[df_res.max(axis=1) > 1 / len(param_list_order_1)].index)
    # Retrieve parameters which have all total Sobol indice > 1 / nb parameters
    param_sel_all =  list(df_res[df_res.min(axis=1) > 1 / len(param_list_order_1)].index)
    # Retrieve parameters which have a mean over all Sobol indices > 1 / nb parameters
    param_sel_mean =  list(df_res[df_res.mean(axis=1) > 1 / len(param_list_order_1)].index)

    print('%s parameters with at least one Sobol index > 1 / nb parameters' %(len(param_sel_one)))
    print('%s parameters with all Sobol indices > 1 / nb parameters' %(len(param_sel_all)))
    print('%s parameters with the mean of all Sobol indices > 1 / nb parameters' %(len(param_sel_mean)))

    print(df_res.mean(axis=1).sort_values()[-len(param_sel_mean):])
    list(df_res.mean(axis=1).sort_values().index[-10:])

    df_design = pd.read_csv('data_samples/design_space', sep=' ', index_col=0)
    df_stochastic = pd.read_csv('data_samples/stochastic_space', sep=' ', index_col=0)

    df_design.loc[param_sel_one].to_csv('data_samples/design_space-order-2', sep=' ')
    df_stochastic.loc[param_sel_one].to_csv('data_samples/stochastic_space-order-2', sep=' ')

    param_list_order_1 = json.load(open('data_samples/param_list.json'))

    param_list_order_2 = dict()
    df_param = pd.DataFrame([key.split('-') for key in param_sel_one])
    for key in list(param_list_order_1.keys()):
        param_list_order_2[key] = list(df_param[1][df_param[0] == key].values)

    json.dump(param_list_order_2, open("data_samples/param_list_order_2.json", "w"), sort_keys=True, indent=4)
