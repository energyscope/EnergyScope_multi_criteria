# -*- coding: utf-8 -*-
"""
Results of system Einv_tot minimization with several scenarios computed
by constraining GWP_tot with different GHG emissions targets.

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
from energyscope.utils import make_dir, load_config
# from energyscope.postprocessing import get_total_einv, compute_fec, get_gwp, \
#     compute_einv_details, compute_primary_energy
# from projects.eroi_study.res_einv_GWP_tot_vs_GWP_op import fec_plots, primary_energy_plots, \
#     plot_asset_capacities_by_tech
# from projects.eroi_study.utils_plot import plot_stacked_bar, plot_one_serie
from projects.eroi_study.utils_plot import plot_two_series
# from projects.eroi_study.utils_res import retrieve_non_zero_val, retrieve_einv_const_by_categories,\
#     res_assets_capacity, gwp_const_per_category
from projects.eroi_study.utils_res import eroi_computation, res_details, gwp_computation, \
    gwp_breakdown, cost_computation


# TODO: define in two files -> move to utils ?
def replace_item_in_list(target_list: list, item_old: str, item_new: str):
    """
    Replace a specific item into a list
    """
    for i in range(len(target_list)):
        if target_list[i] == item_old:
            target_list[i] = item_new
    return target_list


# parameters
domestic_RE_share = 0  # 0, 30 %
config_name_file = 'config_2035'  # config_2035, config_2035_with_nuc

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
    # Compare min Einv vs. min Cost:
    # s.t. GWP_tot <= p * GWP_op^i
    #  with p a percentage and GWP_op^i the GHG emissions target.
    # -----------------------------------------------

    range_val_einv = range(100, 0, -5)
    range_val_cost = range(100, 0, -5)
    dir_einv = f"{config['case_studies_dir']}/{'einv_GWP_tot_' + str(domestic_RE_share)}"
    dir_cost = f"{config['case_studies_dir']}/{'cost_GWP_tot_' + str(domestic_RE_share)}"
    df_res_einv, df_fec_details_einv = \
        eroi_computation(dir_name=dir_einv, user_data=config['user_data'], range_val=range_val_einv)
    df_res_cost, df_fec_details_cost = \
        eroi_computation(dir_name=dir_cost, user_data=config['user_data'], range_val=range_val_cost)
    df_Einv_op_einv, df_Einv_RES_cat_einv, df_Einv_TECH_cat_einv, df_EI_cat_einv, df_EI_einv = \
        res_details(range_val=range_val_einv, all_data=all_data, dir_name=dir_einv, user_data=config['user_data'])
    df_Einv_op_cost, df_Einv_RES_cat_cost, df_Einv_TECH_cat_cost, df_EI_cat_cost, df_EI_cost = \
        res_details(range_val=range_val_cost, all_data=all_data, dir_name=dir_cost, user_data=config['user_data'])

    df_GWP_einv = gwp_computation(dir_name=dir_einv, range_val=range_val_einv)
    df_cost_einv = cost_computation(dir_name=dir_einv, range_val=range_val_einv)
    df_gwp_const_einv, df_gwp_op_einv = gwp_breakdown(dir_name=dir_einv, range_val=range_val_einv)
    df_GWP_cost = gwp_computation(dir_name=dir_cost, range_val=range_val_cost)
    df_cost_cost = cost_computation(dir_name=dir_cost, range_val=range_val_cost)
    df_gwp_const_cost, df_gwp_op_cost = gwp_breakdown(dir_name=dir_cost, range_val=range_val_cost)

    ####################################################################################################################
    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    ####################################################################################################################
    dir_plot = 'einv_vs_cost_GWP_tot_' + str(domestic_RE_share)
    make_dir(cwd+'/export/')
    make_dir(cwd+'/export/'+dir_plot+'/')
    dir_plot = cwd+'/export/einv_vs_cost_GWP_tot_' + str(domestic_RE_share)
    pdf = 'gwp-tot-' + str(domestic_RE_share)

    ####################################################################################################################
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    # x_gwp_tot_index = df_GWP.sum(axis=1).values
    label1 = 'EROI maximization'
    label2 = 'Cost minimization'
    x_einv_index = df_GWP_einv.sum(axis=1).values
    x_cost_index = df_GWP_cost.sum(axis=1).values
    plot_two_series(df_data_1=df_res_einv['EROI'], df_data_2=df_res_cost['EROI'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot+'/cost-vs-eroi_eroi_'+str(domestic_RE_share)+'.pdf', x_index=x_einv_index,
                    ylim=[1.5, 10], ylabel='EROI [-]', xlabel='Yearly emissions limit [MtCO2-eq./y]',
                    x_index_2=x_cost_index, fontsize=20)
    plot_two_series(df_data_1=df_res_einv['FEC'], df_data_2=df_res_cost['FEC'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot+'/cost-vs-eroi_fec_'+str(domestic_RE_share)+'.pdf', x_index=x_einv_index,
                    ylim=[300, 480], ylabel='FEC [TWh/y]', xlabel='Yearly emissions [MtCO2-eq./y]',
                    x_index_2=x_cost_index)
    plot_two_series(df_data_1=df_res_einv['Einv'], df_data_2=df_res_cost['Einv'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot+'/cost-vs-eroi_einv_'+str(domestic_RE_share)+'.pdf', x_index=x_einv_index,
                    ylim=[30, 180], ylabel=r'$Einv{tot}$ [TWh/y]', xlabel='Yearly emissions [MtCO2-eq./y]',
                    x_index_2=x_cost_index)
    plot_two_series(df_data_1=df_GWP_einv.sum(axis=1), df_data_2=df_GWP_cost.sum(axis=1),
                    label_1=label1, label_2=label2,
                    pdf_name=dir_plot+'/cost-vs-eroi_gwp_'+str(domestic_RE_share)+'.pdf', x_index=x_einv_index,
                    ylim=[0, 105], ylabel=r'$GWP_{tot}$ [MtC02/y]', xlabel='Yearly emissions [MtCO2-eq./y]',
                    x_index_2=x_cost_index)
    plot_two_series(df_data_1=df_GWP_einv['GWP_cons'], df_data_2=df_GWP_cost['GWP_cons'],
                    label_1=label1, label_2=label2,
                    pdf_name=dir_plot+'/cost-vs-eroi_gwp_const_'+str(domestic_RE_share)+'.pdf', x_index=x_einv_index,
                    ylim=[0, 10], ylabel=r'$GWP_{const}$ [MtC02/y]', xlabel='Yearly emissions [MtCO2-eq./y]',
                    x_index_2=x_cost_index)
    plot_two_series(df_data_1=df_GWP_einv['GWP_op'], df_data_2=df_GWP_cost['GWP_op'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot+'/cost-vs-eroi_gwp_op_'+str(domestic_RE_share)+'.pdf', x_index=x_einv_index,
                    ylim=[0, 100], ylabel=r'$GWP_{op}$ [MtC02/y]', xlabel='Yearly emissions [MtCO2-eq./y]',
                    x_index_2=x_cost_index)
    plot_two_series(df_data_1=df_cost_einv.sum(axis=1), df_data_2=df_cost_cost.sum(axis=1),
                    label_1=label1, label_2=label2,
                    pdf_name=dir_plot+'/cost-vs-eroi_cost_'+str(domestic_RE_share)+'.pdf', x_index=x_einv_index,
                    ylim=[40, 100], ylabel='Cost [bEUR/y]', xlabel='Yearly emissions limit [MtCO2-eq./y]',
                    x_index_2=x_cost_index, fontsize=20)
    plot_two_series(df_data_1=df_res_einv['EROI'], df_data_2=df_res_cost['EROI'],
                    label_1='Max system EROI', label_2='Min system Cost',
                    pdf_name=dir_plot+'/cost-vs-eroi_eroi_paper_structure_'+str(domestic_RE_share)+'.pdf',
                    x_index=x_einv_index, ylim=[1.5, 10], ylabel='', xlabel='Yearly emissions target',
                    x_index_2=x_cost_index, fontsize=20)

    # plot_one_serie(df_data=df_cost.sum(axis=1), label='Cost',
    #                pdf_name=dir_plot + '/cost_' + str(domestic_RE_share) + '.pdf',
    #                x_index=x_gwp_tot_index, ylim=[40, 100], ylabel='[bEUR/y]')
    # plot_one_serie(df_data=df_res['EROI'], label='EROI',
    #                pdf_name=dir_plot + '/eroi_custom_' + str(domestic_RE_share) + '.pdf',
    #                x_index=x_gwp_tot_index, ylim=[1, 10], ylabel='[-]', yticks_val=[3, 5, 7, 9])
    # plot_one_serie(df_data=df_res['EROI'], label='EROI',
    #                pdf_name=dir_plot + '/eroi_' + str(domestic_RE_share) + '.pdf',
    #                x_index=x_gwp_tot_index, ylim=[2.5, 10], ylabel='[-]')
    # plot_one_serie(df_data=df_res['FEC'], label='FEC',
    #                pdf_name=dir_plot + '/fec_' + str(domestic_RE_share) + '.pdf',
    #                x_index=x_gwp_tot_index, ylim=[300, 480], ylabel='[TWh/y]')
    # plot_one_serie(df_data=df_res['Einv'], label='Einv',
    #                pdf_name=dir_plot + '/einv_' + str(domestic_RE_share) + '.pdf',
    #                x_index=x_gwp_tot_index, ylim=[30, 180], ylabel='[TWh/y]')
    # plot_one_serie(df_data=df_EI.drop(columns=['Subcategory']).transpose().sum(axis=1), label='Primary energy',
    #                pdf_name=dir_plot + '/EI_tot_' + str(domestic_RE_share) + '.pdf',
    #                x_index=x_gwp_tot_index, ylim=[350, 550], ylabel='[TWh/y]')
    #
    #
    # ####################################################################################################################
    # # FEC
    # fec_plots(df_fec_data=df_fec_details, pdf=pdf, dir_plot=dir_plot)
    #
    # ####################################################################################################################
    # # PRIMARY ENERGY
    # new_list = list(df_EI_cat.index)
    # for item_old, item_new in zip(['Biofuel', 'Non-biomass', 'Other non-renewable', 'Fossil fuel'],
    #                               ['Synthetic fuels', 'Wind+Solar', 'Waste+Methanol+Ammonia', 'Fossil fuels']):
    #     new_cols = replace_item_in_list(target_list=new_list, item_old=item_old, item_new=item_new)
    # df_EI_cat.index = new_list
    # df_EI_cat.columns = np.round(x_gwp_tot_index, 1)
    # plot_stacked_bar(df_data=df_EI_cat.drop(index=['Export']).transpose(),
    #                  xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=600,
    #                  pdf_name=dir_plot+'/EI-categories-'+pdf+'.pdf')
    #
    # # Renewable RES: biofuel + biomass + non-biomass
    # RES_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS',
    #                  'WOOD',
    #                  'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    # df_EI_RES_RE = retrieve_non_zero_val(df=df_EI.loc[RES_renewable].drop(columns=['Subcategory']).transpose())
    # new_cols = list(df_EI_RES_RE.columns)
    # for item_old, item_new in zip(['METHANOL_RE', 'GAS_RE', 'AMMONIA_RE', 'H2_RE', 'RES_HYDRO',
    #                                'RES_SOLAR', 'RES_WIND', 'RES_GEO'],
    #                               ['METHANOL_SYN', 'GAS_SYN', 'AMMONIA_SYN', 'H2_SYN', 'HYDRO',
    #                                'SOLAR', 'WIND', 'GEO']):
    #     new_cols = replace_item_in_list(target_list=new_cols, item_old=item_old, item_new=item_new)
    # df_EI_RES_RE.columns = new_cols
    # # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    # colors = plt.cm.tab20b(np.linspace(0, 1, 10))
    # df_EI_RES_RE.index = np.round(x_gwp_tot_index, 1)
    # plot_stacked_bar(df_data=df_EI_RES_RE, xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=530,
    #                  pdf_name=dir_plot + '/EI-RE-' + pdf + '.pdf', colors=colors)
    #
    # # Non renewable RES: Fossil fuel + Other non-renewable
    # RES_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
    #                      'METHANOL', 'URANIUM']
    # colors = plt.cm.tab20c(np.linspace(0, 1, 10))
    # df_EI_RES_non_RE =
    #   retrieve_non_zero_val(df=df_EI.loc[RES_non_renewable].drop(columns=['Subcategory']).transpose())
    # new_cols = list(df_EI_RES_non_RE.columns)
    # new_cols = replace_item_in_list(l=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    # df_EI_RES_non_RE.columns = new_cols
    # df_EI_RES_non_RE.index = np.round(x_gwp_tot_index, 1)
    # plot_stacked_bar(df_data=df_EI_RES_non_RE, xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=350,
    #                  pdf_name=dir_plot + '/EI-non-RE-' + pdf + '.pdf', colors=colors)
    #
    #
    # ####################################################################################################################
    # # Einv_tot = Einv_operation + Einv_construction
    # # RESOURCES -> use Einv only for the operation (0 for construction)
    # # TECHNOLOGIES -> use Einv only for the construction (0 for operation)
    #
    # # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel,
    # #  Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    # df_Einv_RES_cat.columns = np.round(x_gwp_tot_index, 1)
    # plot_stacked_bar(df_data=df_Einv_RES_cat.transpose(), xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=160,
    #                  pdf_name=dir_plot+'/einv-res-'+pdf+'.pdf')
    #
    # # Einv_op classed by RESOURCES (RE and non-RE)
    # df_einv_op_filtered = retrieve_non_zero_val(df=df_Einv_op.transpose())
    # df_einv_op_filtered.index = np.round(x_gwp_tot_index, 1)
    # plot_stacked_bar(df_data=df_einv_op_filtered, xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=160,
    #                  pdf_name=dir_plot+'/einv-op-details-'+pdf+'.pdf')
    #
    # # Einv_op by RE-RESOURCES
    # df_einv_op_RE_filtered = retrieve_non_zero_val(df=df_Einv_op.loc[RES_renewable].transpose())
    # df_einv_op_RE_filtered.index = np.round(x_gwp_tot_index, 1)
    # plot_stacked_bar(df_data=df_einv_op_RE_filtered, xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=160,
    #                  pdf_name=dir_plot+'/einv-op-re-res-'+pdf+'.pdf')
    #
    # # Einv_op by NON-RE-RESOURCES
    # df_einv_op_non_RE_filtered = retrieve_non_zero_val(df=df_Einv_op.loc[RES_non_renewable].transpose())
    # df_einv_op_non_RE_filtered.index = np.round(x_gwp_tot_index, 1)
    # new_cols = list(df_einv_op_non_RE_filtered.columns)
    # new_cols = replace_item_in_list(l=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    # df_einv_op_non_RE_filtered.columns = new_cols
    # plot_stacked_bar(df_data=df_einv_op_non_RE_filtered, xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=30,
    #                  pdf_name=dir_plot+'/einv-op-non-re-res-'+pdf+'.pdf')
    #
    # # 2. Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    # df_Einv_TECH_cat.columns =np.round(x_gwp_tot_index, 1)
    # plot_stacked_bar(df_data=df_Einv_TECH_cat.drop(index=['Infrastructure']).transpose(),
    #                  xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=35,
    #                  pdf_name=dir_plot+'/einv-tech-'+pdf+'.pdf')
    #
    # # Einv_const classed by categories of technologies: 'Electricity', 'Heat', 'Mobility',
    # #  'Infrastructure', 'Synthetic fuels', 'Storage'
    # Einv_const_dict['Electricity'].index = np.round(x_gwp_tot_index, 1)
    # ymax = Einv_const_dict['Electricity'].sum(axis=1).max() * 1.05
    # elec_tech =
    #   list(Einv_const_dict['Electricity'].max(axis=0)[Einv_const_dict['Electricity'].max(axis=0) > 0.1].index)
    # plot_stacked_bar(df_data=Einv_const_dict['Electricity'][elec_tech],
    #                  xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=ymax,
    #                  pdf_name=dir_plot+'/einv_const-elec-'+pdf+'.pdf')
    #
    # Einv_const_dict['Mobility'].index = np.round(x_gwp_tot_index, 1)
    # ymax = Einv_const_dict['Mobility'].sum(axis=1).max() * 1.05
    # # select only the mobility technologies with Einv_const > 0.5 GWh/y
    # mobility_tech = list(Einv_const_dict['Mobility'].max(axis=0)[Einv_const_dict['Mobility'].max(axis=0) > 0.5].index)
    # plot_stacked_bar(df_data=Einv_const_dict['Mobility'][mobility_tech],
    #                  xlabel='GWP total [MtC02/y]', ylabel='[TWh]', ylim=ymax,
    #                  pdf_name=dir_plot+'/einv_const-mob-'+pdf+'.pdf')
    #
    #
    # ##############################################################################################################
    # # GWP breakdown by resources and technologies
    # # GHG emissions related to technologies
    # df_gwp_const_filtered = retrieve_non_zero_val(df=df_gwp_const.transpose())
    # gwp_const_by_tech_cat = gwp_const_per_category(df_gwp_const=df_gwp_const_filtered, user_data=config["user_data"])
    # tech_list = ['Electricity', 'Heat high temperature', 'Heat low temperature centralised',
    #              'Heat low temperature decentralised', 'Passenger public', 'Passenger private', 'Freight',
    #              'Synthetic fuels', 'Electricity storage', 'Thermal storage', 'Other storage']
    #
    # # Aggregate GWP_const by sectors: heat, storage, mobility, and electricity
    # df_gwp_const_by_cat = pd.concat([gwp_const_by_tech_cat[tech].sum(axis=1) for tech in tech_list], axis=1)
    # df_gwp_const_by_cat.columns = tech_list
    # df_1 = df_gwp_const_by_cat[['Heat high temperature', 'Heat low temperature centralised',
    #                             'Heat low temperature decentralised']].sum(axis=1)
    # df_1.name = 'Heat'
    # df_2 = df_gwp_const_by_cat[['Electricity storage', 'Thermal storage', 'Other storage']].sum(axis=1)
    # df_2.name = 'Storage'
    # df_3 = df_gwp_const_by_cat[['Passenger public','Passenger private', 'Freight']].sum(axis=1)
    # df_3.name = 'Mobility'
    # df_4 = df_gwp_const_by_cat[['Electricity', 'Synthetic fuels']]
    # df_gwp_const_concat = pd.concat([df_1, df_2, df_3, df_4], axis=1)
    # plot_stacked_bar(df_data=df_gwp_const_concat, xlabel='p [%]', ylabel='[MtC02/y]', ylim=9,
    #                  pdf_name=dir_plot + '/gwp_const-breakdown-' + pdf + '.pdf')
    #
    # # GHG emissions breakdown by resources
    # df_gwp_op_filtered = retrieve_non_zero_val(df=df_gwp_op.transpose())
    # new_cols = list(df_gwp_op_filtered.columns)
    # new_cols = replace_item_in_list(l=new_cols, item_old='ELECTRICITY', item_new='ELECTRICITY_IMPORT')
    # df_gwp_op_filtered.columns = new_cols
    # plot_stacked_bar(df_data=df_gwp_op_filtered, xlabel='p [%]', ylabel='[MtC02/y]', ylim=100,
    #                  pdf_name=dir_plot + '/gwp_op-breakdown-' + pdf + '.pdf')
    #
    #
    # ##################################################################################################################
    # # PLot assets installed capacities
    # df_assets.columns = np.round(x_gwp_tot_index, 1)
    # plot_asset_capacities_by_tech(df_assets=df_assets, pdf=pdf, user_data=config['user_data'],
    #                               dir_plot=dir_plot, xlabel='[MtC02/y]')
    #
    # ##############
    # #
    # df_EI_filtered = retrieve_non_zero_val(df=df_EI.drop(columns=['Subcategory']).transpose())
    # df_EI_percentage = df_EI_filtered.divide(df_EI_filtered.sum(axis=1), axis=0) * 100
    # df_EI_percentage.index = np.round(x_gwp_tot_index, 1)
