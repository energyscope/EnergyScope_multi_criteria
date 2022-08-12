# -*- coding: utf-8 -*-
"""
Results of system Einv_tot minimization with several scenarios computed by constraining GWP_tot
 with different GHG emissions targets.

@author: Jonathan Dumas
"""

# import yaml
import os

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt

# from sys import platform

from energyscope.utils import make_dir
# from energyscope.postprocessing import get_gwp, compute_fec, compute_einv_details, compute_primary_energy
# from projects.eroi_study.utils_plot import plot_two_series
from projects.eroi_study.utils_plot import plot_stacked_bar, plot_one_serie
from projects.eroi_study.utils_res import eroi_computation, res_details, gwp_computation, retrieve_non_zero_val,\
    retrieve_einv_const_by_categories, res_assets_capacity, gwp_breakdown, gwp_const_per_category, cost_computation
from projects.eroi_study.utils import load_config


def plot_asset_capacities_by_tech(assets_df: pd.DataFrame, user_data: str, save_dir: str, fn_subfix: str,
                                  xlabel: str = 'p (%)'):
    """
    Stacked bar plot of asset installed capacities by technology subcategories
     such as electricity, heat high temperature, etc.
    :param assets_df: data of asset installed capacities for all scenarios.
    :param user_data: user_data path.
    :param save_dir: path to directory where plots are saved
    :param fn_subfix: subfix of the name of the file where the plot is saved.
    :param xlabel: FIXME Complete
    """

    # Retrieve the list of technologies
    aux_tech_df = pd.read_csv(user_data + "/aux_technologies.csv", index_col=0)

    # Retrieve the list subcategory of technologies
    tech_subcategory_list = list(dict.fromkeys(list(aux_tech_df['Subcategory'])))
    tech_by_subcategory = dict()
    for cat in tech_subcategory_list:
        tech_by_subcategory[cat] = list(aux_tech_df[aux_tech_df['Subcategory'] == cat].index)

    # Retrieve for each technology subcategory the corresponding assets
    elec_tech_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Electricity']].transpose())
    elec_tech_df = rename_columns(df=elec_tech_df,
                                  old_col=['CCGT', 'PV', 'WIND_ONSHORE', 'WIND_OFFSHORE', 'HYDRO_RIVER'],
                                  new_col=['CCGT', 'PV', 'Wind onshore', 'Wind offshore', 'Hydro'])
    elec_storage_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Electricity storage']].transpose())
    elec_storage_df = rename_columns(df=elec_storage_df, old_col=['BATT_LI', 'BEV_BATT', 'PHS'],
                                     new_col=['Elec. battery', 'BEV', 'PHS'])
    thermal_storage_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Thermal storage']].transpose())
    thermal_storage_df = rename_columns(df=thermal_storage_df,
                                        old_col=['TS_DEC_HP_ELEC', 'TS_DEC_ADVCOGEN_GAS', 'TS_DEC_BOILER_GAS',
                                                 'TS_DHN_SEASONAL'],
                                        new_col=['DEC elec. HP', 'DEC FC CHP gas', 'DEC gas boiler', 'DHN seasonal'])
    other_storage_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Other storage']].transpose())
    other_storage_df = rename_columns(df=other_storage_df,
                                      old_col=['GAS_STORAGE', 'AMMONIA_STORAGE', 'METHANOL_STORAGE'],
                                      new_col=['Gas', 'Ammonia', 'Methanol'])
    synthetic_fuels_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Synthetic fuels']].transpose())
    synthetic_fuels_df = rename_columns(df=synthetic_fuels_df,
                                        old_col=['SMR', 'METHANE_TO_METHANOL', 'BIOMASS_TO_METHANOL', 'HABER_BOSCH',
                                                 'METHANOL_TO_HVC'],
                                        new_col=['Steam methane reforming', 'Methane to methanol',
                                                 'Biomass to methanol', 'H2 to ammonia',
                                                 'Methanol to HVC'])

    plot_stacked_bar(elec_tech_df, xlabel=xlabel, ylabel='Capacity [GWe]', ylim=90,
                     pdf_name=save_dir + '/f-elec-' + fn_subfix + '.pdf', ncol=1)
    plot_stacked_bar(elec_storage_df, xlabel=xlabel, ylabel='Capacity [GWh]', ylim=150,
                     pdf_name=save_dir + '/f-elec-storage-' + fn_subfix + '.pdf', ncol=1)
    plot_stacked_bar(thermal_storage_df, xlabel=xlabel, ylabel='Capacity [GWh]', ylim=1300,
                     pdf_name=save_dir + '/f-thermal-storage-' + fn_subfix + '.pdf', ncol=1)
    plot_stacked_bar(other_storage_df, xlabel=xlabel, ylabel='Capacity [GWh]', ylim=45000,
                     pdf_name=save_dir + '/f-other-storage-' + fn_subfix + '.pdf', ncol=1)
    plot_stacked_bar(synthetic_fuels_df, xlabel=xlabel, ylabel='Capacity [GW]', ylim=20,
                     pdf_name=save_dir + '/f-synthetic-fuels-' + fn_subfix + '.pdf', ncol=1)

    heat_low_dec_df = retrieve_non_zero_val(
        df=assets_df.loc[tech_by_subcategory['Heat low temperature decentralised']].transpose())
    heat_low_dec_df = rename_columns(df=heat_low_dec_df, old_col=['DEC_HP_ELEC', 'DEC_ADVCOGEN_GAS', 'DEC_BOILER_GAS'],
                                     new_col=['DEC HP', 'DEC gas FC', 'DEC gas boiler'])
    df_heat_low_dhn = retrieve_non_zero_val(
        df=assets_df.loc[tech_by_subcategory['Heat low temperature centralised']].transpose())
    heat_low_dhn_df = rename_columns(df=df_heat_low_dhn,
                                     old_col=['DHN_HP_ELEC', 'DHN_COGEN_GAS', 'DHN_COGEN_BIO_HYDROLYSIS',
                                              'DHN_BOILER_GAS', 'DHN_SOLAR'],
                                     new_col=['DHN HP', 'DHN gas CHP', 'DHN wet biomass CHP', 'DHN gas boiler',
                                              'DHN solar thermal'])
    heat_high_t_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Heat high temperature']].transpose())
    heat_high_t_df = rename_columns(df=heat_high_t_df,
                                    old_col=['IND_COGEN_GAS', 'IND_BOILER_GAS', 'IND_BOILER_WASTE', 'IND_DIRECT_ELEC'],
                                    new_col=['I gas CHP', 'I gas boiler', 'I waste boiler', 'I elec.'])

    plot_stacked_bar(heat_low_dec_df, xlabel=xlabel, ylabel='Capacity [GW]', ylim=35,
                     pdf_name=save_dir + '/f-heat-low-DEC-' + fn_subfix + '.pdf', ncol=1)
    plot_stacked_bar(heat_low_dhn_df, xlabel=xlabel, ylabel='Capacity [GW]', ylim=28,
                     pdf_name=save_dir + '/f-heat-low-DHN-' + fn_subfix + '.pdf', ncol=1)
    plot_stacked_bar(heat_high_t_df, xlabel=xlabel, ylabel='Capacity [GW]', ylim=25,
                     pdf_name=save_dir + '/f-heat-high-T-' + fn_subfix + '.pdf', ncol=1)

    df_mob_private = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Passenger private']].transpose())
    df_mob_private = rename_columns(df=df_mob_private, old_col=['CAR_NG', 'CAR_BEV'], new_col=['Gas car', 'Elec. car'])
    df_mob_public = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Passenger public']].transpose())
    df_mob_public = rename_columns(df=df_mob_public, old_col=['TRAMWAY_TROLLEY', 'BUS_COACH_CNG_STOICH', 'TRAIN_PUB'],
                                   new_col=['Tram or metro', 'Gas bus', 'Train'])
    df_mob_freight = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Freight']].transpose())
    df_mob_freight = rename_columns(df=df_mob_freight,
                                    old_col=['TRAIN_FREIGHT', 'BOAT_FREIGHT_NG', 'TRUCK_ELEC', 'TRUCK_NG'],
                                    new_col=['Train', 'Gas boat', 'Elec. truck', 'Gas truck'])

    plot_stacked_bar(df_mob_private, xlabel=xlabel, ylabel='Capacity [GW]', ylim=220,
                     pdf_name=save_dir + '/f-mob-private-' + fn_subfix + '.pdf', ncol=1)
    plot_stacked_bar(df_mob_public, xlabel=xlabel, ylabel='Capacity [GW]', ylim=40,
                     pdf_name=save_dir + '/f-mob-public-' + fn_subfix + '.pdf', ncol=1)
    plot_stacked_bar(df_mob_freight, xlabel=xlabel, ylabel='Capacity [GW]', ylim=95,
                     pdf_name=save_dir + '/f-freight-' + fn_subfix + '.pdf', ncol=1)


