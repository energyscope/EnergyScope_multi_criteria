# -*- coding: utf-8 -*-
"""
Comparison of the results of the second-order PCE.
@author: Jonathan Dumas
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

version = "short" # short, complete

if __name__ == '__main__':

    dir_name = 'comparison'

    if version == "short":
        # Second-order PCE results: 85400, 56900, 28500, 19000 [ktCO2/y]
        eroi_mean = [8.43, 6.89, 4.74, 4.22]
        eroi_std = [0.76, 0.67, 0.55, 0.45]
        eroi_deterministic = [7.9, 6.2, 4.4, 3.9]
        eroi_deterministic_with_2_GW_nuc = [8.1, 6.5, 4.5, 4.0]
        eroi_deterministic_with_5_6_GW_nuc = [8.6, 6.9, 4.6, 4.2]
        x_index = [85.4, 56.9, 28.5, 19]
        pdf = "short"
        df_param_order_2_19000 = pd.read_csv('sobol_res_19000/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']
        df_param_order_2_28500 = pd.read_csv('sobol_res_28500/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)[ 'Total-order Sobol indices']
        df_param_order_2_56900 = pd.read_csv('sobol_res_56900/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)[ 'Total-order Sobol indices']
        df_param_order_2_85400 = pd.read_csv('sobol_res_85400/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']
        critical_19000 = list(df_param_order_2_19000[df_param_order_2_19000 > 1 / len(df_param_order_2_19000)].index)
        critical_28500 = list(df_param_order_2_28500[df_param_order_2_28500 > 1 / len(df_param_order_2_28500)].index)
        critical_56900 = list(df_param_order_2_56900[df_param_order_2_56900 > 1 / len(df_param_order_2_56900)].index)
        critical_85400 = list(df_param_order_2_85400[df_param_order_2_85400 > 1 / len(df_param_order_2_85400)].index)

        critical_28500_top_5 = critical_28500[:5]
        critical_85400_top_5 = critical_85400[:5]

        # critical_28500_top_5: ['einv_op-GAS_RE', 'f_max-NUCLEAR', 'einv_constr-CAR_BEV', 'avail-WET_BIOMASS', 'f_max-WIND_OFFSHORE']
        df_param_critical_28500_evolution = pd.DataFrame(index=critical_28500_top_5)
        df_param_critical_28500_evolution['85.4'] = np.round(100 * np.array([0.002496, 0.0058591, 0.0632900, 0., 0.]),1)  # ['f_max-NUCLEAR', 'avail-WET_BIOMASS'] not in index"
        df_param_critical_28500_evolution['56.9'] = round(100 * df_param_order_2_56900.loc[critical_28500_top_5], 1).values
        df_param_critical_28500_evolution['28.5'] = round(100 * df_param_order_2_28500.loc[critical_28500_top_5],1).values
        df_param_critical_28500_evolution['19.0'] = round(100 * df_param_order_2_19000.loc[critical_28500_top_5], 1).values

        # critical_85400_top_5: ['einv_constr-CAR_NG', 'einv_op-GAS', 'einv_constr-CAR_BEV', 'other-share_mobility_public_max', 'einv_op-WET_BIOMASS']
        df_param_critical_85400_evolution = pd.DataFrame(index=critical_85400_top_5)
        df_param_critical_85400_evolution['85.4'] = round(100 * df_param_order_2_85400.loc[critical_85400_top_5],1).values
        df_param_critical_85400_evolution['56.9'] = round(100 * df_param_order_2_56900.loc[critical_85400_top_5], 1).values
        df_param_critical_85400_evolution['28.5'] = round(100 * df_param_order_2_28500.loc[critical_85400_top_5], 1).values
        df_param_critical_85400_evolution['19.0'] = np.round(np.array([0.0229618, 0., 0.061080, 0.0192291, 0.0083361]),  1)  # "['einv_op-GAS'] not in index"

    else:
        # Second-order PCE results: 100300, 85400, 56900, 42700, 28500, 19000 [ktCO2/y]
        eroi_mean = [8.83, 8.43, 6.89, 5.63, 4.74, 4.22]
        eroi_std = [0.86, 0.76, 0.67, 0.45, 0.55, 0.45]
        eroi_deterministic = [8.9, 7.9, 6.2, 5.2, 4.4, 3.9]
        eroi_deterministic_with_2_GW_nuc = [9.0, 8.1, 6.5, 5.4, 4.5, 4.0]
        eroi_deterministic_with_5_6_GW_nuc = [9.0, 8.6, 6.9, 5.6, 4.6, 4.2]
        x_index = [100.3, 85.4, 56.9, 42.7, 28.5, 19]
        pdf = "complete"

        df_param_order_2_19000 = pd.read_csv('sobol_res_19000/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']
        df_param_order_2_28500 = pd.read_csv('sobol_res_28500/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)[ 'Total-order Sobol indices']
        df_param_order_2_42700 = pd.read_csv('sobol_res_42700/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']
        df_param_order_2_56900 = pd.read_csv('sobol_res_56900/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)[ 'Total-order Sobol indices']
        df_param_order_2_85400 = pd.read_csv('sobol_res_85400/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']
        df_param_order_2_100300 = pd.read_csv('sobol_res_100300/full_pce_order_2_EROI_Sobol_indices.csv', index_col=0)['Total-order Sobol indices']

        critical_19000 = list(df_param_order_2_19000[df_param_order_2_19000 > 1 / len(df_param_order_2_19000)].index)
        critical_28500 = list(df_param_order_2_28500[df_param_order_2_28500 > 1 / len(df_param_order_2_28500)].index)
        critical_42700 = list(df_param_order_2_42700[df_param_order_2_42700 > 1 / len(df_param_order_2_42700)].index)
        critical_56900 = list(df_param_order_2_56900[df_param_order_2_56900 > 1 / len(df_param_order_2_56900)].index)
        critical_85400 = list(df_param_order_2_85400[df_param_order_2_85400 > 1 / len(df_param_order_2_85400)].index)
        critical_100300 =  list(df_param_order_2_100300[df_param_order_2_100300 > 1 / len(df_param_order_2_100300)].index)
        critical_28500_top_5 = critical_28500[:5]
        critical_85400_top_5 = critical_85400[:5]

        # critical_28500_top_5: ['einv_op-GAS_RE', 'f_max-NUCLEAR', 'einv_constr-CAR_BEV', 'avail-WET_BIOMASS', 'f_max-WIND_OFFSHORE']
        df_param_critical_28500_evolution = pd.DataFrame(index=critical_28500_top_5)
        df_param_critical_28500_evolution['100.3'] = np.round(100 * np.array([0.010269, 0.008092, 0.023192, 0., 0.]),  1)  # "['avail-WET_BIOMASS', 'f_max-WIND_OFFSHORE'] not in index"
        df_param_critical_28500_evolution['85.4'] = np.round(100 * np.array([0.002496, 0.0058591, 0.0632900, 0., 0.]),1)  # ['f_max-NUCLEAR', 'avail-WET_BIOMASS'] not in index"
        df_param_critical_28500_evolution['56.9'] = round(100 * df_param_order_2_56900.loc[critical_28500_top_5], 1).values
        df_param_critical_28500_evolution['42.7'] = round(100 * df_param_order_2_42700.loc[critical_28500_top_5],1).values
        df_param_critical_28500_evolution['28.5'] = round(100 * df_param_order_2_28500.loc[critical_28500_top_5],1).values
        df_param_critical_28500_evolution['19.0'] = round(100 * df_param_order_2_19000.loc[critical_28500_top_5], 1).values

        # critical_85400_top_5: ['einv_constr-CAR_NG', 'einv_op-GAS', 'einv_constr-CAR_BEV', 'other-share_mobility_public_max', 'einv_op-WET_BIOMASS']
        df_param_critical_85400_evolution = pd.DataFrame(index=critical_85400_top_5)
        df_param_critical_85400_evolution['100.3'] = np.round( 100 * np.array([0.30369, 0.50701511, 0.02319239, 0.04836335, 0.]),1)  # "['einv_op-WET_BIOMASS'] not in index"
        df_param_critical_85400_evolution['85.4'] = round(100 * df_param_order_2_85400.loc[critical_85400_top_5],1).values
        df_param_critical_85400_evolution['42.7'] = np.round(100 * np.array([0.021091, 0., 0.18600269, 0.06065117, 0.0097240]), 1)  # 'einv_op-GAS' is not in the list of critical parameters for 42.7 MtC02 -> the values are retrieved mannually and 0. is assigned for 'einv_op-GAS'
        df_param_critical_85400_evolution['56.9'] = round(100 * df_param_order_2_56900.loc[critical_85400_top_5], 1).values
        df_param_critical_85400_evolution['28.5'] = round(100 * df_param_order_2_28500.loc[critical_85400_top_5], 1).values
        df_param_critical_85400_evolution['19.0'] = np.round(np.array([0.0229618, 0., 0.061080, 0.0192291, 0.0083361]),  1)  # "['einv_op-GAS'] not in index"

    print('CoV', 100 * np.round(np.asarray(eroi_std) / np.asarray(eroi_mean), 3))

    color_list_28500 = ['olive', 'orange', 'red', 'brown', 'blue']
    plt.figure()
    for param, label, c  in zip(critical_28500_top_5, [r'$e_{op}^{Gas-RE}$', r'$e_{constr}^{Elec. \ cars}$', r'$f_{max}^{NUC}$', r'${avail}^{Wood}$', r'$\%_{max}^{public \ mob}$'], color_list_28500):
        plt.plot(x_index, df_param_critical_28500_evolution.transpose()[param].values, '-D', markersize=5, label=label, color=c)
    plt.xlabel('Yearly emissions limit [MtCO2-eq./y]', fontsize=15)
    plt.ylabel('Total-order Sobol index %', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15, ncol=2)
    plt.tight_layout()
    plt.savefig(dir_name+'/critical-parameters-28500-evol-'+pdf+'.pdf')
    plt.show()

    color_list_85400 = ['black', 'gray', 'orange', 'blue', 'green']
    plt.figure()
    for param, label, c in zip(critical_85400_top_5, [r'$e_{constr}^{NG \ cars}$', r'$e_{op}^{Gas}$', r'$e_{constr}^{Elec. cars}$', r'$\%_{max}^{public \ mob}$', r'$e_{op}^{Wet \ biomass}$'], color_list_85400):
        plt.plot(x_index, df_param_critical_85400_evolution.transpose()[param].values, '-D', markersize=5, label=label, color=c)
    plt.xlabel('Yearly emissions limit [MtCO2-eq./y]', fontsize=15)
    plt.ylabel('Total-order Sobol index %', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15, ncol=2)
    plt.tight_layout()
    plt.savefig(dir_name+'/critical-parameters-85400-evol-'+pdf+'.pdf')
    plt.show()

    plt.figure()
    plt.plot(x_index, eroi_mean, '-D', markersize=10, label='EROI [GSA]')
    plt.fill_between(x_index, np.asarray(eroi_mean) + 2 * np.asarray(eroi_std) , np.asarray(eroi_mean) - 2 * np.asarray(eroi_std) , facecolor='gray', alpha=0.5)
    plt.plot(x_index, eroi_deterministic, 'g-P', markersize=10, label='EROI [deterministic] NUC-0')
    plt.plot(x_index, eroi_deterministic_with_2_GW_nuc, 'k-s', markersize=10, label='EROI [deterministic] NUC-2')
    plt.plot(x_index, eroi_deterministic_with_5_6_GW_nuc, 'r-v', markersize=10, label='EROI [deterministic] NUC-5.6')
    plt.xlabel('Yearly emissions limit [MtCO2-eq./y]', fontsize=15)
    plt.ylabel('System EROI [-]', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.ylim(3, 10)
    plt.tight_layout()
    plt.savefig(dir_name+'/eroi-statistics-'+pdf+'.pdf')
    plt.show()