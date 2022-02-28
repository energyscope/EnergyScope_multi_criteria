# -*- coding: utf-8 -*-
"""
Plot the total Sobol indices following the first-order PCE.

@author: Jonathan Dumas
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

if __name__ == '__main__':

    df_res_2 = pd.read_csv('first_order_res/full_pce_order_1_EROI_Sobol_indices-2.csv', index_col=0)['Total-order Sobol indices']
    df_res_3 = pd.read_csv('first_order_res/full_pce_order_1_EROI_Sobol_indices-3.csv', index_col=0)['Total-order Sobol indices']

    param_list = list(df_res_2.index)
    res_list = []
    for param in param_list:
        res_list.append([df_res_2.loc[param], df_res_3.loc[param]])

    df_res = pd.DataFrame(index=param_list, data=np.asarray(res_list))

    plt.figure()
    for col in df_res.columns:
        plt.plot(df_res[col].values, '.')
    plt.plot(df_res.mean(axis=1).values, 'k', label='mean')
    plt.hlines(y=1/len(param_list), xmin=0, xmax=len(param_list), colors='k', label='negligible', linestyles=':')
    plt.xlabel('parameters')
    plt.ylabel('Total-order Sobol indices')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Retrieve parameters which have at least one total Sobol indice > 1 / nb parameters
    param_sel_one =  list(df_res[df_res.max(axis=1) > 1 / len(param_list)].index)
    # Retrieve parameters which have all total Sobol indice > 1 / nb parameters
    param_sel_all =  list(df_res[df_res.min(axis=1) > 1 / len(param_list)].index)

    print('%s parameters with at least one Sobol index > 1 / nb parameters' %(len(param_sel_one)))
    print('%s parameters with allSobol indices > 1 / nb parameters' %(len(param_sel_all)))
