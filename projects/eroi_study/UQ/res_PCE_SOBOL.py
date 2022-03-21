# -*- coding: utf-8 -*-
"""
Plot the total Sobol indices following the first-order PCE.

@author: Jonathan Dumas
"""
import json

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter, NullFormatter, ScalarFormatter
import pandas as pd
import numpy as np

if __name__ == '__main__':

    # First-order PCE results
    df_list = []
    for batch in range(1, 5+1):
        df_list.append(pd.read_csv('sobol_res/full_pce_order_1_EROI_Sobol_indices-'+str(batch)+'.csv', index_col=0)['Total-order Sobol indices'])

    param_list_order_1 = list(df_list[0].index)
    res_list = []
    for param in param_list_order_1:
        res_list.append([df.loc[param] for df in df_list])

    df_res = pd.DataFrame(index=param_list_order_1, data=np.asarray(res_list))
    df_res_reorder = df_res.reindex(axis='index', labels=list(df_res.max(axis=1).sort_values(ascending=False).index)).copy() # reorder index
    y_mean = 100 * df_res_reorder.mean(axis=1).values
    y_min = 100 * df_res_reorder.min(axis=1).values
    y_max = 100 * df_res_reorder.max(axis=1).values
    y_max_critical = y_max[y_max > 100/len(y_max)]
    y_max_negligible = y_max[y_max < 100 / len(y_max)]
    x_critical = np.arange(len(y_max_critical))
    x_negligible = np.arange(len(y_max_critical), len(y_max_critical)+len(y_max_negligible))

    plt.figure()
    # for col in df_res.columns:
    #     plt.plot(100 * df_res[col].values, '.', markersize=10, alpha=0.5)
    plt.plot(y_min, '-or', label='min')
    # plt.plot(y_max, '-^b', label='max')
    plt.plot(x_critical, y_max_critical, '-^', color='blue', label='max critical')
    plt.plot(x_negligible, y_max_negligible, '-^', color='gray', label='max negligible')
    # plt.fill_between(np.arange(len(y_mean)), y_mean + y_max, y_mean - y_min, facecolor='gray', label='-min/+max')
    plt.plot(y_mean, '*-', color='k', markersize=5, label='mean')
    plt.hlines(y=100/len(param_list_order_1), xmin=0, xmax=len(param_list_order_1), colors='k', label='negligible: 1/'+str(len(param_list_order_1)), linestyles='-', linewidth=3)
    plt.xlabel('Parameters', fontsize=15)
    plt.ylabel('%', rotation=180, fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.yscale('log')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.2f}'))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks([0.01, 0.1, 1, 10, 30])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    plt.tight_layout()
    plt.savefig('sobol_res/first-order-total-order-sobol-indices.pdf')
    plt.show()

    # Retrieve parameters which have at least one total Sobol indice > 1 / nb parameters
    param_sel_one =  list(df_res[df_res.max(axis=1) > 1 / len(param_list_order_1)].index)
    df_param_order_1_selected = df_res[df_res.max(axis=1) > 1 / len(param_list_order_1)].copy()
    # Retrieve parameters which have all total Sobol indice > 1 / nb parameters
    param_sel_all =  list(df_res[df_res.min(axis=1) > 1 / len(param_list_order_1)].index)
    # Retrieve parameters which have a mean over all Sobol indices > 1 / nb parameters
    param_sel_mean =  list(df_res[df_res.mean(axis=1) > 1 / len(param_list_order_1)].index)

    print('%s parameters with at least one Sobol index > 1 / nb parameters' %(len(param_sel_one)))
    print('%s parameters with all Sobol indices > 1 / nb parameters' %(len(param_sel_all)))
    print('%s parameters with the mean of all Sobol indices > 1 / nb parameters' %(len(param_sel_mean)))

    print(df_res.mean(axis=1).sort_values()[-len(param_sel_mean):])
    list(df_res.mean(axis=1).sort_values().index[-10:])

    # Select the parameters for the second-order PCE based on the results of the first-order PCE
    # df_design = pd.read_csv('data_samples/design_space', sep=' ', index_col=0)
    # df_stochastic = pd.read_csv('data_samples/stochastic_space', sep=' ', index_col=0)
    #
    # df_design.loc[param_sel_one].to_csv('data_samples/design_space-order-2', sep=' ')
    # df_stochastic.loc[param_sel_one].to_csv('data_samples/stochastic_space-order-2', sep=' ')
    #
    # param_list_order_1 = json.load(open('data_samples/param_list.json'))
    #
    # param_list_order_2 = dict()
    # df_param = pd.DataFrame([key.split('-') for key in param_sel_one])
    # for key in list(param_list_order_1.keys()):
    #     param_list_order_2[key] = [key +'-'+ l for l in list(df_param[1][df_param[0] == key].values)]
    #
    # json.dump(param_list_order_2, open("data_samples/param_list_order_2.json", "w"), sort_keys=True, indent=4)

    # Second-order PCE results
    df_param_order_2 = pd.read_csv('sobol_res/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']

    # Retrieve parameters from second-order PCE which have at least one total Sobol indice > 1 / nb parameters
    second_order_params =  list(df_param_order_2[df_param_order_2 > 1 / len(df_param_order_2)].index)

    plt.figure()
    # plt.plot(df_param_order_2.values, '*', markersize=10, label='Second-order PCE')
    plt.plot(range(len(df_param_order_2.values[df_param_order_2.values > 1 / len(df_param_order_2)])), 100 * df_param_order_2.values[df_param_order_2.values > 1 / len(df_param_order_2)], '*', markersize=10, label='critical')
    plt.plot(range(len(df_param_order_2.values[df_param_order_2.values > 1 / len(df_param_order_2)]), len(df_param_order_2.values[df_param_order_2.values > 1 / len(df_param_order_2)])+ len(df_param_order_2.values[df_param_order_2.values < 1 / len(param_list_order_1)])), 100 * df_param_order_2.values[df_param_order_2.values < 1 / len(param_list_order_1)], '.', markersize=10, color='grey', label='neglected')
    plt.hlines(y=100/len(df_param_order_2), xmin=0, xmax=len(df_param_order_2), colors='k', label='negligible: 1/'+str(len(df_param_order_2)), linestyles='-', linewidth=3)
    plt.xlabel('Parameters', fontsize=15)
    plt.ylabel('%', rotation=180, fontsize=15)
    plt.yscale('log')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.1f}'))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks([0.1, 1, 5, 10, 20, 30])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig('sobol_res/second-order-total-order-sobol-indices.pdf')
    plt.show()


    # Comparison between order 1 and order 2
    df_param_order_1_selected.mean(axis=1)
