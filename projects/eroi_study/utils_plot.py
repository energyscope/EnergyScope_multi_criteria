# -*- coding: utf-8 -*-
"""
This script makes plots of relevant data.

@author: Jonathan Dumas
"""

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt


def plot_one_serie(df_data: pd.DataFrame, label: str, pdf_name: str, x_index: list, ylim: list, ylabel: str):
    """
    Plot one time serie: EROI, FEC, Einv, GWP, etc.
    """
    plt.figure()
    plt.plot(x_index, df_data.values, '-Dk', linewidth=3, markersize=10, label=label)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel(ylabel, fontsize=15)
    plt.xlabel('p (%)', fontsize=15)
    plt.ylim(ylim[0], ylim[1])
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(pdf_name)
    plt.show()


def plot_two_series(df_data_1: pd.DataFrame, df_data_2: pd.DataFrame, label_1: str, label_2: str, pdf_name: str,
                    x_index: list, ylim: list, ylabel: str):
    """
    Compare two time series: EROI, FEC, Einv, GWP, etc.
    """
    plt.figure()
    plt.plot(x_index, df_data_1.values, '-Dk', linewidth=3, markersize=10, label=label_1)
    plt.plot(x_index, df_data_2.values, '-Db', linewidth=3, markersize=10, label=label_2)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel(ylabel, fontsize=15)
    plt.xlabel('GWP total [MtC02/y]', fontsize=15)
    plt.ylim(ylim[0], ylim[1])
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(pdf_name)
    plt.close()


def plot_stacked_bar(df_data: pd.DataFrame, ylabel: str, ylim: float, pdf_name: str):
    """
    Stacked bar plot of a pd.DataFrame.
    :param df_data:
    :param ylabel:
    :param ylim:
    :param pdf_name:
    """
    plt.figure()
    df_data.plot(kind='bar', stacked=True)
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel(ylabel, fontsize=15)
    plt.xlabel('p (%)', fontsize=15)
    plt.ylim(0, ylim)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(pdf_name)
    plt.close()

if __name__ == '__main__':

    # Load configuration into a dict
    config = load_config(config_fn='config.yaml')

    # Loading data
    all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    GWP_tot = True
    if GWP_tot:
        dir_name = 're_be_GWP_tot'
    else:
        dir_name = 're_be_GWP_op'

    # Read case study name
    run = 'run_100'
    cs_test = f"{config['case_studies_dir']}/{dir_name + '_0/' + run}"

    # Compute the FEC from the year_balance.csv
    df_year_balance = pd.read_csv(f"{cs_test}/output/year_balance.csv", index_col=0)
    fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
    fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
    # Compute the FEC from SANKEY
    ef = get_FEC_from_sankey(case_study_dir=cs_test, col=run)
    fec_sankey = ef.sum()
    einv = get_total_einv(cs_test) / 1000  # TWh
    print('FEC SANKEY %.2f vs year_balance %.2f [TWh/y]' % (fec_sankey, fec_tot_val))
    print('EROI %.2f %.2f' % (fec_sankey / einv, fec_tot_val / einv))
    GWP_val = get_GWP(cs=cs_test)
    print('GWP_cons %.1f GWP_op %.1f [ktC02/y]' %(GWP_val['GWP_constr'], GWP_val['GWP_op']))

    # Compute Einv by ressources and technologies
    df_inv_res_by_subcat, df_inv_tech_by_cat = compute_einv_details(cs=cs_test, user_data=config['user_data'], all_data=all_data)

    # Primary Energy by subcategory
    df_primary_energy_subcat, df_primary_energy = compute_primary_energy(cs=cs_test, user_data=config['user_data'], run=run, all_data=all_data)