def fec_plots(fec_data_df: pd.DataFrame, save_dir: str, fn_subfix: str,):
    """
    FEC PLOTS
    """
    xlabel = 'Yearly emissions [MtC02/y]'
    plot_stacked_bar(fec_data_df.transpose(), xlabel=xlabel,  ylabel='[TWh]', ylim=520,
                     pdf_name=save_dir + '/fec-details-' + fn_subfix + '.pdf')

    # FEC detailed by EUD
    heat_list = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']
    fec_data_heat_df = fec_data_df.loc[heat_list].transpose().copy()
    fec_data_heat_df = rename_columns(df=fec_data_heat_df, old_col=heat_list,
                                      new_col=['Heat high T.', 'Heat low T. DHN', 'Heat low T. DEC'])
    plot_stacked_bar(fec_data_heat_df, xlabel=xlabel,  ylabel='FEC [TWh]', ylim=205,
                     pdf_name=save_dir + '/fec-details-heat-' + fn_subfix + '.pdf')

    mob_list = ['MOB_PUBLIC', 'MOB_PRIVATE', 'MOB_FREIGHT_RAIL', 'MOB_FREIGHT_BOAT', 'MOB_FREIGHT_ROAD']
    fec_data_mob_df = fec_data_df.loc[mob_list].transpose().copy()
    fec_data_mob_df = rename_columns(df=fec_data_mob_df, old_col=mob_list,
                                     new_col=['Mob. public', 'Mob. private', 'Mob. freight rail',
                                              'Mob. freight boat', 'Mob. freight road'])
    plot_stacked_bar(fec_data_mob_df, xlabel=xlabel, ylabel='FEC [TWh]', ylim=100,
                     pdf_name=save_dir + '/fec-details-mob-' + fn_subfix + '.pdf')

    non_energy_list = ['HVC', 'AMMONIA', 'METHANOL', 'ELECTRICITY']
    fec_data_non_energy_df = fec_data_df.loc[non_energy_list].transpose().copy()
    fec_data_non_energy_df = rename_columns(df=fec_data_non_energy_df, old_col=non_energy_list,
                                            new_col=['HVC', 'Ammonia', 'Methanol', 'Electricity'])
    plot_stacked_bar(fec_data_non_energy_df, xlabel=xlabel, ylabel='FEC [TWh]', ylim=200,
                     pdf_name=save_dir + '/fec-details-non-E-' + fn_subfix + '.pdf')


