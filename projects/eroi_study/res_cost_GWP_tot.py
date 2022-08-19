# -*- coding: utf-8 -*-
"""
Results of system Einv_tot minimization with several scenarios computed
by constraining GWP_tot with different GHG emissions targets.

@author: Jonathan Dumas, Antoine Dubois
"""

import os

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt


from energyscope.utils import make_dir, get_names, get_colors
from projects.eroi_study.res_einv_GWP_tot import print_share_of_energies, plot_series
from projects.eroi_study.res_einv_GWP_tot_vs_GWP_op import fec_plots, plot_asset_capacities_by_tech
from projects.eroi_study.utils_plot import plot_stacked_bar, plot_one_serie
from projects.eroi_study.utils_res import eroi_computation, res_details, gwp_computation, retrieve_non_zero_val, \
    retrieve_einv_const_by_categories, res_assets_capacity, gwp_breakdown, gwp_const_per_category, \
    cost_computation, cost_breakdown
from projects.eroi_study.utils import load_config, replace_item_in_list


# TODO: could maybe be merged with 'plot_primary_energy' in res_einv_gwp_tot.py
def plot_primary_energy(ei_df, ei_cat_df, res_renewable, res_non_renewable, x_gwp_tot_index,
                        user_data_dir, save_dir, fn_suffix):

    df_index = x_gwp_tot_index.astype(int)

    # TODO: this is inefficient
    # Waste+Methanol+Ammonia = other non-RE
    new_list = list(ei_cat_df.index)
    for item_old, item_new in zip(['Biofuel', 'Non-biomass', 'Other non-renewable', 'Fossil fuel'],
                                  ['RE-fuels', 'Wind+Solar', 'non-RE', 'Fossil fuels']):
        new_list = replace_item_in_list(target_list=new_list, item_old=item_old, item_new=item_new)
    ei_cat_df.index = new_list
    ei_cat_df = ei_cat_df.drop(index=['Export']).transpose()
    ei_cat_df = ei_cat_df[sorted(ei_cat_df.columns)]
    ei_cat_df.index = df_index
    colors = pd.Series({'Biomass': '#996633', 'Fossil': '#858585', 'RE-fuels': '#910091', 'Wind+Solar': '#009d3f',
                        'non-RE': '#000ECD'})
    pdf_name = os.path.join(save_dir, f'EI-categories-{fn_suffix}.pdf')
    plot_stacked_bar(ei_cat_df,
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]',
                     ylim=625, pdf_name=pdf_name, colors=colors)

    # Renewable RES: biofuel + biomass + non-biomass
    ei_res_re_df = retrieve_non_zero_val(df=ei_df.loc[res_renewable].drop(columns=['Subcategory']).transpose())
    ei_res_re_df = ei_res_re_df[['AMMONIA_RE', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD', 'RES_HYDRO',
                                 'RES_SOLAR', 'RES_WIND', 'H2_RE', 'BIODIESEL']]
    ei_res_re_df = ei_res_re_df[sorted(ei_res_re_df.columns)]
    colors = get_colors(list(ei_res_re_df.columns), 'resources', user_data_path=user_data_dir)
    ei_res_re_df.columns = get_names(list(ei_res_re_df.columns), 'resources', user_data_path=user_data_dir)
    ei_res_re_df.index = df_index
    pdf_name = os.path.join(save_dir, f'EI-RE-{fn_suffix}.pdf')
    plot_stacked_bar(ei_res_re_df, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]',
                     ylim=625, pdf_name=pdf_name, colors=colors)

    # Non-renewable RES: Fossil fuel + Other non-renewable
    ei_res_non_re_df = retrieve_non_zero_val(df=ei_df.loc[res_non_renewable].drop(columns=['Subcategory']).transpose())
    ei_res_non_re_df = ei_res_non_re_df[['GAS', 'ELECTRICITY', 'AMMONIA', 'WASTE', 'LFO', 'COAL']]
    ei_res_non_re_df = ei_res_non_re_df[sorted(ei_res_non_re_df.columns)]
    colors = get_colors(list(ei_res_non_re_df.columns), 'resources', user_data_path=user_data_dir)
    ei_res_non_re_df.columns = get_names(list(ei_res_non_re_df.columns), 'resources', user_data_path=user_data_dir)
    ei_res_non_re_df.index = x_gwp_tot_index.astype(int)
    pdf_name = os.path.join(save_dir, f'EI-non-RE-{fn_suffix}.pdf')
    plot_stacked_bar(ei_res_non_re_df, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]',
                     ylim=375, pdf_name=pdf_name, colors=colors)


