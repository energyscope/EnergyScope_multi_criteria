# -*- coding: utf-8 -*-
"""
Results of system Einv_tot minimization with several scenarios computed
by constraining GWP_tot with different GHG emissions targets.

@author: Jonathan Dumas
"""

# import yaml
import os

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt

# from sys import platform

# from energyscope.utils import get_fec_from_sankey
from energyscope.utils import make_dir, load_config
# from energyscope.postprocessing import get_total_einv, compute_fec, get_gwp, \
#     compute_einv_details, compute_primary_energy
from projects.eroi_study.res_einv_GWP_tot import replace_item_in_list
# from projects.eroi_study.res_einv_GWP_tot_vs_GWP_op import primary_energy_plots
from projects.eroi_study.res_einv_GWP_tot_vs_GWP_op import fec_plots, plot_asset_capacities_by_tech
# from projects.eroi_study.utils_plot import plot_two_series
from projects.eroi_study.utils_plot import plot_stacked_bar, plot_one_serie
from projects.eroi_study.utils_res import eroi_computation, res_details, gwp_computation, retrieve_non_zero_val, \
    retrieve_einv_const_by_categories, res_assets_capacity, gwp_breakdown, gwp_const_per_category, \
    cost_computation, cost_breakdown

# parameters
domestic_RE_share = 0  # 0, 30 %
config_name_file = 'config_2035'  # config_2035, config_2035_2_GW_nuc, config_2035_5_6_GW_nuc

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn=config_name_file+'.yaml')

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
    if config_name_file == 'config_2035_2_GW_nuc':
        dir_name = f"{config['case_studies_dir']}/{'cost_GWP_tot_2_GW_nuc_' + str(domestic_RE_share)}"
    elif config_name_file == 'config_2035_5_6_GW_nuc':
        dir_name = f"{config['case_studies_dir']}/{'cost_GWP_tot_5_6_GW_nuc_' + str(domestic_RE_share)}"
    else:
        dir_name = f"{config['case_studies_dir']}/{'cost_GWP_tot_' + str(domestic_RE_share)}"

    df_res, df_fec_details = eroi_computation(dir_name=dir_name, user_data=config['user_data'], range_val=range_val)
    df_Einv_op, df_Einv_RES_cat, df_Einv_TECH_cat, df_EI_cat, df_EI = \
        res_details(range_val=range_val, all_data=all_data, dir_name=dir_name, user_data=config['user_data'])
    df_GWP = gwp_computation(dir_name=dir_name, range_val=range_val)
    df_cost = cost_computation(dir_name=dir_name, range_val=range_val)
    Einv_const_dict = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data,
                                                        dir_name=dir_name, user_data=config['user_data'])
    df_assets = res_assets_capacity(range_val=range_val, dir_name=dir_name)
    df_gwp_const, df_gwp_op = gwp_breakdown(dir_name=dir_name, range_val=range_val)
    df_cost_inv, df_cost_maint, df_cost_op = cost_breakdown(dir_name=dir_name, range_val=range_val)

    ######
    # Share of energies
    for p in range(100, 0, -5):
        tot_EI = df_EI[p].sum()
        print('GWP_tot %.1f [MtCO2-eq./y]: EROI %.1f offshore %.1f [GW] onshore %.1f [GW] PV %.1f [GW] NUC %.1f [GW]'
              % (df_GWP.sum(axis=1).loc[p], df_res['EROI'].loc[p], df_assets[p].loc['WIND_OFFSHORE'],
                 df_assets[p].loc['WIND_ONSHORE'], df_assets[p].loc['PV'], df_assets[p]['NUCLEAR']))
        print('GWh: Gas %.1f METHANOL_RE %.1f AMMONIA_RE %.1f H2_RE %.1f '
              'Gas-re %.1f PV %.1f Wind %.1f wood %.1f wet biomass %.1f waste %.1f'
              % (df_EI[p]['GAS'],  df_EI[p]['METHANOL_RE'],  df_EI[p]['AMMONIA_RE'],  df_EI[p]['H2_RE'],
                 df_EI[p]['GAS_RE'],  df_EI[p]['RES_SOLAR'],  df_EI[p]['RES_WIND'],  df_EI[p]['WOOD'],
                 df_EI[p]['WET_BIOMASS'],   df_EI[p]['WASTE']))
        print('Percentage: Gas %.1f METHANOL_RE %.1f AMMONIA_RE %.1f H2_RE %.1f '
              'Gas-re %.1f PV %.1f Wind %.1f wood %.1f wet biomass %.1f waste %.1f'
              % (100 * df_EI[p]['GAS'] / tot_EI, 100 * df_EI[p]['METHANOL_RE'] / tot_EI,
                 100 * df_EI[p]['AMMONIA_RE'] / tot_EI, 100 * df_EI[p]['H2_RE'] / tot_EI,
                 100 * df_EI[p]['GAS_RE'] / tot_EI, 100 * df_EI[p]['RES_SOLAR'] / tot_EI,
                 100 * df_EI[p]['RES_WIND'] / tot_EI, 100 * df_EI[p]['WOOD'] / tot_EI,
                 100 * df_EI[p]['WET_BIOMASS'] / tot_EI,  100 * df_EI[p]['WASTE'] / tot_EI))

    ####################################################################################################################
    # Compare the case p = 100, 20, 10 and 5
    # When GWP_tot <= p * gwp_limit
    # Use fec_details DataFrame to identify the technologies that satisfy the different EDU and the FEC related
    # df_year_balance_100 = pd.read_csv(dir_name + '/run_100/' + "/output/year_balance.csv", index_col=0)
    # fec_details_100, fec_tot_100 = compute_fec(data=df_year_balance_100, user_data=config['user_data'])
    #
    # df_year_balance_10 = pd.read_csv(dir_name + '/run_10/' + "/output/year_balance.csv", index_col=0)
    # fec_details_10, fec_tot_10 = compute_fec(data=df_year_balance_10, user_data=config['user_data'])
    #
    # df_year_balance_5 = pd.read_csv(dir_name + '/run_5/' + "/output/year_balance.csv", index_col=0)
    # fec_details_5, fec_tot_5 = compute_fec(data=df_year_balance_5, user_data=config['user_data'])
    #
    # df_energy_stored_50 = pd.read_csv(dir_name + '/run_50/' + "/output/hourly_data/energy_stored.csv",
    #                                   index_col=0).dropna(axis=1)
    # df_layer_elec_50 = pd.read_csv(dir_name + '/run_50/' + "/output/hourly_data/layer_ELECTRICITY.csv",
    #                                index_col=0).dropna(axis=1)
    # df_layer_HEAT_LOW_T_DECEN_50 = pd.read_csv(dir_name+'/run_50/'+"/output/hourly_data/layer_HEAT_LOW_T_DECEN.csv",
    #                                            index_col=0).dropna(axis=1)
    # df_layer_HEAT_LOW_T_DHN_50 = pd.read_csv(dir_name + '/run_50/' + "/output/hourly_data/layer_HEAT_LOW_T_DHN.csv",
    #                                          index_col=0).dropna(axis=1)

    #
    # df_layer_gas_5 = pd.read_csv(dir_name+'/run_5/'+"/output/hourly_data/layer_GAS.csv", index_col=0).dropna(axis=1)
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
    
    if config_name_file == 'config_2035_2_GW_nuc':
        dir_plot = 'cost_GWP_tot_2_GW_nuc_' + str(domestic_RE_share)
    elif config_name_file == 'config_2035_5_6_GW_nuc':
        dir_plot = 'cost_GWP_tot_5_6_GW_nuc_' + str(domestic_RE_share)
    else:
        dir_plot = 'cost_GWP_tot_' + str(domestic_RE_share)

    make_dir(cwd+'/export/')
    make_dir(cwd+'/export/'+dir_plot+'/')
    if config_name_file == 'config_2035_2_GW_nuc':
        dir_plot = cwd + '/export/cost_GWP_tot_2_GW_nuc_' + str(domestic_RE_share)
    elif config_name_file == 'config_2035_5_6_GW_nuc':
        dir_plot = cwd + '/export/cost_GWP_tot_5_6_GW_nuc_' + str(domestic_RE_share)
    else:
        dir_plot = cwd + '/export/cost_GWP_tot_' + str(domestic_RE_share)
    pdf = 'cost-' + str(domestic_RE_share)

    ####################################################################################################################
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    x_gwp_tot_index = df_GWP.sum(axis=1).values
    plot_one_serie(df_data=df_cost.sum(axis=1), label='Cost',
                   pdf_name=dir_plot + '/cost_' + str(domestic_RE_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[40, 65], ylabel='[bEUR/y]')
    plot_one_serie(df_data=df_res['EROI'], label='EROI',
                   pdf_name=dir_plot + '/eroi_custom_' + str(domestic_RE_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[1, 10], ylabel='[-]', yticks_val=[3, 5, 7, 9])
    plot_one_serie(df_data=df_res['EROI'], label='EROI',
                   pdf_name=dir_plot + '/eroi_' + str(domestic_RE_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[1, 10], ylabel='[-]')
    plot_one_serie(df_data=df_res['FEC'], label='FEC',
                   pdf_name=dir_plot + '/fec_' + str(domestic_RE_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[300, 480], ylabel='[TWh/y]')
    plot_one_serie(df_data=df_res['Einv'], label='Einv',
                   pdf_name=dir_plot + '/einv_' + str(domestic_RE_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[30, 180], ylabel='[TWh/y]')
    plot_one_serie(df_data=df_EI.drop(columns=['Subcategory']).transpose().sum(axis=1), label='Primary energy',
                   pdf_name=dir_plot + '/EI_tot_' + str(domestic_RE_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[350, 550], ylabel='[TWh/y]')

    ####################################################################################################################
    # FEC
    fec_plots(df_fec_data=df_fec_details, pdf=pdf, dir_plot=dir_plot)

    ####################################################################################################################
    # PRIMARY ENERGY
    new_list = list(df_EI_cat.index)
    for item_old, item_new in zip(['Biofuel', 'Non-biomass', 'Other non-renewable', 'Fossil fuel'],
                                  ['Synthetic fuels', 'Wind+Solar', 'Waste+Methanol+Ammonia', 'Fossil fuels']):
        new_cols = replace_item_in_list(l=new_list, item_old=item_old, item_new=item_new)
    df_EI_cat.index = new_list
    df_EI_cat.columns = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_EI_cat.drop(index=['Export']).transpose(),
                     xlabel='Yearly emissions limit [MtCO2-eq./y]',  ylabel='Primary energy [TWh]',
                     ylim=600, pdf_name=dir_plot+'/EI-categories-'+pdf+'.pdf')

    # Renewable RES: biofuel + biomass + non-biomass
    RES_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD',
                     'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    df_EI_RES_RE = retrieve_non_zero_val(df=df_EI.loc[RES_renewable].drop(columns=['Subcategory']).transpose())
    new_cols = list(df_EI_RES_RE.columns)
    for item_old, item_new in zip(['BIODIESEL', 'WET_BIOMASS', 'WOOD', 'METHANOL_RE', 'GAS_RE', 'AMMONIA_RE', 'H2_RE',
                                   'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO'],
                                  ['Biodiesel', 'Wet biomass', 'Wood', 'Methanol-RE', 'Gas-RE', 'Ammonia-RE', 'H2-RE',
                                   'Hydro', 'Solar', 'Wind', 'Geo']):
        new_cols = replace_item_in_list(l=new_cols, item_old=item_old, item_new=item_new)
    df_EI_RES_RE.columns = new_cols
    # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    colors = plt.cm.tab20b(np.linspace(0, 1, 10))
    df_EI_RES_RE.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_EI_RES_RE[['Ammonia-RE', 'Methanol-RE', 'Gas-RE', 'Wet biomass', 'Wood', 'Hydro',
                                           'Solar', 'Wind', 'H2-RE', 'Biodiesel']],
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]',
                     ylim=530, pdf_name=dir_plot + '/EI-RE-' + pdf + '.pdf', colors=colors)

    # Non-renewable RES: Fossil fuel + Other non-renewable
    RES_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
                         'METHANOL', 'URANIUM']
    colors = plt.cm.tab20c(np.linspace(0, 1, 10))
    df_EI_RES_non_RE = retrieve_non_zero_val(df=df_EI.loc[RES_non_renewable].drop(columns=['Subcategory']).transpose())
    new_cols = list(df_EI_RES_non_RE.columns)
    for item_old, item_new in zip(['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
                                   'METHANOL', 'URANIUM'],
                                  ['LFO', 'DIESEL', 'Coal', 'GASOLINE', 'NG', 'Elec. import', 'Ammonia', 'H2', 'Waste',
                                   'Methanol', 'URANIUM']):
        new_cols = replace_item_in_list(l=new_cols, item_old=item_old, item_new=item_new)
    # new_cols = replace_item_in_list(l=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    df_EI_RES_non_RE.columns = new_cols
    df_EI_RES_non_RE.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_EI_RES_non_RE[['NG', 'Elec. import', 'Ammonia', 'Waste', 'LFO', 'Coal']],
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]', ylim=350,
                     pdf_name=dir_plot + '/EI-non-RE-' + pdf + '.pdf', colors=colors)

    ####################################################################################################################
    # Einv_tot = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)

    # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel,
    # Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    df_Einv_RES_cat.columns = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_Einv_RES_cat.transpose(), xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=160,
                     pdf_name=dir_plot+'/einv-res-'+pdf+'.pdf')

    # Einv_op classed by RESOURCES (RE and non-RE)
    df_einv_op_filtered = retrieve_non_zero_val(df=df_Einv_op.transpose())
    df_einv_op_filtered.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_einv_op_filtered, xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=160,
                     pdf_name=dir_plot+'/einv-op-details-'+pdf+'.pdf')

    # Einv_op by RE-RESOURCES
    df_einv_op_RE_filtered = retrieve_non_zero_val(df=df_Einv_op.loc[RES_renewable].transpose())
    df_einv_op_RE_filtered.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_einv_op_RE_filtered, xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=160,
                     pdf_name=dir_plot+'/einv-op-re-res-'+pdf+'.pdf')

    # Einv_op by NON-RE-RESOURCES
    df_einv_op_non_RE_filtered = retrieve_non_zero_val(df=df_Einv_op.loc[RES_non_renewable].transpose())
    df_einv_op_non_RE_filtered.index = np.round(x_gwp_tot_index, 1)
    new_cols = list(df_einv_op_non_RE_filtered.columns)
    new_cols = replace_item_in_list(l=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    df_einv_op_non_RE_filtered.columns = new_cols
    plot_stacked_bar(df_data=df_einv_op_non_RE_filtered, xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=30,
                     pdf_name=dir_plot+'/einv-op-non-re-res-'+pdf+'.pdf')

    # 2. Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    df_Einv_TECH_cat.columns = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_Einv_TECH_cat.drop(index=['Infrastructure']).transpose(),
                     xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=35,
                     pdf_name=dir_plot+'/einv-tech-'+pdf+'.pdf')

    # Einv_const classed by categories of technologies: 'Electricity', 'Heat', 'Mobility',
    # 'Infrastructure', 'Synthetic fuels', 'Storage'
    Einv_const_dict['Electricity'].index = np.round(x_gwp_tot_index, 1)
    ymax = Einv_const_dict['Electricity'].sum(axis=1).max() * 1.05
    elec_tech = list(Einv_const_dict['Electricity'].max(axis=0)[Einv_const_dict['Electricity'].max(axis=0) > 0.1].index)
    plot_stacked_bar(df_data=Einv_const_dict['Electricity'][elec_tech],
                     xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=ymax,
                     pdf_name=dir_plot+'/einv_const-elec-'+pdf+'.pdf')

    Einv_const_dict['Mobility'].index = np.round(x_gwp_tot_index, 1)
    ymax = Einv_const_dict['Mobility'].sum(axis=1).max() * 1.05
    # select only the mobility technologies with Einv_const > 0.5 GWh/y
    mobility_tech = list(Einv_const_dict['Mobility'].max(axis=0)[Einv_const_dict['Mobility'].max(axis=0) > 0.5].index)
    plot_stacked_bar(df_data=Einv_const_dict['Mobility'][mobility_tech],
                     xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=ymax,
                     pdf_name=dir_plot+'/einv_const-mob-'+pdf+'.pdf')

    ##############################################################################################################
    # GWP breakdown by resources and technologies
    # GHG emissions related to technologies
    df_gwp_const_filtered = retrieve_non_zero_val(df=df_gwp_const.transpose())
    gwp_const_by_tech_cat = gwp_const_per_category(df_gwp_const=df_gwp_const_filtered, user_data=config["user_data"])
    tech_list = ['Electricity', 'Heat high temperature', 'Heat low temperature centralised',
                 'Heat low temperature decentralised', 'Passenger public', 'Passenger private', 'Freight',
                 'Synthetic fuels', 'Electricity storage', 'Thermal storage', 'Other storage']

    # Aggregate GWP_const by sectors: heat, storage, mobility, and electricity
    df_gwp_const_by_cat = pd.concat([gwp_const_by_tech_cat[tech].sum(axis=1) for tech in tech_list], axis=1)
    df_gwp_const_by_cat.columns = tech_list
    df_1 = df_gwp_const_by_cat[
        ['Heat high temperature', 'Heat low temperature centralised', 'Heat low temperature decentralised']].sum(axis=1)
    df_1.name = 'Heat'
    df_2 = df_gwp_const_by_cat[['Electricity storage', 'Thermal storage', 'Other storage']].sum(axis=1)
    df_2.name = 'Storage'
    df_3 = df_gwp_const_by_cat[['Passenger public', 'Passenger private', 'Freight']].sum(axis=1)
    df_3.name = 'Mobility'
    df_4 = df_gwp_const_by_cat[['Electricity', 'Synthetic fuels']]
    df_gwp_const_concat = pd.concat([df_1, df_2, df_3, df_4], axis=1)
    plot_stacked_bar(df_data=df_gwp_const_concat, xlabel='p [%]', ylabel='[MtCO2-eq./y]', ylim=9,
                     pdf_name=dir_plot + '/gwp_const-breakdown-' + pdf + '.pdf')

    # GHG emissions breakdown by resources
    df_gwp_op_filtered = retrieve_non_zero_val(df=df_gwp_op.transpose())
    new_cols = list(df_gwp_op_filtered.columns)
    new_cols = replace_item_in_list(l=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    df_gwp_op_filtered.columns = new_cols
    plot_stacked_bar(df_data=df_gwp_op_filtered, xlabel='p [%]', ylabel='[MtCO2-eq./y]', ylim=100,
                     pdf_name=dir_plot + '/gwp_op-breakdown-' + pdf + '.pdf')

    ##############################################################################################################
    # Cost breakdown by resources and technologies
    df_cost_inv_filtered = retrieve_non_zero_val(df=df_cost_inv.transpose())
    df_cost_maint_filtered = retrieve_non_zero_val(df=df_cost_maint.transpose())
    df_cost_op_filtered = retrieve_non_zero_val(df=df_cost_op.transpose())

    # Retrieve the list of technologies
    df_aux_tech = pd.read_csv(config['user_data'] + "/aux_technologies.csv", index_col=0)

    # Retrieve the list subcategory of technologies
    tech_subcategory_list = list(dict.fromkeys(list(df_aux_tech['Subcategory'])))
    tech_by_subcategory = dict()
    for cat in tech_subcategory_list:
        tech_by_subcategory[cat] = list(df_aux_tech[df_aux_tech['Subcategory'] == cat].index)

    concat_list = []
    for cat in tech_by_subcategory.keys():
        concat_list.append(df_cost_inv_filtered[[i for i in df_cost_inv_filtered.columns
                                                 if i in tech_by_subcategory[cat]]].sum(axis=1))
    df_cost_inv_by_cat = pd.concat(concat_list, axis=1)
    df_cost_inv_by_cat.columns = tech_by_subcategory.keys()

    plot_stacked_bar(df_data=df_cost_inv_filtered[[i for i in df_cost_inv_filtered.columns
                                                   if i in tech_by_subcategory['Electricity']]],
                     xlabel='p [%]', ylabel='[bEUR/y]', ylim=30,
                     pdf_name=dir_plot + '/cost-inv-elec-breakdown-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_cost_inv_filtered[[i for i in df_cost_inv_filtered.columns
                                                   if i in tech_by_subcategory['Passenger private']]],
                     xlabel='p [%]', ylabel='[bEUR/y]', ylim=30,
                     pdf_name=dir_plot + '/cost-inv-private-mob-breakdown-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_cost_inv_by_cat, xlabel='p [%]', ylabel='[bEUR/y]', ylim=30,
                     pdf_name=dir_plot + '/cost-inv-breakdown-' + pdf + '.pdf')

    df_cost_inv_by_cat_aggregated = \
        pd.concat([df_cost_inv_by_cat[['Electricity', 'Infrastructure', 'Synthetic fuels']],
                   df_cost_inv_by_cat[['Electricity storage', 'Thermal storage', 'Other storage']].sum(axis=1),
                   df_cost_inv_by_cat[['Heat high temperature', 'Heat low temperature centralised',
                                       'Heat low temperature decentralised']].sum(axis=1),
                   df_cost_inv_by_cat[['Passenger public', 'Passenger private', 'Freight']].sum(axis=1)], axis=1)
    df_cost_inv_by_cat_aggregated.columns = ['Electricity', 'Infrastructure', 'Synthetic fuels',
                                             'storage', 'heat', 'mobility']
    plot_stacked_bar(df_data=df_cost_inv_by_cat_aggregated, xlabel='p [%]', ylabel='[bEUR/y]', ylim=30,
                     pdf_name=dir_plot + '/cost-inv-breakdown-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_cost_op_filtered[[i for i in RES_renewable if i in df_cost_op_filtered.columns]],
                     xlabel='p [%]', ylabel='[bEUR/y]', ylim=60,
                     pdf_name=dir_plot + '/cost-op-re-breakdown-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_cost_op_filtered[[i for i in RES_non_renewable if i in df_cost_op_filtered.columns]],
                     xlabel='p [%]', ylabel='[bEUR/y]', ylim=20,
                     pdf_name=dir_plot + '/cost-op-non-re-breakdown-' + pdf + '.pdf')

    ####################################################################################################################
    # PLot assets installed capacities
    df_assets.columns = np.round(x_gwp_tot_index, 1)
    plot_asset_capacities_by_tech(df_assets=df_assets, pdf=pdf, user_data=config['user_data'], dir_plot=dir_plot,
                                  xlabel='[MtCO2-eq./y]')

    ##############
    #
    df_EI_filtered = retrieve_non_zero_val(df=df_EI.drop(columns=['Subcategory']).transpose())
    df_EI_percentage = df_EI_filtered.divide(df_EI_filtered.sum(axis=1), axis=0) * 100
    df_EI_percentage.index = np.round(x_gwp_tot_index, 1)