def rename_columns(df: pd.DataFrame, old_col: list, new_col: list):
    """
    Rename columns of a pd.DataFrame.
    """
    new_cols = list(df.columns)
    for item_old, item_new in zip(old_col, new_col):
        new_cols = replace_item_in_list(target_list=new_cols, item_old=item_old, item_new=item_new)
    df.columns = new_cols
    return df


def replace_item_in_list(target_list: list, item_old: str, item_new: str):
    """
    Replace a specific item into a list.
    """
    for i in range(len(target_list)):
        if target_list[i] == item_old:
            target_list[i] = item_new
    return target_list


def plot_series(cost_df, res_df, ei_df, x_gwp_tot_index, dir_plot, domestic_re_share):

    plot_one_serie(cost_df.sum(axis=1), label='Cost',
                   pdf_name=dir_plot + '/cost_' + str(domestic_re_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[40, 100], ylabel='[bEUR/y]')
    plot_one_serie(res_df['EROI'], label='EROI',
                   pdf_name=dir_plot + '/eroi_custom_' + str(domestic_re_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[1, 10], ylabel='[-]', yticks_val=[3, 5, 7, 9])
    plot_one_serie(res_df['EROI'], label='EROI',
                   pdf_name=dir_plot + '/eroi_' + str(domestic_re_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[2.5, 10], ylabel='[-]')
    plot_one_serie(res_df['FEC'], label='FEC',
                   pdf_name=dir_plot + '/fec_' + str(domestic_re_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[300, 480], ylabel='[TWh/y]')
    plot_one_serie(res_df['Einv'], label='Einv',
                   pdf_name=dir_plot + '/einv_' + str(domestic_re_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[30, 180], ylabel='[TWh/y]')
    plot_one_serie(ei_df.drop(columns=['Subcategory']).transpose().sum(axis=1), label='Primary energy',
                   pdf_name=dir_plot + '/EI_tot_' + str(domestic_re_share) + '.pdf',
                   x_index=x_gwp_tot_index, ylim=[350, 550], ylabel='[TWh/y]')


def plot_primary_energy(ei_df, ei_cat_df, res_renewable, res_non_renewable, x_gwp_tot_index, save_dir, fn_subfix):

    ei_cat_df = rename_columns(df=ei_cat_df.transpose(),
                               old_col=['Biofuel', 'Non-biomass', 'Other non-renewable', 'Fossil fuel'],
                               new_col=['RE-fuels', 'Wind+Solar', 'non-RE', 'Fossil'])
    ei_cat_df.index = np.round(x_gwp_tot_index, 1)
    # Waste+Methanol+Ammonia = other non-RE
    plot_stacked_bar(ei_cat_df.drop(columns=['Export']),
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]', ylim=600,
                     pdf_name=save_dir+'/EI-categories-'+fn_subfix+'.pdf')

    # Renewable RES: biofuel + biomass + non-biomass
    ei_res_re_df = retrieve_non_zero_val(df=ei_df.loc[res_renewable].drop(columns=['Subcategory']).transpose())
    ei_res_re_df = rename_columns(df=ei_res_re_df,
                                  old_col=['WET_BIOMASS', 'WOOD', 'METHANOL_RE', 'GAS_RE', 'AMMONIA_RE', 'H2_RE',
                                           'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO'],
                                  new_col=['Wet biomass', 'Wood', 'Methanol-RE', 'Gas-RE', 'Ammonia-RE', 'H2-RE',
                                           'Hydro', 'Solar', 'Wind', 'Geo'])
    # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    colors = plt.cm.tab20b(np.linspace(0, 1, 10))
    ei_res_re_df.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(ei_res_re_df[['Ammonia-RE', 'Methanol-RE', 'Gas-RE', 'Wet biomass', 'Wood',
                                   'Hydro', 'Solar', 'Wind']],
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]', ylim=530,
                     pdf_name=save_dir + '/EI-RE-' + fn_subfix + '.pdf', colors=colors)

    # Non-renewable RES: Fossil fuel + Other non-renewable

    colors = plt.cm.tab20c(np.linspace(0, 1, 10))
    ei_res_non_re_df = retrieve_non_zero_val(df=ei_df.loc[res_non_renewable].drop(columns=['Subcategory']).transpose())
    ei_res_non_re_df = rename_columns(df=ei_res_non_re_df,
                                      old_col=['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA',
                                               'H2', 'WASTE', 'METHANOL', 'URANIUM'],
                                      new_col=['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'NG', 'Elec. import', 'Ammonia',
                                               'H2', 'Waste', 'Methanol', 'URANIUM'])
    ei_res_non_re_df.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(ei_res_non_re_df, xlabel='Yearly emissions limit [MtCO2-eq./y]',
                     ylabel='Primary energy [TWh]', ylim=350, pdf_name=save_dir + '/EI-non-RE-' + fn_subfix + '.pdf',
                     colors=colors)


def plot_einv_op(einv_res_cat_df, einv_op_df, res_renewable, res_non_renewable, x_gwp_tot_index, save_dir, fn_subfix):

    # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel,
    # Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    einv_res_cat_df.columns = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(einv_res_cat_df.transpose(), xlabel='Yearly emissions limit [MtCO2-eq./y]',
                     ylabel='Operation energy [TWh]', ylim=160, pdf_name=save_dir+'/einv-res-'+fn_subfix+'.pdf')

    # Einv_op classed by RESOURCES (RE and non-RE)
    einv_op_filtered_df = retrieve_non_zero_val(df=einv_op_df.transpose())
    einv_op_filtered_df.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(einv_op_filtered_df,
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation energy [TWh]', ylim=160,
                     pdf_name=save_dir+'/einv-op-details-'+fn_subfix+'.pdf')

    # Einv_op by RE-RESOURCES
    einv_op_re_filtered_df = retrieve_non_zero_val(df=einv_op_df.loc[res_renewable].transpose())
    einv_op_re_filtered_df.index = np.round(x_gwp_tot_index, 1)
    einv_op_re_filtered_df = rename_columns(df=einv_op_re_filtered_df,
                                            old_col=['AMMONIA_RE', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD'],
                                            new_col=['Ammonia-RE', 'Methanol-RE', 'Gas-RE', 'Wet biomass', 'Wood'])
    plot_stacked_bar(einv_op_re_filtered_df,
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation energy [TWh]', ylim=160,
                     pdf_name=save_dir+'/einv-op-re-res-'+fn_subfix+'.pdf')

    # Einv_op by NON-RE-RESOURCES
    einv_op_non_re_filtered_df = retrieve_non_zero_val(df=einv_op_df.loc[res_non_renewable].transpose())
    einv_op_non_re_filtered_df.index = np.round(x_gwp_tot_index, 1)
    einv_op_non_re_filtered_df = rename_columns(df=einv_op_non_re_filtered_df,
                                                old_col=['GAS', 'ELECTRICITY', 'AMMONIA', 'WASTE', 'METHANOL'],
                                                new_col=['NG', 'Elec. import', 'Ammonia', 'Waste', 'Methanol'])
    plot_stacked_bar(einv_op_non_re_filtered_df,
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation energy [TWh]', ylim=30,
                     pdf_name=save_dir+'/einv-op-non-re-res-'+fn_subfix+'.pdf')


def plot_einv_const(einv_tech_cat_df, einv_const_dict, x_gwp_tot_index, save_dir, fn_subfix):

    # 2. Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    einv_tech_cat_df.columns = np.round(x_gwp_tot_index, 1)
    einv_tech_cat_df = rename_columns(df=einv_tech_cat_df.transpose(),
                                      old_col=['Electricity', 'Heat', 'Mobility', 'Infrastructure',
                                               'Synthetic fuels', 'Storage'],
                                      new_col=['Electricity', 'Heat', 'Mobility', 'Infrastructure',
                                               'RE fuels', 'Storage'])
    plot_stacked_bar(einv_tech_cat_df.drop(columns=['Infrastructure']),
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Construction energy [TWh]', ylim=35,
                     pdf_name=save_dir+'/einv-tech-'+fn_subfix+'.pdf')

    # Einv_const classed by categories of technologies: 'Electricity', 'Heat', 'Mobility',
    # 'Infrastructure', 'Synthetic fuels', 'Storage'
    einv_const_dict['Electricity'].index = np.round(x_gwp_tot_index, 1)
    ymax_elec = einv_const_dict['Electricity'].sum(axis=1).max() * 1.05
    elec_tech = list(einv_const_dict['Electricity'].max(axis=0)[einv_const_dict['Electricity'].max(axis=0) > 0.1].index)
    einv_constr_elec_tech_df = einv_const_dict['Electricity'][elec_tech].copy()
    einv_constr_elec_tech_df = rename_columns(df=einv_constr_elec_tech_df,
                                              old_col=['CCGT', 'PV', 'WIND_ONSHORE', 'WIND_OFFSHORE'],
                                              new_col=['CCGT', 'PV', 'Onshore wind', 'Offshore wind'])
    plot_stacked_bar(einv_constr_elec_tech_df,
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Construction energy [TWh]', ylim=ymax_elec,
                     pdf_name=save_dir+'/einv_const-elec-'+fn_subfix+'.pdf')

    einv_const_dict['Mobility'].index = np.round(x_gwp_tot_index, 1)
    ymax_mob = einv_const_dict['Mobility'].sum(axis=1).max() * 1.05
    # select only the mobility technologies with Einv_const > 0.5 GWh/y
    mobility_tech = list(einv_const_dict['Mobility'].max(axis=0)[einv_const_dict['Mobility'].max(axis=0) > 0.5].index)
    einv_constr_mob_tech_df = einv_const_dict['Mobility'][mobility_tech].copy()
    einv_constr_mob_tech_df = rename_columns(df=einv_constr_mob_tech_df,
                                             old_col=['CAR_NG', 'CAR_BEV', 'TRUCK_ELEC', 'TRUCK_NG'],
                                             new_col=['Gas car', 'Elec. car', 'Elec. truck', 'Gas truck'])
    plot_stacked_bar(einv_constr_mob_tech_df,
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Construction energy [TWh]', ylim=ymax_mob,
                     pdf_name=save_dir+'/einv_const-mob-'+fn_subfix+'.pdf')


def plot_gwp(gwp_op_df, gwp_const_df, x_gwp_tot_index, user_data_dir, save_dir, fn_subfix):

    gwp_const_filtered_df = retrieve_non_zero_val(df=gwp_const_df.transpose())
    gwp_const_by_tech_cat = gwp_const_per_category(gwp_const_df=gwp_const_filtered_df, user_data_dir=user_data_dir)
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
    gwp_const_concat_df.index = np.round(x_gwp_tot_index, 1)
    pdf_name = os.path.join(save_dir, f"gwp_const-breakdown-{fn_subfix}.pdf")
    plot_stacked_bar(gwp_const_concat_df,
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Construction emissions [MtCO2-eq./y]',
                     ylim=9, pdf_name=pdf_name)

    # GHG emissions breakdown by resources
    gwp_op_filtered_df = retrieve_non_zero_val(df=gwp_op_df.transpose())
    gwp_op_filtered_df = rename_columns(df=gwp_op_filtered_df,
                                        old_col=['AMMONIA', 'ELECTRICITY', 'GAS', 'METHANOL', 'WASTE',
                                                 'WET_BIOMASS', 'WOOD'],
                                        new_col=['Ammonia', 'Elec. import', 'NG', 'Methanol', 'Waste',
                                                 'Wet biomass', 'Wood'])
    gwp_op_filtered_df.index = np.round(x_gwp_tot_index, 1)
    pdf_name = os.path.join(save_dir, f"gwp_op-breakdown-{fn_subfix}.pdf")
    plot_stacked_bar(gwp_op_filtered_df,
                     xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation emissions [MtCO2-eq./y]',
                     ylim=100, pdf_name=pdf_name)


def plot_asset_capacities_by_tech_line(assets_df: pd.DataFrame, user_data_dir: str, save_dir: str, fn_subfix: str,
                                       xlabel: str = 'p (%)'):
    """
    Line plot of asset installed capacities by technology subcategories
    such as electricity, heat high temperature, etc.
    :param assets_df: data of asset installed capacities for all scenarios.
    :param user_data_dir: user_data path.
    :param save_dir: path to directory where the plots are saved
    :param fn_subfix: subfix of the file names where the plots are stored.
    :param xlabel: FIXME: complete
    """

    # Retrieve the list of technologies
    aux_tech_df = pd.read_csv(user_data_dir + "/aux_technologies.csv", index_col=0)

    # Retrieve the list subcategory of technologies
    tech_subcategory_list = list(dict.fromkeys(list(aux_tech_df['Subcategory'])))
    tech_by_subcategory = dict()
    for cat in tech_subcategory_list:
        tech_by_subcategory[cat] = list(aux_tech_df[aux_tech_df['Subcategory'] == cat].index)

    # Retrieve for each technology subcategory the corresponding assets
    elec_tech_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Electricity']].transpose())
    heat_low_dec_df = retrieve_non_zero_val(
        df=assets_df.loc[tech_by_subcategory['Heat low temperature decentralised']].transpose())
    heat_low_dhn_df = retrieve_non_zero_val(
        df=assets_df.loc[tech_by_subcategory['Heat low temperature centralised']].transpose())
    heat_high_t_df = retrieve_non_zero_val(
        df=assets_df.loc[tech_by_subcategory['Heat high temperature']].transpose())
    synthetic_fuels_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Synthetic fuels']].transpose())
    elec_storage_df = retrieve_non_zero_val(
        df=assets_df.loc[tech_by_subcategory['Electricity storage']].transpose())
    thermal_storage_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Thermal storage']].transpose())
    # FIXME: variable are not used
    mob_private_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Passenger private']].transpose())
    mob_public_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Passenger public']].transpose())
    mob_freight_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Freight']].transpose())
    other_storage_df = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Other storage']].transpose())

    x_index = list(elec_tech_df.index)
    # Installed capacity for electricity production for different scenarios (hydro is removed because too small)
    plt.figure()
    plt.plot(x_index, elec_tech_df['PV'].values, '-D', color='gold', linewidth=3, markersize=5, label='PV')
    plt.plot(x_index, elec_tech_df['WIND_ONSHORE'].values + elec_tech_df['WIND_ONSHORE'].values, '-Dg', linewidth=3,
             markersize=5, label='Wind')
    plt.plot(x_index, elec_tech_df['CCGT'].values, '-Dk', linewidth=3, markersize=5, label='CCGT')
    plt.plot(x_index, heat_high_t_df['IND_COGEN_GAS'].values + heat_low_dhn_df['DHN_COGEN_GAS'].values, '--P',
             color='orange', linewidth=3, markersize=5, label='IND. +DHN gas CHP')
    plt.plot(x_index, heat_low_dhn_df['DHN_COGEN_BIO_HYDROLYSIS'].values, '--P', color='brown', linewidth=3,
             markersize=5, label='Bio. hydro. CHP')
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(save_dir + '/f-elec-line-' + fn_subfix + '.pdf')
    plt.show()

    # Installed capacity for decentralised low temperature heat production for different scenarios.
    plt.figure()
    plt.plot(x_index, heat_low_dec_df['DEC_HP_ELEC'].values, '-D', linewidth=3, markersize=5, label='Heat pumps')
    # plt.plot(x_index, heat_low_dec_df['DEC_ADVCOGEN_GAS'].values,
    #          '-D', linewidth=3, markersize=5, label='DEC_ADVCOGEN_GAS')
    plt.plot(x_index, heat_low_dec_df['DEC_BOILER_GAS'].values,
             '-D', linewidth=3, markersize=5, label='Gas boilers')
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(save_dir + '/f-heat-low-DEC-line-' + fn_subfix + '.pdf')
    plt.show()

    # Installed capacity for centralised low temperature heat production for different scenarios.
    plt.figure()
    plt.plot(x_index, heat_low_dhn_df['DHN_HP_ELEC'].values, '-D', linewidth=3, markersize=5, label='Heat pumps')
    plt.plot(x_index, heat_low_dhn_df['DHN_BOILER_GAS'].values,
             '-D', linewidth=3, markersize=5, label='Gas boilers')
    plt.plot(x_index, heat_low_dhn_df['DHN_COGEN_GAS'].values, '-D', linewidth=3, markersize=5, label='Gas CHP')
    plt.plot(x_index, heat_low_dhn_df['DHN_COGEN_BIO_HYDROLYSIS'].values,
             '-D', linewidth=3, markersize=5, label='Bio. hydro. CHP')
    plt.plot(x_index, heat_low_dhn_df['DHN_SOLAR'].values, '-D', linewidth=3, markersize=5, label='Solar')
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(save_dir + '/f-heat-low-DHN-line-' + fn_subfix + '.pdf')
    plt.show()

    # Installed capacity for industrial heat production for different scenarios.
    plt.figure()
    plt.plot(x_index, heat_high_t_df['IND_BOILER_WASTE'].values,
             '-D', linewidth=3, markersize=5, label='Waste boilers')
    plt.plot(x_index, heat_high_t_df['IND_BOILER_GAS'].values, '-D', linewidth=3, markersize=5, label='Gas boilers')
    plt.plot(x_index, heat_high_t_df['IND_COGEN_GAS'].values, '-D', linewidth=3, markersize=5, label='Gas CHP')
    plt.plot(x_index, heat_high_t_df['IND_DIRECT_ELEC'].values,
             '-D', linewidth=3, markersize=5, label='Direct electricity')
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(save_dir + '/f-heat-high-T-line-' + fn_subfix + '.pdf')
    plt.show()

    # Installed capacity for synthetic gas production for different scenarios.
    plt.figure()
    plt.plot(x_index, synthetic_fuels_df['SMR'].values, '-D', linewidth=3, markersize=5, label='Methane reforming')
    plt.plot(x_index, synthetic_fuels_df['METHANE_TO_METHANOL'].values,
             '-D', linewidth=3, markersize=5, label='Methane to methanol')
    plt.plot(x_index, synthetic_fuels_df['BIOMASS_TO_METHANOL'].values,
             '-D', linewidth=3, markersize=5, label='Biomass methanolation')
    plt.plot(x_index, synthetic_fuels_df['HABER_BOSCH'].values,
             '-D', linewidth=3, markersize=5, label='Haber Bosch')
    plt.plot(x_index, synthetic_fuels_df['METHANOL_TO_HVC'].values,
             '-D', linewidth=3, markersize=5, label='Methanol to HVC')
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(save_dir + '/f-synthetic-fuels-line-' + fn_subfix + '.pdf')
    plt.show()

    # Installed storage capacity for different scenarios.
    plt.figure()
    plt.plot(x_index, thermal_storage_df['TS_DEC_HP_ELEC'].values,
             '-D', linewidth=3, markersize=5, label='TS DEC HP')
    plt.plot(x_index, thermal_storage_df['TS_DEC_ADVCOGEN_GAS'].values,
             '-D', linewidth=3, markersize=5, label='TS DEC FC CHP gas')
    plt.plot(x_index, thermal_storage_df['TS_DEC_BOILER_GAS'].values,
             '-D', linewidth=3, markersize=5, label='TS DEC boiler gas')
    plt.plot(x_index, thermal_storage_df['TS_DHN_SEASONAL'].values, '-D', linewidth=3, markersize=5, label='TS DHN')
    plt.plot(x_index, other_storage_df['GAS_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Gas')
    plt.plot(x_index, other_storage_df['AMMONIA_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Ammonia')
    plt.plot(x_index, other_storage_df['METHANOL_STORAGE'].values,
             '-P', linewidth=3, markersize=5, label='Methanol')
    plt.plot(x_index, elec_storage_df['PHS'].values, '-+', linewidth=3, markersize=5, label='PHS')
    plt.plot(x_index, elec_storage_df['BATT_LI'].values, '-+', linewidth=3, markersize=5, label='LI Batteries')
    plt.plot(x_index, elec_storage_df['BEV_BATT'].values, '-+', linewidth=3, markersize=5, label='BEV batteries')
    plt.xlabel(xlabel, fontsize=15)
    plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(save_dir + '/f-storages-line-' + fn_subfix + '.pdf')
    plt.show()

    # # Installed storage capacity for different scenarios.
    # plt.figure()
    # plt.plot(x_index, thermal_storage_df['TS_DEC_HP_ELEC'].values,
    #          '-D', linewidth=3, markersize=5, label='TS DEC HP')
    # plt.plot(x_index, thermal_storage_df['TS_DEC_ADVCOGEN_GAS'].values,
    #          '-D', linewidth=3, markersize=5, label='TS DEC FC CHP gas')
    # plt.plot(x_index, thermal_storage_df['TS_DEC_BOILER_GAS'].values,
    #          '-D', linewidth=3, markersize=5, label='TS DEC boiler gas')
    # plt.plot(x_index, thermal_storage_df['TS_DHN_SEASONAL'].values,
    #          '-D', linewidth=3, markersize=5, label='TS DHN')
    # plt.plot(x_index, other_storage_df['GAS_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Gas')
    # plt.plot(x_index, other_storage_df['AMMONIA_STORAGE'].values,
    #          '-P', linewidth=3, markersize=5, label='Ammonia')
    # plt.plot(x_index, other_storage_df['METHANOL_STORAGE'].values,
    #          '-P', linewidth=3, markersize=5, label='Methanol')
    # plt.plot(x_index, elec_storage_df['PHS'].values, '-+', linewidth=3, markersize=5, label='PHS')
    # plt.plot(x_index, elec_storage_df['BATT_LI'].values, '-+', linewidth=3, markersize=5, label='LI Batteries')
    # plt.plot(x_index, elec_storage_df['BEV_BATT'].values, '-+', linewidth=3, markersize=5, label='BEV batteries')
    # plt.xlabel(xlabel, fontsize=15)
    # plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
    # plt.gca().invert_xaxis()
    # plt.xticks(fontsize=15)
    # plt.yticks(fontsize=15)
    # plt.legend(fontsize=15)
    # plt.tight_layout()
    # plt.savefig(save_dir+ '/f-storages-line-' + fn_subfix + '.pdf')
    # plt.show()


def print_share_of_energies(ei_df, gwp_df, res_df, assets_df):
    for p in range(100, 0, -5):
        tot_ei = ei_df[p].sum()
        print('GWP_tot %.1f [MtCO2-eq./y]: EROI %.1f offshore %.1f [GW] onshore %.1f [GW] PV %.1f [GW] NUC %.1f [GW]' %
              (gwp_df.sum(axis=1).loc[p], res_df['EROI'].loc[p], assets_df[p].loc['WIND_OFFSHORE'],
               assets_df[p].loc['WIND_ONSHORE'], assets_df[p].loc['PV'], assets_df[p]['NUCLEAR']))
        print('GWh: Gas %.1f METHANOL_RE %.1f AMMONIA_RE %.1f H2_RE %.1f '
              'Gas-re %.1f PV %.1f Wind %.1f wood %.1f wet biomass %.1f waste %.1f'
              % (ei_df[p]['GAS'],  ei_df[p]['METHANOL_RE'],  ei_df[p]['AMMONIA_RE'],  ei_df[p]['H2_RE'],
                 ei_df[p]['GAS_RE'],  ei_df[p]['RES_SOLAR'],  ei_df[p]['RES_WIND'],  ei_df[p]['WOOD'],
                 ei_df[p]['WET_BIOMASS'],   ei_df[p]['WASTE']))
        print('Percentage: Gas %.1f METHANOL_RE %.1f AMMONIA_RE %.1f H2_RE %.1f '
              'Gas-re %.1f PV %.1f Wind %.1f wood %.1f wet biomass %.1f waste %.1f'
              % (100 * ei_df[p]['GAS'] / tot_ei, 100 * ei_df[p]['METHANOL_RE'] / tot_ei,
                 100 * ei_df[p]['AMMONIA_RE'] / tot_ei, 100 * ei_df[p]['H2_RE'] / tot_ei,
                 100 * ei_df[p]['GAS_RE'] / tot_ei, 100 * ei_df[p]['RES_SOLAR'] / tot_ei,
                 100 * ei_df[p]['RES_WIND'] / tot_ei, 100 * ei_df[p]['WOOD'] / tot_ei,
                 100 * ei_df[p]['WET_BIOMASS'] / tot_ei,  100 * ei_df[p]['WASTE'] / tot_ei))


def main(config_fn, domestic_re_share):

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn=config_fn+'.yaml')

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
        dir_name = f"{config['case_studies_dir']}/{'einv_GWP_tot_2_GW_nuc_' + str(domestic_re_share)}"
    elif config_fn == 'config_2035_5_6_GW_nuc':
        dir_name = f"{config['case_studies_dir']}/{'einv_GWP_tot_5_6_GW_nuc_' + str(domestic_re_share)}"
    else:
        dir_name = f"{config['case_studies_dir']}/{'einv_GWP_tot_' + str(domestic_re_share)}"

    res_df, fec_details_df = \
        eroi_computation(dir_name=dir_name, user_data_dir=config['user_data'], range_val=range_val)
    einv_op_df, einv_res_cat_df, einv_tech_cat_df, ei_cat_df, ei_df = \
        res_details(range_val=range_val, all_data=all_data, dir_name=dir_name, user_data=config['user_data'])
    gwp_df = gwp_computation(dir_name=dir_name, range_val=range_val)
    x_gwp_tot_index = gwp_df.sum(axis=1).values
    cost_df = cost_computation(dir_name=dir_name, range_val=range_val)
    einv_const_dict = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data, dir_name=dir_name,
                                                        user_data=config['user_data'])
    assets_df = res_assets_capacity(range_val=range_val, dir_name=dir_name)
    gwp_const_df, gwp_op_df = gwp_breakdown(dir_name=dir_name, range_val=range_val)

    ######
    # Share of energies
    if 0:
        print_share_of_energies(ei_df, gwp_df, res_df, assets_df)

    ####################################################################################################################
    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    ####################################################################################################################
    if config_fn == 'config_2035_2_GW_nuc':
        dir_plot = 'einv_GWP_tot_2_GW_nuc_' + str(domestic_re_share)
    elif config_fn == 'config_2035_5_6_GW_nuc':
        dir_plot = 'einv_GWP_tot_5_6_GW_nuc_' + str(domestic_re_share)
    else:
        dir_plot = 'einv_GWP_tot_' + str(domestic_re_share)
    fn_subfix = 'gwp-tot-' + str(domestic_re_share)

    main_export_dir = os.path.join(cwd, 'export')
    make_dir(main_export_dir)
    save_dir = os.path.join(main_export_dir, dir_plot)
    make_dir(save_dir)

    ####################################################################################################################
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    # df_eroi = res_df['EROI'].copy()
    # df_eroi.index = x_gwp_tot_index_
    if 0:
        plot_series(cost_df, res_df, ei_df, x_gwp_tot_index, save_dir, domestic_re_share)

    ####################################################################################################################
    # FEC
    fec_details_df.columns = np.round(x_gwp_tot_index, 1)
    if 0:
        fec_plots(fec_data_df=fec_details_df, save_dir=save_dir, fn_subfix=fn_subfix)

    ####################################################################################################################
    # PRIMARY ENERGY

    res_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD',
                     'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    res_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2',
                         'WASTE', 'METHANOL', 'URANIUM']
    if 0:
        plot_primary_energy(ei_df, ei_cat_df, res_renewable, res_non_renewable, x_gwp_tot_index, save_dir, fn_subfix)

    ####################################################################################################################
    # Einv_tot = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)
    if 0:
        plot_einv_op(einv_res_cat_df, einv_op_df, res_renewable, res_non_renewable, x_gwp_tot_index, save_dir, fn_subfix)
        plot_einv_const(einv_tech_cat_df, einv_const_dict, x_gwp_tot_index, save_dir, fn_subfix)

    ##############################################################################################################
    # GWP breakdown by resources and technologies
    # GHG emissions related to technologies
    plot_gwp(gwp_op_df, gwp_const_df, x_gwp_tot_index, config["user_data"], save_dir, fn_subfix)
    exit()

    ####################################################################################################################
    # Plot assets installed capacities with stacked bars
    assets_df_.columns = np.round(x_gwp_tot_index, 1)
    plot_asset_capacities_by_tech(assets_df=assets_df, user_data=config['user_data'],
                                  save_dir=save_dir, fn_subfix=fn_subfix,
                                  xlabel='Yearly emissions limit [MtCO2-eq./y]')

    ####################################################################################################################
    # Plot assets installed capacities with lines
    # plot_asset_capacities_by_tech_line(assets_df=assets_df, user_data_dir=config['user_data'],
    #                                    save_dir=save_dir, fn_subfix=fn_subfix, xlabel='Yearly emissions [MtC02]')

    ##############
    #
    # ei_filtered_df = retrieve_non_zero_val(df=ei_df_.drop(columns=['Subcategory']).transpose())
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
    #
    # layer_gas_5_df = pd.read_csv(dir_name + '/run_5/' + "/output/hourly_data/layer_GAS.csv",
    #                              index_col=0).dropna(axis=1)
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