def plot_einv_op(einv_res_cat_df, einv_op_df, res_renewable, res_non_renewable, x_gwp_tot_index, save_dir, fn_suffix):

    # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel,
    # Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    einv_res_cat_df.columns = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(einv_res_cat_df.transpose(), xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=160,
                     pdf_name=save_dir + '/einv-res-' + fn_suffix + '.pdf')

    # Einv_op classed by RESOURCES (RE and non-RE)
    einv_op_filtered_df = retrieve_non_zero_val(df=einv_op_df.transpose())
    einv_op_filtered_df.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(einv_op_filtered_df, xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=160,
                     pdf_name=save_dir + '/einv-op-details-' + fn_suffix + '.pdf')

    # Einv_op by RE-RESOURCES
    einv_op_re_filtered_df = retrieve_non_zero_val(df=einv_op_df.loc[res_renewable].transpose())
    einv_op_re_filtered_df.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(einv_op_re_filtered_df, xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=160,
                     pdf_name=save_dir + '/einv-op-re-res-' + fn_suffix + '.pdf')

    # Einv_op by NON-RE-RESOURCES
    einv_op_non_re_filtered_df = retrieve_non_zero_val(df=einv_op_df.loc[res_non_renewable].transpose())
    einv_op_non_re_filtered_df.index = np.round(x_gwp_tot_index, 1)
    new_cols = list(einv_op_non_re_filtered_df.columns)
    new_cols = replace_item_in_list(target_list=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    einv_op_non_re_filtered_df.columns = new_cols
    plot_stacked_bar(einv_op_non_re_filtered_df, xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=30,
                     pdf_name=save_dir + '/einv-op-non-re-res-' + fn_suffix + '.pdf')


def plot_einv_const(einv_tech_cat_df, einv_const_dict, x_gwp_tot_index, save_dir, fn_suffix):

    # Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    einv_tech_cat_df.columns = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(einv_tech_cat_df.drop(index=['Infrastructure']).transpose(),
                     xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=35,
                     pdf_name=save_dir + '/einv-tech-' + fn_suffix + '.pdf')

    # Einv_const classed by categories of technologies: 'Electricity', 'Heat', 'Mobility',
    # 'Infrastructure', 'Synthetic fuels', 'Storage'
    einv_const_dict['Electricity'].index = np.round(x_gwp_tot_index, 1)
    ymax = einv_const_dict['Electricity'].sum(axis=1).max() * 1.05
    elec_tech = list(einv_const_dict['Electricity'].max(axis=0)[einv_const_dict['Electricity'].max(axis=0) > 0.1].index)
    plot_stacked_bar(einv_const_dict['Electricity'][elec_tech],
                     xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=ymax,
                     pdf_name=save_dir + '/einv_const-elec-' + fn_suffix + '.pdf')

    einv_const_dict['Mobility'].index = np.round(x_gwp_tot_index, 1)
    ymax = einv_const_dict['Mobility'].sum(axis=1).max() * 1.05
    # select only the mobility technologies with Einv_const > 0.5 GWh/y
    mobility_tech = list(einv_const_dict['Mobility'].max(axis=0)[einv_const_dict['Mobility'].max(axis=0) > 0.5].index)
    plot_stacked_bar(einv_const_dict['Mobility'][mobility_tech],
                     xlabel='GWP total [MtCO2-eq./y]', ylabel='[TWh]', ylim=ymax,
                     pdf_name=save_dir + '/einv_const-mob-' + fn_suffix + '.pdf')


