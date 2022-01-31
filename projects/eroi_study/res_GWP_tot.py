# -*- coding: utf-8 -*-
"""
This script makes plots of relevant data.

@author: Jonathan Dumas
"""

import yaml
import os

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt

from sys import platform

from energyscope.utils import make_dir, load_config, get_FEC_from_sankey
from energyscope.postprocessing import get_total_einv
from projects.eroi_study.res_GWP_tot_vs_GWP_op import fec_plots, primary_energy_plots
from projects.eroi_study.utils_plot import plot_two_series, plot_stacked_bar, plot_one_serie
from projects.eroi_study.utils_res import compute_fec, get_gwp, compute_einv_details, compute_primary_energy, \
    eroi_computation, res_details, gwp_computation, retrieve_non_zero_val, retrieve_einv_const_by_categories, \
    res_assets_capacity

# parameters
domestic_RE_share = 0 # 0, 30 %

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config.yaml')

    # Loading data
    all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # -----------------------------------------------
    # Compare minimization of the system Einv:
    # s.t. GWP_tot <= p * GWP_op^i
    #  with p a percentage and GWP_op^i the value obtained by Min Einv without contraint on GWP_tot
    # -----------------------------------------------

    range_val = range(100, 0, -5)
    dir = f"{config['case_studies_dir']}/{'re_be_GWP_tot_' + str(domestic_RE_share)}"
    df_res, df_fec_details = eroi_computation(dir=dir, user_data=config['user_data'], range_val=range_val)
    df_Einv_op, df_Einv_RES_cat, df_Einv_TECH_cat, df_EI_cat, df_EI = res_details(range_val=range_val, all_data=all_data, dir=dir, user_data=config['user_data'])
    df_GWP = gwp_computation(dir=dir, range_val=range_val)
    df_Einv_const = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data, dir=dir, user_data=config['user_data'])
    df_assets = res_assets_capacity(range_val=range_val, dir=dir)



    ####################################################################################################################
    # Compare the case p = 100, 20, 10 and 5
    # When GWP_tot <= p * gwp_limit
    # Use fec_details DataFrame to identify the technologies that satisfy the different EDU and the FEC related
    df_year_balance_100 = pd.read_csv(dir + '/run_100/' + "/output/year_balance.csv", index_col=0)
    fec_details_100, fec_tot_100 = compute_fec(data=df_year_balance_100, user_data=config['user_data'])

    df_year_balance_10 = pd.read_csv(dir + '/run_10/' + "/output/year_balance.csv", index_col=0)
    fec_details_10, fec_tot_10 = compute_fec(data=df_year_balance_10, user_data=config['user_data'])

    df_year_balance_5 = pd.read_csv(dir + '/run_5/' + "/output/year_balance.csv", index_col=0)
    fec_details_5, fec_tot_5 = compute_fec(data=df_year_balance_5, user_data=config['user_data'])

    # Compare technologies that produce electricity between p = 5 and 10 %
    # For instance, when p = 5  -> CCGT mainly produced electricity for the case where GWP_tot is constrained
    # print(df_year_balance_10[df_year_balance_10['ELECTRICITY'] > 0]['ELECTRICITY'])
    # print(df_year_balance_5[df_year_balance_5['ELECTRICITY'] > 0]['ELECTRICITY'])

    ####################################################################################################################
    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    ####################################################################################################################
    dir_plot = 'GWP_tot_' + str(domestic_RE_share)
    make_dir(cwd+'/export/')
    make_dir(cwd+'/export/'+dir_plot+'/')
    dir_plot = cwd+'/export/GWP_tot_' + str(domestic_RE_share)
    pdf = 'gwp-tot-' + str(domestic_RE_share)

    ####################################################################################################################
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    label = r'$x^{tot}$' # x^{tot} = \frac{\text{GWP}_{tot}}{\alpha^0}


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
        plt.xlabel('GWP total [MtC02/y]', fontsize=15)
        plt.ylim(ylim[0], ylim[1])
        plt.legend(fontsize=15)
        plt.tight_layout()
        plt.savefig(pdf_name)
        plt.show()

    plot_one_serie(df_data=df_res['EROI'], label=label, pdf_name=dir_plot + '/eroi_' + str(domestic_RE_share) + '.pdf', x_index=df_GWP.sum(axis=1).values, ylim=[2.5, 10], ylabel='EROI [-]')

    ####################################################################################################################
    # FEC
    fec_plots(df_fec_data=df_fec_details, pdf=pdf, dir_plot=dir_plot)

    ####################################################################################################################
    # PRIMARY ENERGY
    # RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_data=df_EI_cat.transpose(), ylabel='(TWh)', ylim=520, pdf_name=dir_plot+'/EI-details-'+pdf+'.pdf')
    # Provides the list of resources by subcategories
    # res_2_list = list(retrieve_non_zero_val(df=df_EI_2.drop(columns=['Subcategory']).transpose()).columns)
    # df_2_res_by_subcat = res_by_sub_cat(res_list=res_2_list, res_subcat=df_EI_2['Subcategory'])

    # Primary energy plots by RES categories: RE, Non-RE
    # primary_energy_plots(df_EI_1=df_EI_1, df_EI_2=df_EI, pdf_1=pdf_1, pdf_2=pdf, dir_plot=dir_plot)

    ####################################################################################################################
    # Einv_tot = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)

    # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_data=df_Einv_RES_cat.transpose(), ylabel='(TWh)', ylim=160, pdf_name=dir_plot+'/einv-res-'+pdf+'.pdf')

    # Einv_op classed by RESOURCES
    df = retrieve_non_zero_val(df=df_Einv_op.transpose())
    plot_stacked_bar(df_data=df, ylabel='(TWh)', ylim=160, pdf_name=dir_plot+'/einv-res-details-'+pdf+'.pdf')

    # 2. Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    plot_stacked_bar(df_data=df_Einv_TECH_cat.transpose(), ylabel='(TWh)', ylim=35, pdf_name=dir_plot+'/einv-tech-'+pdf+'.pdf')