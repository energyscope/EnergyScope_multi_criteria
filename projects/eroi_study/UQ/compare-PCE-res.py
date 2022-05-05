# -*- coding: utf-8 -*-
"""
Comparison of the results of the second-order PCE.
@author: Jonathan Dumas
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

gwp_tot_max = 19000 # ktCO2/y, 85400, 28500, 56900, 19000
new = True
if __name__ == '__main__':

    dir_name = 'comparison'

    # Second-order PCE results
    if new:
        path = '-new'
        eroi_mean = [8.43, 6.89, 5.63, 4.74, 4.22]
        eroi_std = [0.76, 0.67, 0.45, 0.55, 0.45]
    else:
        path = ''
        eroi_mean = [8.4, 6.81, 4.70, 4.21]
        eroi_std = [0.75, 0.51, 0.43, 0.41]

    print('CoV', 100 * np.round(np.asarray(eroi_std) / np.asarray(eroi_mean), 3))

    df_param_order_2_19000 = pd.read_csv('sobol_res_19000/full_pce_order_2_EROI_Sobol_indices'+path+'.csv', index_col=0)['Total-order Sobol indices']
    df_param_order_2_28500 = pd.read_csv('sobol_res_28500/full_pce_order_2_EROI_Sobol_indices'+path+'.csv', index_col=0)['Total-order Sobol indices']
    df_param_order_2_42700 = pd.read_csv('sobol_res_42700/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']
    df_param_order_2_56900 = pd.read_csv('sobol_res_56900/full_pce_order_2_EROI_Sobol_indices'+path+'.csv', index_col=0)['Total-order Sobol indices']
    df_param_order_2_85400 = pd.read_csv('sobol_res_85400/full_pce_order_2_EROI_Sobol_indices'+path+'.csv', index_col=0)['Total-order Sobol indices']
    # df_param_order_2_85400 = pd.read_csv('sobol_res_85400/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']

    critical_19000 =  list(df_param_order_2_19000[df_param_order_2_19000 > 1 / len(df_param_order_2_19000)].index)
    critical_28500 =  list(df_param_order_2_28500[df_param_order_2_28500 > 1 / len(df_param_order_2_28500)].index)
    critical_56900 =  list(df_param_order_2_56900[df_param_order_2_56900 > 1 / len(df_param_order_2_56900)].index)
    critical_85400 =  list(df_param_order_2_85400[df_param_order_2_85400 > 1 / len(df_param_order_2_85400)].index)

    critical_28500_top_5 =critical_28500[:5]
    critical_85400_top_5 =critical_85400[:5]

    x_index = [85.4, 56.9, 42.7, 28.5, 19]
    df_param_critical_28500_evolution = pd.DataFrame(index=critical_28500_top_5)
    df_param_critical_28500_evolution['85.4'] = np.array([0.6, 6.3, 0.0, 1.4, 5.3])
    df_param_critical_28500_evolution['56.9'] = round(100* df_param_order_2_56900.loc[critical_28500_top_5], 1).values
    df_param_critical_28500_evolution['42.7'] = round(100* df_param_order_2_42700.loc[critical_28500_top_5], 1).values
    df_param_critical_28500_evolution['28.5'] = round(100* df_param_order_2_28500.loc[critical_28500_top_5], 1).values
    df_param_critical_28500_evolution['19.0'] = round(100* df_param_order_2_19000.loc[critical_28500_top_5], 1).values

    df_param_critical_85400_evolution = pd.DataFrame(index=critical_85400_top_5)
    df_param_critical_85400_evolution['85.4'] = round(100* df_param_order_2_85400.loc[critical_85400_top_5], 1).values
    df_param_critical_85400_evolution['56.9'] = round(100* df_param_order_2_56900.loc[critical_85400_top_5], 1).values
    df_param_critical_85400_evolution['42.7'] = np.array([2.1, 0., 18.6, 6.1, 1.]) # 'einv_op-GAS' is not in the list of critical parameters for 42.7 MtC02 -> the values are retrieved mannually and 0. is assigned for 'einv_op-GAS'
    df_param_critical_85400_evolution['28.5'] = round(100* df_param_order_2_28500.loc[critical_85400_top_5], 1).values
    df_param_critical_85400_evolution['19.0'] = np.array([2., 0., 6.6, 2.1, 0.3])



    color_list = ['olive', 'orange', 'red', 'brown', 'blue']
    plt.figure()
    for param, label, c  in zip(critical_28500_top_5, [r'$e_{op}^{Gas-RE}$', r'$e_{constr}^{Elec. \ cars}$', r'$f_{max}^{NUC}$', r'${avail}^{Wood}$', r'$\%_{max}^{public \ mob}$'], color_list):
        plt.plot(x_index, df_param_critical_28500_evolution.transpose()[param].values, '-D', markersize=5, label=label, color=c)
    plt.xlabel('Yearly emissions limit [MtC02-eq./y]', fontsize=15)
    plt.ylabel('Total-order Sobol index %', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15, ncol=2)
    plt.tight_layout()
    plt.savefig(dir_name+'/critical-parameters-28500-evol'+path+'.pdf')
    plt.show()

    color_list = ['black', 'gray', 'orange', 'blue', 'green']
    plt.figure()
    for param, label, c in zip(critical_85400_top_5, [r'$e_{constr}^{NG \ cars}$', r'$e_{op}^{Gas}$', r'$e_{constr}^{Elec. cars}$', r'$\%_{max}^{public \ mob}$', r'$e_{op}^{Wet \ biomass}$'], color_list):
        plt.plot(x_index, df_param_critical_85400_evolution.transpose()[param].values, '-D', markersize=5, label=label, color=c)
    plt.xlabel('Yearly emissions limit [MtC02-eq./y]', fontsize=15)
    plt.ylabel('Total-order Sobol index %', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15, ncol=2)
    plt.tight_layout()
    plt.savefig(dir_name+'/critical-parameters-85400-evol'+path+'.pdf')
    plt.show()

    eroi_deterministic = [7.9, 6.2, 5.2, 4.4, 3.9]
    plt.figure()
    plt.plot(x_index, eroi_mean, '-D', markersize=10, label='EROI mean with uncertainties')
    plt.fill_between(x_index, np.asarray(eroi_mean) + 2 * np.asarray(eroi_std) , np.asarray(eroi_mean) - 2 * np.asarray(eroi_std) , facecolor='gray', alpha=0.5)
    plt.plot(x_index, eroi_deterministic, 'g-P', markersize=10, label='EROI with deterministic approach')
    plt.xlabel('Yearly emissions limit [MtC02-eq./y]', fontsize=15)
    plt.ylabel('System EROI [-]', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(dir_name+'/eroi-statistics'+path+'.pdf')
    plt.show()