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
from projects.eroi_study.utils_plot import plot_data, plot_stacked_bar
from projects.eroi_study.utils_res import compute_fec, get_GWP, compute_einv_details, compute_primary_energy, \
    eroi_computation, res_details, gwp_computation

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
    # s.t. GWP_op <= p * GWP_op^i
    #  with p a percentage and GWP_op^i the value obtained by Min Einv without contraint on GWP_tot
    # -----------------------------------------------

    range_val = range(100, 5, -5)
    dir_1 = f"{config['case_studies_dir']}/{'re_be_GWP_op_' + str(domestic_RE_share)}"
    dir_2 = f"{config['case_studies_dir']}/{'re_be_GWP_tot_' + str(domestic_RE_share)}"
    df_res_1, df_fec_details_1 = eroi_computation(dir=dir_1, user_data=config['user_data'], range_val=range_val)
    df_res_2, df_fec_details_2 = eroi_computation(dir=dir_2, user_data=config['user_data'], range_val=range_val)
    df_Einv_RES_cat_1, df_Einv_TECH_cat_1, df_EI_cat_1, df_EI_1 = res_details(range_val=range_val, all_data=all_data, dir=dir_1, user_data=config['user_data'])
    df_Einv_RES_cat_2, df_Einv_TECH_cat_2, df_EI_cat_2, df_EI_2 = res_details(range_val=range_val, all_data=all_data, dir=dir_2, user_data=config['user_data'])
    df_GWP_1 = gwp_computation(dir=dir_1, range_val=range_val)
    df_GWP_2 = gwp_computation(dir=dir_2, range_val=range_val)

    ####################################################################################################################
    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    ####################################################################################################################
    dir_plot = 'comparison_GWP_' + str(domestic_RE_share)
    make_dir(cwd+'/export/')
    make_dir(cwd+'/export/'+dir_plot+'/')
    dir_plot = cwd+'/export/comparison_GWP_' + str(domestic_RE_share)
    pdf_1 = 'GWP-op-' + str(domestic_RE_share)
    pdf_2 = 'GWP-tot-' + str(domestic_RE_share)
    ####################################################################################################################
    # Plot EROI, FEC, and Einv vs p [%]
    plot_data(df_data_1=df_res_1['EROI'], df_data_2=df_res_2['EROI'], label_1='GWP_op', label_2='GWP_tot', pdf_name=dir_plot+'/eroi_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[3, 10], ylabel='(-)')
    plot_data(df_data_1=df_res_1['FEC'], df_data_2=df_res_2['FEC'], label_1='GWP_op', label_2='GWP_tot', pdf_name=dir_plot+'/fec_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[300, 400], ylabel='(TWh)')
    plot_data(df_data_1=df_res_1['Einv'], df_data_2=df_res_2['Einv'], label_1='GWP_op', label_2='GWP_tot', pdf_name=dir_plot+'/einv_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[30, 110], ylabel='(TWh)')
    plot_data(df_data_1=df_GWP_1.sum(axis=1), df_data_2=df_GWP_2.sum(axis=1), label_1='GWP_op', label_2='GWP_tot', pdf_name=dir_plot+'/gwp_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[5, 105], ylabel='(MtC02/y)')

    # FEC detailled by stacked bars
    plot_stacked_bar(df_data=df_fec_details_1.transpose(), ylabel='(TWh)', ylim=400, pdf_name=dir_plot+'/fec-details-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_fec_details_2.transpose(), ylabel='(TWh)', ylim=400, pdf_name=dir_plot+'/fec-details-'+pdf_2+'.pdf')

    heat_list = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']
    plot_stacked_bar(df_data=df_fec_details_1.loc[heat_list].transpose(), ylabel='(TWh)', ylim=150, pdf_name=dir_plot+'/fec-details-heat-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_fec_details_2.loc[heat_list].transpose(), ylabel='(TWh)', ylim=150, pdf_name=dir_plot+'/fec-details-heat-'+pdf_2+'.pdf')
    mob_list = ['MOB_PUBLIC', 'MOB_PRIVATE', 'MOB_FREIGHT_RAIL', 'MOB_FREIGHT_BOAT', 'MOB_FREIGHT_ROAD']
    plot_stacked_bar(df_data=df_fec_details_1.loc[mob_list].transpose(), ylabel='(TWh)', ylim=100, pdf_name=dir_plot+'/fec-details-mob-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_fec_details_2.loc[mob_list].transpose(), ylabel='(TWh)', ylim=100, pdf_name=dir_plot+'/fec-details-mob-'+pdf_2+'.pdf')
    non_energy_list = ['HVC', 'AMMONIA', 'METHANOL', 'ELECTRICITY']
    plot_stacked_bar(df_data=df_fec_details_1.loc[non_energy_list].transpose(), ylabel='(TWh)', ylim=200, pdf_name=dir_plot+'/fec-details-non-E-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_fec_details_2.loc[non_energy_list].transpose(), ylabel='(TWh)', ylim=200, pdf_name=dir_plot+'/fec-details-non-E-'+pdf_2+'.pdf')
    ####################################################################################################################
    # PLOT: primary energy by subcategory
    # RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_data=df_EI_cat_1.transpose(), ylabel='(TWh)', ylim=450, pdf_name=dir_plot+'/EI-details-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_EI_cat_2.transpose(), ylabel='(TWh)', ylim=450, pdf_name=dir_plot+'/EI-details-'+pdf_2+'.pdf')

    # Renewable RES: biofuel + biomass + non-biomass
    RES_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD',
                     'RES_HYDRO',
                     'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    df_copy_1 = df_EI_1.loc[RES_renewable].drop(columns=['Subcategory']).copy().transpose()
    df_copy_1.columns.name = ''
    plot_stacked_bar(df_data=df_copy_1.loc[:, (df_copy_1 != 0).any(axis=0)], ylabel='(TWh)', ylim=450, pdf_name=dir_plot+'/EI-RE-'+pdf_1+'.pdf')
    df_copy_2 = df_EI_2.loc[RES_renewable].drop(columns=['Subcategory']).copy().transpose()
    df_copy_2.columns.name = ''
    plot_stacked_bar(df_data=df_copy_2.loc[:, (df_copy_2 != 0).any(axis=0)], ylabel='(TWh)', ylim=450, pdf_name=dir_plot+'/EI-RE-'+pdf_2+'.pdf')


    # Non renewable RES: Fossil fuel + Other non-renewable
    RES_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
                         'METHANOL', 'URANIUM']
    df_copy_1 = df_EI_1.loc[RES_non_renewable].drop(columns=['Subcategory']).copy().transpose()
    df_copy_1.columns.name = ''
    plot_stacked_bar(df_data=df_copy_1.loc[:, (df_copy_1 != 0).any(axis=0)], ylabel='(TWh)', ylim=400, pdf_name=dir_plot+'/EI-non-RE-'+pdf_1+'.pdf')
    df_copy_2 = df_EI_2.loc[RES_non_renewable].drop(columns=['Subcategory']).copy().transpose()
    df_copy_2.columns.name = ''
    plot_stacked_bar(df_data=df_copy_2.loc[:, (df_copy_2 != 0).any(axis=0)], ylabel='(TWh)', ylim=400, pdf_name=dir_plot+'/EI-non-RE-'+pdf_2+'.pdf')

    ####################################################################################################################
    # Plot Einv breakdown by subcategories and categories of ressources and technologies, respectively.
    # Einv = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)

    # 1. RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_data=df_Einv_RES_cat_1.transpose(), ylabel='(TWh)', ylim=70, pdf_name=dir_plot+'/einv-res-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_Einv_RES_cat_2.transpose(), ylabel='(TWh)', ylim=70, pdf_name=dir_plot+'/einv-res-'+pdf_2+'.pdf')

    # 2. TECHNOLOGIES categories: electricity, mobility, heat, ...
    # WARNING: the energy invested for technologies is 0 for the operation part
    # GWP_op
    plot_stacked_bar(df_data=df_Einv_TECH_cat_1.transpose(), ylabel='(TWh)', ylim=35, pdf_name=dir_plot+'/einv-tech-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_Einv_TECH_cat_2.transpose(), ylabel='(TWh)', ylim=35, pdf_name=dir_plot+'/einv-tech-'+pdf_2+'.pdf')