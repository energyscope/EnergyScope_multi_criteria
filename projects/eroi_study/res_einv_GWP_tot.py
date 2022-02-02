# -*- coding: utf-8 -*-
"""
Results of system Einv_tot minimization with several scenarios computed by constraining GWP_tot with different GHG emissions targets.

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
from projects.eroi_study.res_einv_GWP_tot_vs_GWP_op import fec_plots, primary_energy_plots, \
    plot_asset_capacities_by_tech
from projects.eroi_study.utils_plot import plot_two_series, plot_stacked_bar, plot_one_serie
from projects.eroi_study.utils_res import compute_fec, get_gwp, compute_einv_details, compute_primary_energy, \
    eroi_computation, res_details, gwp_computation, retrieve_non_zero_val, retrieve_einv_const_by_categories, \
    res_assets_capacity, gwp_breakdown, gwp_const_per_category


def replace_item_in_list(l: list, item_old: str, item_new: str):
    """
    Replace a specific item into a list
    """
    for i in range(len(l)):
        if l[i] == item_old:
            l[i] = item_new
    return l

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
    plt.close()

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
    #  with p a percentage and GWP_op^i the GHG emissions target.
    # -----------------------------------------------

    range_val = range(100, 0, -5)
    dir = f"{config['case_studies_dir']}/{'einv_GWP_tot_' + str(domestic_RE_share)}"
    df_res, df_fec_details = eroi_computation(dir=dir, user_data=config['user_data'], range_val=range_val)
    df_Einv_op, df_Einv_RES_cat, df_Einv_TECH_cat, df_EI_cat, df_EI = res_details(range_val=range_val, all_data=all_data, dir=dir, user_data=config['user_data'])
    df_GWP = gwp_computation(dir=dir, range_val=range_val)
    df_Einv_const = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data, dir=dir, user_data=config['user_data'])
    df_assets = res_assets_capacity(range_val=range_val, dir=dir)
    df_gwp_const, df_gwp_op = gwp_breakdown(dir=dir, range_val=range_val)

    ######
    # Share of energies
    for p in range(100, 60, -5):
        print('GWP_tot %.1f [MtC02/y]: offshore %.1f [GW] onshore %.1f [GW] PV %.1f [GW]' %(df_GWP.sum(axis=1).loc[p], df_assets[p].loc['WIND_OFFSHORE'], df_assets[p].loc['WIND_ONSHORE'], df_assets[p].loc['PV']))
        print('Gas %.1f PV %.1f Wind %.1f wood %.1f wet biomass %.1f waste %.1f percentage of primary energy share' % (100 * df_EI[p]['GAS'] / df_EI[p].sum(), 100 * df_EI[p]['RES_SOLAR'] / df_EI[p].sum(), 100 * df_EI[p]['RES_WIND'] / df_EI[p].sum(), 100 * df_EI[p]['WOOD'] / df_EI[p].sum(), 100 * df_EI[p]['WET_BIOMASS'] / df_EI[p].sum(),  100 * df_EI[p]['WASTE'] / df_EI[p].sum()))

    ####################################################################################################################
    # Compare the case p = 100, 20, 10 and 5
    # When GWP_tot <= p * gwp_limit
    # Use fec_details DataFrame to identify the technologies that satisfy the different EDU and the FEC related
    # df_year_balance_100 = pd.read_csv(dir + '/run_100/' + "/output/year_balance.csv", index_col=0)
    # fec_details_100, fec_tot_100 = compute_fec(data=df_year_balance_100, user_data=config['user_data'])
    #
    # df_year_balance_10 = pd.read_csv(dir + '/run_10/' + "/output/year_balance.csv", index_col=0)
    # fec_details_10, fec_tot_10 = compute_fec(data=df_year_balance_10, user_data=config['user_data'])
    #
    # df_year_balance_5 = pd.read_csv(dir + '/run_5/' + "/output/year_balance.csv", index_col=0)
    # fec_details_5, fec_tot_5 = compute_fec(data=df_year_balance_5, user_data=config['user_data'])
    #
    # df_energy_stored_5 = pd.read_csv(dir + '/run_5/' + "/output/hourly_data/energy_stored.csv", index_col=0).dropna(axis=1)
    # df_energy_stored_5['GAS_STORAGE']
    #
    # df_layer_gas_5 = pd.read_csv(dir + '/run_5/' + "/output/hourly_data/layer_GAS.csv", index_col=0).dropna(axis=1)
    # df_layer_gas_5['GAS_STORAGE_Pin']

    # Compare technologies that produce electricity between p = 5 and 10 %
    # For instance, when p = 5  -> CCGT mainly produced electricity for the case where GWP_tot is constrained
    # print(df_year_balance_10[df_year_balance_10['ELECTRICITY'] > 0]['ELECTRICITY'])
    # print(df_year_balance_5[df_year_balance_5['ELECTRICITY'] > 0]['ELECTRICITY'])

    ####################################################################################################################
    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    ####################################################################################################################
    dir_plot = 'einv_GWP_tot_' + str(domestic_RE_share)
    make_dir(cwd+'/export/')
    make_dir(cwd+'/export/'+dir_plot+'/')
    dir_plot = cwd+'/export/einv_GWP_tot_' + str(domestic_RE_share)
    pdf = 'gwp-tot-' + str(domestic_RE_share)

    ####################################################################################################################
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    x_gwp_tot_index = df_GWP.sum(axis=1).values
    plot_one_serie(df_data=df_res['EROI'], label='EROI', pdf_name=dir_plot + '/eroi_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[2.5, 10], ylabel='[-]')
    plot_one_serie(df_data=df_res['FEC'], label='FEC', pdf_name=dir_plot + '/fec_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[300, 480], ylabel='[TWh/y]')
    plot_one_serie(df_data=df_res['Einv'], label='Einv', pdf_name=dir_plot + '/einv_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[30, 180], ylabel='[TWh/y]')
    plot_one_serie(df_data=df_EI.drop(columns=['Subcategory']).transpose().sum(axis=1), label='Primary energy', pdf_name=dir_plot + '/EI_tot_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[350, 550], ylabel='[TWh/y]')


    ####################################################################################################################
    # FEC
    fec_plots(df_fec_data=df_fec_details, pdf=pdf, dir_plot=dir_plot)

    ####################################################################################################################
    # PRIMARY ENERGY
    new_list = list(df_EI_cat.index)
    for item_old, item_new in zip(['Biofuel', 'Non-biomass', 'Other non-renewable', 'Fossil fuel'], ['Synthetic fuels', 'Wind+Solar', 'Waste+Methanol+Ammonia', 'Fossil fuels']):
        new_cols = replace_item_in_list(l=new_list, item_old=item_old, item_new=item_new)
    df_EI_cat.index = new_list
    df_EI_cat.columns = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_EI_cat.drop(index=['Export']).transpose(), xlabel='GWP total [MtC02/y]',  ylabel='[TWh]', ylim=600, pdf_name=dir_plot+'/EI-categories-'+pdf+'.pdf')

    # Renewable RES: biofuel + biomass + non-biomass
    RES_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS',
                     'WOOD',
                     'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    df_EI_RES_RE = retrieve_non_zero_val(df=df_EI.loc[RES_renewable].drop(columns=['Subcategory']).transpose())
    new_cols = list(df_EI_RES_RE.columns)
    for item_old, item_new in zip(['METHANOL_RE', 'GAS_RE', 'AMMONIA_RE', 'H2_RE', 'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO'], ['METHANOL_SYN', 'GAS_SYN', 'AMMONIA_SYN', 'H2_SYN', 'HYDRO', 'SOLAR', 'WIND', 'GEO']):
        new_cols = replace_item_in_list(l=new_cols, item_old=item_old, item_new=item_new)
    df_EI_RES_RE.columns = new_cols
    # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    colors = plt.cm.tab20b(np.linspace(0, 1, 10))
    df_EI_RES_RE.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_EI_RES_RE, xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=530, pdf_name=dir_plot + '/EI-RE-' + pdf + '.pdf', colors=colors)

    # Non renewable RES: Fossil fuel + Other non-renewable
    RES_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
                         'METHANOL', 'URANIUM']
    colors = plt.cm.tab20c(np.linspace(0, 1, 10))
    df_EI_RES_non_RE = retrieve_non_zero_val(df=df_EI.loc[RES_non_renewable].drop(columns=['Subcategory']).transpose())
    new_cols = list(df_EI_RES_non_RE.columns)
    new_cols = replace_item_in_list(l=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    df_EI_RES_non_RE.columns = new_cols
    df_EI_RES_non_RE.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_EI_RES_non_RE, xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=350, pdf_name=dir_plot + '/EI-non-RE-' + pdf + '.pdf', colors=colors)


    ####################################################################################################################
    # Einv_tot = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)

    # # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    # plot_stacked_bar(df_data=df_Einv_RES_cat.transpose(), ylabel='[TWh]', ylim=160, pdf_name=dir_plot+'/einv-res-'+pdf+'.pdf')
    #
    # # Einv_op classed by RESOURCES
    # df = retrieve_non_zero_val(df=df_Einv_op.transpose())
    # plot_stacked_bar(df_data=df, ylabel='[TWh]', ylim=160, pdf_name=dir_plot+'/einv-res-details-'+pdf+'.pdf')
    #
    # # 2. Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    # plot_stacked_bar(df_data=df_Einv_TECH_cat.transpose(), ylabel='[TWh]', ylim=35, pdf_name=dir_plot+'/einv-tech-'+pdf+'.pdf')

    ##############################################################################################################
    # GWP breakdown by resources and technologies
    # GHG emissions related to technologies
    df_gwp_const_filtered = retrieve_non_zero_val(df=df_gwp_const.transpose())
    gwp_const_by_tech_cat = gwp_const_per_category(df_gwp_const=df_gwp_const_filtered, user_data=config["user_data"])
    tech_list = ['Electricity', 'Heat high temperature', 'Heat low temperature centralised', 'Heat low temperature decentralised', 'Passenger public', 'Passenger private', 'Freight', 'Synthetic fuels', 'Electricity storage', 'Thermal storage', 'Other storage']

    # Aggregate GWP_const by sectors: heat, storage, mobility, and electricity
    df_gwp_const_by_cat = pd.concat([gwp_const_by_tech_cat[tech].sum(axis=1) for tech in tech_list], axis=1)
    df_gwp_const_by_cat.columns = tech_list
    df_1 = df_gwp_const_by_cat[['Heat high temperature', 'Heat low temperature centralised', 'Heat low temperature decentralised']].sum(axis=1)
    df_1.name = 'Heat'
    df_2 = df_gwp_const_by_cat[['Electricity storage', 'Thermal storage', 'Other storage']].sum(axis=1)
    df_2.name = 'Storage'
    df_3 = df_gwp_const_by_cat[['Passenger public','Passenger private', 'Freight']].sum(axis=1)
    df_3.name = 'Mobility'
    df_4 = df_gwp_const_by_cat[['Electricity', 'Synthetic fuels']]
    df_gwp_const_concat = pd.concat([df_1, df_2, df_3, df_4], axis=1)
    plot_stacked_bar(df_data=df_gwp_const_concat, xlabel='p [%]', ylabel='[MtC02/y]', ylim=9, pdf_name=dir_plot + '/gwp_const-breakdown-' + pdf + '.pdf')

    # GHG emissions breakdown by resources
    df_gwp_op_filtered = retrieve_non_zero_val(df=df_gwp_op.transpose())
    new_cols = list(df_gwp_op_filtered.columns)
    new_cols = replace_item_in_list(l=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    df_gwp_op_filtered.columns = new_cols
    plot_stacked_bar(df_data=df_gwp_op_filtered, xlabel='p [%]', ylabel='[MtC02/y]', ylim=100, pdf_name=dir_plot + '/gwp_op-breakdown-' + pdf + '.pdf')


    ####################################################################################################################
    # PLot assets installed capacities
    df_assets.columns = np.round(x_gwp_tot_index, 1)
    plot_asset_capacities_by_tech(df_assets=df_assets, pdf=pdf, user_data=config['user_data'], dir_plot=dir_plot, xlabel='[MtC02/y]')