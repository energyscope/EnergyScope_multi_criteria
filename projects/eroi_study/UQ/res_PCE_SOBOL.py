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

gwp_tot_max = 100300  # ktCO2/y, 100300, 85400, 42700, 28500, 56900, 19000
new = False

if __name__ == '__main__':

    dir_name = 'sobol_res_'+str(gwp_tot_max)

    # First-order PCE results
    df_list = []
    for batch in range(1, 5+1):
        df_list.append(pd.read_csv(dir_name+'/full_pce_order_1_EROI_Sobol_indices-'+str(batch)+'.csv',
                                   index_col=0)['Total-order Sobol indices'])

    param_list_order_1 = list(df_list[0].index)
    res_list = []
    for param in param_list_order_1:
        res_list.append([df.loc[param] for df in df_list])

    df_res = pd.DataFrame(index=param_list_order_1, data=np.asarray(res_list))
    # reorder index
    df_res_reorder = df_res.reindex(axis='index',
                                    labels=list(df_res.max(axis=1).sort_values(ascending=False).index)).copy()
    y_mean = 100 * df_res_reorder.mean(axis=1).values
    y_min = 100 * df_res_reorder.min(axis=1).values
    y_max = 100 * df_res_reorder.max(axis=1).values
    y_max_critical = y_max[y_max > 100/len(y_max)]
    y_max_negligible = y_max[y_max < 100 / len(y_max)]
    x_critical = np.arange(len(y_max_critical))
    x_negligible = np.arange(len(y_max_critical), len(y_max_critical)+len(y_max_negligible))

    if gwp_tot_max == 56900:
        y_ticks = [0.01, 0.1, 100/len(param_list_order_1), 5, 10, 30]
    elif gwp_tot_max == 28500:
        y_ticks = [0.1, 100/len(param_list_order_1), 10, 80]
    elif gwp_tot_max == 19000:
        y_ticks = [0.1, 100/len(param_list_order_1), 10, 80]
    elif gwp_tot_max == 85400:
        y_ticks = [0.01, 0.1, 100/len(param_list_order_1), 5, 10, 30]
    elif gwp_tot_max == 42700:
        y_ticks = [0.01, 0.1, 100/len(param_list_order_1), 5, 10, 30]
    elif gwp_tot_max == 100300:
        y_ticks = [0.01, 0.1, 100/len(param_list_order_1), 5, 10, 50]

    plt.figure()
    # for col in df_res.columns:
    #     plt.plot(100 * df_res[col].values, '.', markersize=10, alpha=0.5)
    plt.plot(y_min, '-or', label='min')
    # plt.plot(y_max, '-^b', label='max')
    plt.plot(x_critical, y_max_critical, '-^', color='blue', label='max critical')
    plt.plot(x_negligible, y_max_negligible, '-^', color='gray', label='max negligible')
    # plt.fill_between(np.arange(len(y_mean)), y_mean + y_max, y_mean - y_min, facecolor='gray', label='-min/+max')
    plt.plot(y_mean, '*-', color='k', markersize=5, label='mean')
    plt.hlines(y=100/len(param_list_order_1), xmin=0, xmax=len(param_list_order_1), colors='k',
               label='negligible: 1/'+str(len(param_list_order_1)), linestyles='-', linewidth=3)
    plt.xlabel('Parameters', fontsize=15)
    plt.ylabel('%', rotation=180, fontsize=15)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.yscale('log')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.2f}'))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks(y_ticks)
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    plt.tight_layout()
    plt.savefig(dir_name+'/first-order-total-order-sobol-indices-'+str(gwp_tot_max)+'.pdf')
    plt.show()

    # Retrieve parameters which have at least one total Sobol index > 1 / nb parameters
    param_sel_one = list(df_res[df_res.max(axis=1) > 1 / len(param_list_order_1)].index)
    df_param_order_1_selected = df_res[df_res.max(axis=1) > 1 / len(param_list_order_1)].copy()
    # Retrieve parameters which have all total Sobol index > 1 / nb parameters
    param_sel_all = list(df_res[df_res.min(axis=1) > 1 / len(param_list_order_1)].index)
    # Retrieve parameters which have a mean over all Sobol indices > 1 / nb parameters
    param_sel_mean = list(df_res[df_res.mean(axis=1) > 1 / len(param_list_order_1)].index)

    print('%s parameters with at least one Sobol index > 1 / nb parameters' % (len(param_sel_one)))
    print('%s parameters with all Sobol indices > 1 / nb parameters' % (len(param_sel_all)))
    print('%s parameters with the mean of all Sobol indices > 1 / nb parameters' % (len(param_sel_mean)))

    # Print the first 10 critical parameters selected
    print(100*df_res[df_res.max(axis=1) > 1 / len(param_list_order_1)]
          .mean(axis=1).sort_values(ascending=False)[:10].round(3))
    list(df_res[df_res.max(axis=1) > 1 / len(param_list_order_1)].mean(axis=1).sort_values(ascending=False)[:10].index)

    # Select the parameters for the second-order PCE based on the results of the first-order PCE
    df_design = pd.read_csv('data_samples/design_space', sep=' ', index_col=0)
    df_stochastic = pd.read_csv('data_samples/stochastic_space', sep=' ', index_col=0)

    df_design.loc[param_sel_one].to_csv('data_samples/design_space-order-2-gwp-'+str(gwp_tot_max), sep=' ')
    df_stochastic.loc[param_sel_one].to_csv('data_samples/stochastic_space-order-2-gwp-'+str(gwp_tot_max), sep=' ')

    param_list_order_1 = json.load(open('data_samples/param_list.json'))

    # Build the json with the parameters short-listed for second-order PCE
    param_list_order_2 = dict()
    df_param = pd.DataFrame([key.split('-') for key in param_sel_one])
    for key in ['avail', 'c_pt', 'einv_constr', 'einv_op', 'f_max', 'other']:
        param_list_order_2[key] = [key + '-' + l for l in list(df_param[1][df_param[0] == key].values)]
    param_list_order_2['demand'] = []
    for l in param_list_order_1['demand']:
        if l in param_sel_one:
            param_list_order_2['demand'].append(l)

    # Check if the count is ok
    count_tot = 0
    for key, item in param_list_order_2.items():
        count_tot += len(item)
        print(key, len(item))
    if count_tot == len(param_sel_one):
        print('ok: count_tot %s vs len(param_sel_one) %s' % (count_tot, len(param_sel_one)))
        json.dump(param_list_order_2, open('data_samples/param_list_order_2-' + str(gwp_tot_max) + '.json', "w"),
                  sort_keys=True, indent=4)
    else:
        print('ERROR: count_tot %s vs len(param_sel_one) %s' % (count_tot, len(param_sel_one)))

    # Second-order PCE results
    if new:
        df_param_order_2 = pd.read_csv(dir_name+'/full_pce_order_2_EROI_Sobol_indices-new.csv',
                                       index_col=0)['Total-order Sobol indices']
    else:
        df_param_order_2 = pd.read_csv(dir_name+'/full_pce_order_2_EROI_Sobol_indices.csv',
                                       index_col=0)['Total-order Sobol indices']

    # Retrieve parameters from second-order PCE which have at least one total Sobol index > 1 / nb parameters
    second_order_params = list(df_param_order_2[df_param_order_2 > 1 / len(df_param_order_2)].index)
    n_second_param_critical = len(second_order_params)
    n_second_param_negligible = len(list(df_param_order_2[df_param_order_2 < 1 / len(df_param_order_2)].index))

    if gwp_tot_max == 56900:
        y_ticks = [0.1, 1, 100/55, 5, 10, 20, 30]
    elif gwp_tot_max == 28500:
        y_ticks = [0.1, 1, 100/42, 5, 10, 70]
    elif gwp_tot_max == 19000:
        y_ticks = [0.1, 1, 100/42, 5, 10, 80]
    elif gwp_tot_max == 85400:
        y_ticks = [0.01, 0.1, 100/len(param_list_order_1), 5, 10, 40]
    elif gwp_tot_max == 42700:
        y_ticks = [0.01, 0.1, 100 / len(param_list_order_1), 5, 10, 30]
    elif gwp_tot_max == 100300:
        y_ticks = [0.01, 0.1, 100/len(param_list_order_1), 5, 10, 40]

    plt.figure()
    # plt.plot(df_param_order_2.values, '*', markersize=10, label='Second-order PCE')
    plt.plot(range(0, n_second_param_critical),
             100 * df_param_order_2.values[df_param_order_2.values > 1 / len(df_param_order_2)],
             '*', markersize=10, label='critical')
    plt.plot(range(n_second_param_critical, n_second_param_critical + n_second_param_negligible),
             100 * df_param_order_2.values[df_param_order_2.values < 1 / len(df_param_order_2)],
             '.', markersize=10, color='grey', label='neglected')
    plt.hlines(y=100/len(df_param_order_2), xmin=0, xmax=len(df_param_order_2), colors='k',
               label='negligible: 1/'+str(len(df_param_order_2)), linestyles='-', linewidth=3)
    plt.xlabel('Parameters', fontsize=15)
    plt.ylabel('%', rotation=180, fontsize=15)
    plt.yscale('log')
    ax = plt.gca()
    ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.1f}'))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_yticks(y_ticks)
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(dir_name+'/second-order-total-order-sobol-indices-'+str(gwp_tot_max)+'.pdf')
    plt.show()

    print('%s critical second-order parameters' % (len(df_param_order_2[df_param_order_2 > 1 / len(df_param_order_2)])))
    print(100 * df_param_order_2[df_param_order_2 > 1 / len(df_param_order_2)].round(3))
