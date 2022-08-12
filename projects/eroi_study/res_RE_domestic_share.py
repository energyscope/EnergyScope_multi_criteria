# -*- coding: utf-8 -*-
"""
This script makes plots of relevant data.

@author: Jonathan Dumas
"""

# import yaml
import os

# import pandas as pd
import energyscope as es
# import numpy as np
# import matplotlib.pyplot as plt

# from sys import platform

# from energyscope.utils import get_fec_from_sankey
from energyscope.utils import make_dir
# from energyscope.postprocessing import get_gwp, get_total_einv, compute_fec, \
#     compute_einv_details, compute_primary_energy
from projects.eroi_study.utils_plot import plot_two_series, plot_stacked_bar
from projects.eroi_study.utils_res import eroi_computation, res_details, gwp_computation
from projects.eroi_study.utils import load_config

GWP = 'GWP_op'  # 'GWP_tot', 'GWP_op'

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
    # Compare two case studies with a RE minimal share of 0% and 30%.
    # Min Einv
    # s.t. GWP_tot <= p * GWP_op^i with p a percentage and GWP_op^i the value
    # obtained by Min Einv without constraint on GWP_tot
    # -----------------------------------------------

    range_val = range(100, 5, -5)
    dir_1 = f"{config['case_studies_dir']}/{'re_be_' +  GWP + '_0'}"
    dir_2 = f"{config['case_studies_dir']}/{'re_be_' +  GWP + '_30'}"
    df_res_1, df_fec_details_1 = eroi_computation(dir_name=dir_1, user_data=config['user_data'], range_val=range_val)
    df_res_2, df_fec_details_2 = eroi_computation(dir_name=dir_2, user_data=config['user_data'], range_val=range_val)
    df_Einv_RES_cat_1, df_Einv_TECH_cat_1, df_EI_cat_1, df_EI_1 = \
        res_details(range_val=range_val, all_data=all_data, dir_name=dir_1, user_data=config['user_data'])
    df_Einv_RES_cat_2, df_Einv_TECH_cat_2, df_EI_cat_2, df_EI_2 = \
        res_details(range_val=range_val, all_data=all_data, dir_name=dir_2, user_data=config['user_data'])
    df_GWP_1 = gwp_computation(dir_name=dir_1, range_val=range_val)
    df_GWP_2 = gwp_computation(dir_name=dir_2, range_val=range_val)
    ####################################################################################################################
    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    ####################################################################################################################
    dir_plot = 'comparison_domestic_RE_' + GWP
    make_dir(cwd + '/export/')
    make_dir(cwd + '/export/' + dir_plot + '/')
    dir_plot = cwd + '/export/comparison_domestic_RE_' + GWP
    pdf_1 = '0-'+GWP
    pdf_2 = '30-'+GWP
    ####################################################################################################################
    # Plot EROI, FEC, and Einv vs p [%]
    plot_two_series(df_data_1=df_res_1['EROI'], df_data_2=df_res_2['EROI'], label_1='0%', label_2='30%',
                    pdf_name=dir_plot + '/eroi_'+GWP+'.pdf',
                    x_index=[i for i in range_val], ylim=[2, 10], ylabel='(-)')
    plot_two_series(df_data_1=df_res_1['FEC'], df_data_2=df_res_2['FEC'], label_1='0%', label_2='30%',
                    pdf_name=dir_plot + '/fec_'+GWP+'.pdf',
                    x_index=[i for i in range_val], ylim=[0, 400], ylabel='(TWh)')
    plot_two_series(df_data_1=df_res_1['Einv'], df_data_2=df_res_2['Einv'], label_1='0%', label_2='30%',
                    pdf_name=dir_plot + '/einv_'+GWP+'.pdf',
                    x_index=[i for i in range_val], ylim=[0, 120], ylabel='(TWh)')
    plot_two_series(df_data_1=df_GWP_1.sum(axis=1), df_data_2=df_GWP_2.sum(axis=1), label_1='0%', label_2='30%',
                    pdf_name=dir_plot + '/gwp_'+GWP+'.pdf',
                    x_index=[i for i in range_val], ylim=[0, 110], ylabel='(MtC02/y)')

    # FEC detailed by stacked bars
    plot_stacked_bar(df_data=df_fec_details_1.transpose(), ylabel='(TWh)', ylim=450,
                     pdf_name=dir_plot + '/fec-details-' + pdf_1 + '.pdf')
    plot_stacked_bar(df_data=df_fec_details_2.transpose(), ylabel='(TWh)', ylim=450,
                     pdf_name=dir_plot + '/fec-details-' + pdf_2 + '.pdf')

    ####################################################################################################################
    # PLOT: primary energy by subcategory
    # RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_data=df_EI_cat_1.transpose(), ylabel='(TWh)', ylim=450,
                     pdf_name=dir_plot + '/EI-details-' + pdf_1 + '.pdf')
    plot_stacked_bar(df_data=df_EI_cat_2.transpose(), ylabel='(TWh)', ylim=450,
                     pdf_name=dir_plot + '/EI-details-' + pdf_2 + '.pdf')

    # Renewable RES: biofuel + biomass + non-biomass
    RES_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD',
                     'RES_HYDRO',
                     'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    df_copy = df_EI_1.loc[RES_renewable].drop(columns=['Subcategory']).copy().transpose()
    df_copy.columns.name = ''
    plot_stacked_bar(df_data=df_copy.loc[:, (df_copy != 0).any(axis=0)], ylabel='(TWh)', ylim=450,
                     pdf_name=dir_plot + '/EI-RE-' + pdf_1 + '.pdf')

    # Non-renewable RES: Fossil fuel + Other non-renewable
    RES_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
                         'METHANOL', 'URANIUM']
    df_copy = df_EI_1.loc[RES_non_renewable].drop(columns=['Subcategory']).copy().transpose()
    df_copy.columns.name = ''
    plot_stacked_bar(df_data=df_copy.loc[:, (df_copy != 0).any(axis=0)], ylabel='(TWh)', ylim=350,
                     pdf_name=dir_plot + '/EI-non-RE-' + pdf_1 + '.pdf')

    ####################################################################################################################
    # Plot Einv breakdown by subcategories and categories of resources and technologies, respectively.
    # Einv = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)

    # 1. RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_data=df_Einv_RES_cat_1.transpose(), ylabel='(TWh)', ylim=90,
                     pdf_name=dir_plot + '/einv-res-' + pdf_1 + '.pdf')
    plot_stacked_bar(df_data=df_Einv_RES_cat_2.transpose(), ylabel='(TWh)', ylim=90,
                     pdf_name=dir_plot + '/einv-res-' + pdf_2 + '.pdf')

    # 2. TECHNOLOGIES categories: electricity, mobility, heat, ...
    # WARNING: the energy invested for technologies is 0 for the operation part
    # GWP_op
    plot_stacked_bar(df_data=df_Einv_TECH_cat_1.transpose(), ylabel='(TWh)', ylim=35,
                     pdf_name=dir_plot + '/einv-tech-' + pdf_1 + '.pdf')
    plot_stacked_bar(df_data=df_Einv_TECH_cat_2.transpose(), ylabel='(TWh)', ylim=35,
                     pdf_name=dir_plot + '/einv-tech-' + pdf_2 + '.pdf')
