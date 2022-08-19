# -*- coding: utf-8 -*-
"""
This script makes plots of relevant data.

@author: Jonathan Dumas
"""

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt


def plot_one_serie(df: pd.DataFrame, label: str, pdf_name: str, x_index: list, ylim: list, ylabel: str,
                   yticks_val=None):
    """
    Plot one time serie: EROI, FEC, Einv, GWP, etc.
    """
    plt.figure()
    plt.plot(x_index, df.values, ':Dk', linewidth=3, markersize=10, label=label)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.yticks(yticks_val)
    plt.ylabel(ylabel, fontsize=15)
    plt.xlabel('Yearly emissions [MtCO2-eq./y]', fontsize=15)
    plt.ylim(ylim[0], ylim[1])
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(pdf_name)
    plt.close()


def plot_two_series(df_data_1: pd.DataFrame, df_data_2: pd.DataFrame, label_1: str, label_2: str, pdf_name: str,
                    x_index: list, ylim: list, ylabel: str, xlabel: str, x_index_2: list = None, fontsize: int = 15):
    """
    Compare two time series: EROI, FEC, Einv, GWP, etc.
    """
    if x_index_2 is None:
        x_index_2 = x_index

    plt.figure()
    plt.plot(x_index, df_data_1.values, ':Dk', linewidth=3, markersize=10, label=label_1)
    plt.plot(x_index_2, df_data_2.values, ':Pb', linewidth=3, markersize=10, label=label_2)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=fontsize)
    plt.yticks(fontsize=fontsize)
    plt.ylabel(ylabel, fontsize=fontsize)
    plt.xlabel(xlabel=xlabel, fontsize=fontsize)
    # plt.tick_params(top=False, bottom=False, left=False, right=False, labelleft=False, labelbottom=False)
    plt.ylim(ylim[0], ylim[1])
    plt.legend(fontsize=fontsize)
    plt.tight_layout()
    plt.savefig(pdf_name)
    plt.close()


def plot_stacked_bar(df: pd.DataFrame, xlabel: str, ylabel: str, ylim: float, pdf_name: str,
                     colors=plt.cm.tab20(np.linspace(0, 1, 10)), ncol: int = 2):
    """
    Stacked bar plot of a pd.DataFrame.
    """
    # plt.figure()
    ax = df.plot(kind='bar', stacked=True, color=colors)
    plt.xticks(fontsize=15)
    plt.xticks(labels=[t if i % 3 == 0 else '' for i, t in enumerate(df.index)], ticks=range(0, len(df.index)))
    plt.yticks(fontsize=15)
    plt.ylabel(ylabel, fontsize=15)
    plt.xlabel(xlabel, fontsize=15)
    plt.ylim(0, ylim)
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    plt.legend(fontsize=15, ncol=ncol)
    plt.tight_layout()
    plt.savefig(pdf_name)
    plt.close()


if __name__ == '__main__':

    from energyscope.utils import get_fec_from_sankey
    from projects.eroi_study.utils import load_config
    from energyscope.postprocessing import compute_fec, get_total_einv, get_gwp, \
        compute_einv_details, compute_primary_energy

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
    fec_details, fec_tot = compute_fec(year_balance=df_year_balance, user_data_dir=config['user_data'])
    fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
    # Compute the FEC from SANKEY
    ef = get_fec_from_sankey(case_study_dir=cs_test, col=run)
    fec_sankey = ef.sum()
    einv = get_total_einv(cs_test) / 1000  # TWh
    print('FEC SANKEY %.2f vs year_balance %.2f [TWh/y]' % (fec_sankey, fec_tot_val))
    print('EROI %.2f %.2f' % (fec_sankey / einv, fec_tot_val / einv))
    GWP_val = get_gwp(cs=cs_test)
    print('GWP_cons %.1f GWP_op %.1f [ktC02/y]' % (GWP_val['GWP_constr'], GWP_val['GWP_op']))

    # Compute Einv by ressources and technologies
    df_inv_res_by_subcat, df_inv_tech_by_cat = \
        compute_einv_details(cs=cs_test, user_data=config['user_data'], all_data=all_data)

    # Primary Energy by subcategory
    df_primary_energy_subcat, df_primary_energy = \
        compute_primary_energy(cs=cs_test, user_data=config['user_data'], run=run, all_data=all_data)