def plot_gwp(gwp_op_df, gwp_const_df, user_data_dir, save_dir, fn_suffix):

    gwp_const_filtered_df = retrieve_non_zero_val(df=gwp_const_df.transpose())
    gwp_const_by_tech_cat = \
        gwp_const_per_category(gwp_const_df=gwp_const_filtered_df, user_data_dir=user_data_dir)
    tech_list = ['Electricity', 'Heat high temperature', 'Heat low temperature centralised',
                 'Heat low temperature decentralised', 'Passenger public', 'Passenger private', 'Freight',
                 'Synthetic fuels', 'Electricity storage', 'Thermal storage', 'Other storage']

    # Aggregate GWP_const by sectors: heat, storage, mobility, and electricity
    gwp_const_by_cat_df = pd.concat([gwp_const_by_tech_cat[tech].sum(axis=1) for tech in tech_list], axis=1)
    gwp_const_by_cat_df.columns = tech_list
    df_1 = gwp_const_by_cat_df[
        ['Heat high temperature', 'Heat low temperature centralised', 'Heat low temperature decentralised']].sum(axis=1)
    df_1.name = 'Heat'
    df_2 = gwp_const_by_cat_df[['Electricity storage', 'Thermal storage', 'Other storage']].sum(axis=1)
    df_2.name = 'Storage'
    df_3 = gwp_const_by_cat_df[['Passenger public', 'Passenger private', 'Freight']].sum(axis=1)
    df_3.name = 'Mobility'
    df_4 = gwp_const_by_cat_df[['Electricity', 'Synthetic fuels']]
    gwp_const_concat_df = pd.concat([df_1, df_2, df_3, df_4], axis=1)
    plot_stacked_bar(gwp_const_concat_df, xlabel='p [%]', ylabel='[MtCO2-eq./y]', ylim=9,
                     pdf_name=save_dir + '/gwp_const-breakdown-' + fn_suffix + '.pdf')

    # GHG emissions breakdown by resources
    gwp_op_filtered_df = retrieve_non_zero_val(df=gwp_op_df.transpose())
    new_cols = list(gwp_op_filtered_df.columns)
    new_cols = replace_item_in_list(target_list=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    gwp_op_filtered_df.columns = new_cols
    plot_stacked_bar(gwp_op_filtered_df, xlabel='p [%]', ylabel='[MtCO2-eq./y]', ylim=100,
                     pdf_name=save_dir + '/gwp_op-breakdown-' + fn_suffix + '.pdf')


def plot_cost(cost_inv_df, cost_op_df, user_data_dir, res_renewable, res_non_renewable, save_dir, fn_suffix):

    cost_inv_filtered_df = retrieve_non_zero_val(df=cost_inv_df.transpose())
    # cost_maint_filtered_df = retrieve_non_zero_val(df=cost_maint_df.transpose())
    cost_op_filtered_df = retrieve_non_zero_val(df=cost_op_df.transpose())

    # Retrieve the list of technologies
    aux_tech_df = pd.read_csv(user_data_dir + "/aux_technologies.csv", index_col=0)

    # Retrieve the list subcategory of technologies
    tech_subcategory_list = list(dict.fromkeys(list(aux_tech_df['Subcategory'])))
    tech_by_subcategory = dict()
    for cat in tech_subcategory_list:
        tech_by_subcategory[cat] = list(aux_tech_df[aux_tech_df['Subcategory'] == cat].index)

    concat_list = []
    for cat in tech_by_subcategory.keys():
        concat_list.append(cost_inv_filtered_df[[i for i in cost_inv_filtered_df.columns
                                                 if i in tech_by_subcategory[cat]]].sum(axis=1))
    cost_inv_by_cat_df = pd.concat(concat_list, axis=1)
    cost_inv_by_cat_df.columns = tech_by_subcategory.keys()

    plot_stacked_bar(cost_inv_filtered_df[[i for i in cost_inv_filtered_df.columns
                                          if i in tech_by_subcategory['Electricity']]],
                     xlabel='p [%]', ylabel='[bEUR/y]', ylim=30,
                     pdf_name=save_dir + '/cost-inv-elec-breakdown-' + fn_suffix + '.pdf')
    plot_stacked_bar(cost_inv_filtered_df[[i for i in cost_inv_filtered_df.columns
                                          if i in tech_by_subcategory['Passenger private']]],
                     xlabel='p [%]', ylabel='[bEUR/y]', ylim=30,
                     pdf_name=save_dir + '/cost-inv-private-mob-breakdown-' + fn_suffix + '.pdf')
    plot_stacked_bar(cost_inv_by_cat_df, xlabel='p [%]', ylabel='[bEUR/y]', ylim=30,
                     pdf_name=save_dir + '/cost-inv-breakdown-' + fn_suffix + '.pdf')

    cost_inv_by_cat_aggregated_df = \
        pd.concat([cost_inv_by_cat_df[['Electricity', 'Infrastructure', 'Synthetic fuels']],
                   cost_inv_by_cat_df[['Electricity storage', 'Thermal storage', 'Other storage']].sum(axis=1),
                   cost_inv_by_cat_df[['Heat high temperature', 'Heat low temperature centralised',
                                       'Heat low temperature decentralised']].sum(axis=1),
                   cost_inv_by_cat_df[['Passenger public', 'Passenger private', 'Freight']].sum(axis=1)], axis=1)
    cost_inv_by_cat_aggregated_df.columns = ['Electricity', 'Infrastructure', 'Synthetic fuels',
                                             'storage', 'heat', 'mobility']
    plot_stacked_bar(cost_inv_by_cat_aggregated_df, xlabel='p [%]', ylabel='[bEUR/y]', ylim=30,
                     pdf_name=save_dir + '/cost-inv-breakdown-' + fn_suffix + '.pdf')
    plot_stacked_bar(cost_op_filtered_df[[i for i in res_renewable if i in cost_op_filtered_df.columns]],
                     xlabel='p [%]', ylabel='[bEUR/y]', ylim=60,
                     pdf_name=save_dir + '/cost-op-re-breakdown-' + fn_suffix + '.pdf')
    plot_stacked_bar(cost_op_filtered_df[[i for i in res_non_renewable if i in cost_op_filtered_df.columns]],
                     xlabel='p [%]', ylabel='[bEUR/y]', ylim=20,
                     pdf_name=save_dir + '/cost-op-non-re-breakdown-' + fn_suffix + '.pdf')


def main(config_fn, domestic_re_share):

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn=config_fn + '.yaml')

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
    if config_fn == 'config_2035_2_GW_nuc':
        dir_name = f"{config['case_studies_dir']}/{'cost_GWP_tot_2_GW_nuc_' + str(domestic_re_share)}"
    elif config_fn == 'config_2035_5_6_GW_nuc':
        dir_name = f"{config['case_studies_dir']}/{'cost_GWP_tot_5_6_GW_nuc_' + str(domestic_re_share)}"
    else:
        dir_name = f"{config['case_studies_dir']}/{'cost_GWP_tot_' + str(domestic_re_share)}"

    res_df, fec_details_df = eroi_computation(dir_name=dir_name, user_data_dir=config['user_data'], range_val=range_val)
    einv_op_df, einv_res_cat_df, einv_tech_cat_df, ei_cat_df, ei_df = \
        res_details(range_val=range_val, all_data=all_data, dir_name=dir_name, user_data=config['user_data'])
    gwp_df = gwp_computation(dir_name=dir_name, range_val=range_val)
    x_gwp_tot_index = gwp_df.sum(axis=1).values
    cost_df = cost_computation(dir_name=dir_name, range_val=range_val)
    einv_const_dict = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data,
                                                        dir_name=dir_name, user_data=config['user_data'])
    assets_df = res_assets_capacity(range_val=range_val, dir_name=dir_name)
    gwp_const_df, gwp_op_df = gwp_breakdown(dir_name=dir_name, range_val=range_val)
    cost_inv_df, cost_maint_df, cost_op_df = cost_breakdown(dir_name=dir_name, range_val=range_val)

    ######
    # Share of energies
    if 0:
        print_share_of_energies(ei_df, gwp_df, res_df, assets_df)
    ####################################################################################################################
    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    ####################################################################################################################
    fn_suffix = 'cost-' + str(domestic_re_share)

    if config_fn == 'config_2035_2_GW_nuc':
        dir_plot = 'cost_GWP_tot_2_GW_nuc_' + str(domestic_re_share)
    elif config_fn == 'config_2035_5_6_GW_nuc':
        dir_plot = 'cost_GWP_tot_5_6_GW_nuc_' + str(domestic_re_share)
    else:
        dir_plot = 'cost_GWP_tot_' + str(domestic_re_share)

    main_export_dir = os.path.join(cwd, 'export')
    make_dir(main_export_dir)
    save_dir = os.path.join(main_export_dir, dir_plot)
    make_dir(save_dir)

    ####################################################################################################################
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    if 0:
        intervals = [[40, 65], [1, 10], [1, 10], [300, 480], [30, 180], [350, 550]]
        plot_series(cost_df, res_df, ei_df, x_gwp_tot_index, save_dir, domestic_re_share, intervals)

    ####################################################################################################################
    # FEC
    if 0:
        fec_plots(df_fec_data=fec_details_df, save_dir=save_dir, fn_suffix=fn_suffix)

    ####################################################################################################################
    # PRIMARY ENERGY
    res_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD',
                     'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    res_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
                         'METHANOL', 'URANIUM']
    if 1:
        plot_primary_energy(ei_df, ei_cat_df, res_renewable, res_non_renewable, x_gwp_tot_index,
                            config['user_data'], save_dir, fn_suffix)

    ####################################################################################################################
    # Einv_tot = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)
    if 0:
        plot_einv_op(einv_res_cat_df, einv_op_df, res_renewable, res_non_renewable, x_gwp_tot_index,
                     save_dir, fn_suffix)
        plot_einv_const(einv_tech_cat_df, einv_const_dict, x_gwp_tot_index, save_dir, fn_suffix)

    ##############################################################################################################
    # GWP breakdown by resources and technologies
    # GHG emissions related to technologies
    if 0:
        plot_gwp(gwp_op_df, gwp_const_df, user_data_dir, save_dir, fn_suffix)

    ##############################################################################################################
    # Cost breakdown by resources and technologies
    if 0:
        plot_cost(cost_inv_df, cost_op_df, user_data_dir, res_renewable, res_non_renewable, save_dir, fn_suffix)

    ####################################################################################################################
    # Plot assets installed capacities
    assets_df.columns = np.round(x_gwp_tot_index, 1)
    if 0:
        plot_asset_capacities_by_tech(assets_df=assets_df, user_data_dir=config['user_data'],
                                      save_dir=dir_plot, fn_suffix=fn_suffix, xlabel='[MtCO2-eq./y]')
    ##############
    #
    # ei_filtered_df = retrieve_non_zero_val(df=ei_df.drop(columns=['Subcategory']).transpose())
    # ei_percentage_df = ei_filtered_df.divide(ei_filtered_df.sum(axis=1), axis=0) * 100
    # ei_percentage_df.index = np.round(x_gwp_tot_index, 1)

    ####################################################################################################################
    # Compare the case p = 100, 20, 10 and 5
    # When GWP_tot <= p * gwp_limit
    # Use fec_details DataFrame to identify the technologies that satisfy the different EDU and the FEC related
    # year_balance_100_df = pd.read_csv(dir_name + '/run_100/' + "/output/year_balance.csv", index_col=0)
    # fec_details_100, fec_tot_100 = compute_fec(year_balance=year_balance_100_df, user_data_dir=config['user_data'])
    #
    # year_balance_10_df = pd.read_csv(dir_name + '/run_10/' + "/output/year_balance.csv", index_col=0)
    # fec_details_10, fec_tot_10 = compute_fec(year_balance=year_balance_10_df, user_data_dir=config['user_data'])
    #
    # year_balance_5_df = pd.read_csv(dir_name + '/run_5/' + "/output/year_balance.csv", index_col=0)
    # fec_details_5, fec_tot_5 = compute_fec(year_balance=year_balance_5_df, user_data_dir=config['user_data'])
    #
    # energy_stored_50_df = pd.read_csv(dir_name + '/run_50/' + "/output/hourly_data/energy_stored.csv",
    #                                   index_col=0).dropna(axis=1)
    # layer_elec_50_df = pd.read_csv(dir_name + '/run_50/' + "/output/hourly_data/layer_ELECTRICITY.csv",
    #                                index_col=0).dropna(axis=1)
    # layer_HEAT_LOW_T_DECEN_50_df = pd.read_csv(dir_name+'/run_50/'+"/output/hourly_data/layer_HEAT_LOW_T_DECEN.csv",
    #                                            index_col=0).dropna(axis=1)
    # layer_HEAT_LOW_T_DHN_50_df = pd.read_csv(dir_name + '/run_50/' + "/output/hourly_data/layer_HEAT_LOW_T_DHN.csv",
    #                                          index_col=0).dropna(axis=1)

    #
    # layer_gas_5_df = pd.read_csv(dir_name+'/run_5/'+"/output/hourly_data/layer_GAS.csv", index_col=0).dropna(axis=1)
    # layer_gas_5_df['GAS_STORAGE_Pin']

    # Compare technologies that produce electricity between p = 5 and 10 %
    # For instance, when p = 5  -> CCGT mainly produced electricity for the case where GWP_tot is constrained
    # print(year_balance_10_df[year_balance_10_df['ELECTRICITY'] > 0]['ELECTRICITY'])
    # print(year_balance_5_df[year_balance_5_df['ELECTRICITY'] > 0]['ELECTRICITY'])


if __name__ == '__main__':

    # parameters
    domestic_re_share_ = 0  # 0, 30 %
    config_fn_ = 'config_2035'  # config_2035, config_2035_2_GW_nuc, config_2035_5_6_GW_nuc

    main(config_fn_, domestic_re_share_)
