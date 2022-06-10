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

from energyscope.utils import make_dir, load_config
from projects.eroi_study.utils_plot import plot_two_series, plot_stacked_bar, plot_one_serie
from projects.eroi_study.utils_res import compute_fec, get_gwp, compute_einv_details, compute_primary_energy, \
    eroi_computation, res_details, gwp_computation, retrieve_non_zero_val, retrieve_einv_const_by_categories, \
    res_assets_capacity, gwp_breakdown, gwp_const_per_category, cost_computation

def plot_asset_capacities_by_tech(df_assets: pd.DataFrame, pdf: str, user_data: str, dir_plot: str,
                                  xlabel: str = 'p (%)'):
    """
    Stacked bar plot of asset installed capacities by technology subcategories such as electricity, heat high temperature, etc.
    :param df_assets: data of asset installed capacities for all scenarios.
    :param pdf: pdf name.
    :param user_data: user_data path.
    """

    # Retrieve the list of technologies
    df_aux_tech = pd.read_csv(user_data + "/aux_technologies.csv", index_col=0)

    # Retrieve the list subcategory of technologies
    tech_subcategory_list = list(dict.fromkeys(list(df_aux_tech['Subcategory'])))
    tech_by_subcategory = dict()
    for cat in tech_subcategory_list:
        tech_by_subcategory[cat] = list(df_aux_tech[df_aux_tech['Subcategory'] == cat].index)

    # Retrieve for each technology subcategory the corresponding assets
    df_elec_tech = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Electricity']].transpose())
    df_elec_tech = rename_columns(df=df_elec_tech,
                                  old_col=['CCGT', 'PV', 'WIND_ONSHORE', 'WIND_OFFSHORE', 'HYDRO_RIVER'],
                                  new_col=['CCGT', 'PV', 'Wind onshore', 'Wind offshore', 'Hydro'])
    df_elec_storage = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Electricity storage']].transpose())
    df_elec_storage = rename_columns(df=df_elec_storage, old_col=['BATT_LI', 'BEV_BATT', 'PHS'],
                                     new_col=['Elec. battery', 'BEV', 'PHS'])
    df_thermal_storage = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Thermal storage']].transpose())
    df_thermal_storage = rename_columns(df=df_thermal_storage,
                                        old_col=['TS_DEC_HP_ELEC', 'TS_DEC_ADVCOGEN_GAS', 'TS_DEC_BOILER_GAS',
                                                 'TS_DHN_SEASONAL'],
                                        new_col=['DEC elec. HP', 'DEC FC CHP gas', 'DEC gas boiler', 'DHN seasonal'])
    df_other_storage = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Other storage']].transpose())
    df_other_storage = rename_columns(df=df_other_storage,
                                      old_col=['GAS_STORAGE', 'AMMONIA_STORAGE', 'METHANOL_STORAGE'],
                                      new_col=['Gas', 'Ammonia', 'Methanol'])
    df_synthetic_fuels = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Synthetic fuels']].transpose())
    df_synthetic_fuels = rename_columns(df=df_synthetic_fuels,
                                        old_col=['SMR', 'METHANE_TO_METHANOL', 'BIOMASS_TO_METHANOL', 'HABER_BOSCH',
                                                 'METHANOL_TO_HVC'],
                                        new_col=['Steam methane reforming', 'Methane to methanol',
                                                 'Biomass to methanol', 'H2 to ammonia',
                                                 'Methanol to HVC'])

    plot_stacked_bar(df_data=df_elec_tech, xlabel=xlabel, ylabel='Capacity [GWe]', ylim=90,
                     pdf_name=dir_plot + '/f-elec-' + pdf + '.pdf', ncol=1)
    plot_stacked_bar(df_data=df_elec_storage, xlabel=xlabel, ylabel='Capacity [GWh]', ylim=150,
                     pdf_name=dir_plot + '/f-elec-storage-' + pdf + '.pdf', ncol=1)
    plot_stacked_bar(df_data=df_thermal_storage, xlabel=xlabel, ylabel='Capacity [GWh]', ylim=1300,
                     pdf_name=dir_plot + '/f-thermal-storage-' + pdf + '.pdf', ncol=1)
    plot_stacked_bar(df_data=df_other_storage, xlabel=xlabel, ylabel='Capacity [GWh]', ylim=45000,
                     pdf_name=dir_plot + '/f-other-storage-' + pdf + '.pdf', ncol=1)
    plot_stacked_bar(df_data=df_synthetic_fuels, xlabel=xlabel, ylabel='Capacity [GW]', ylim=20,
                     pdf_name=dir_plot + '/f-synthetic-fuels-' + pdf + '.pdf', ncol=1)

    df_heat_low_DEC = retrieve_non_zero_val(
        df=df_assets.loc[tech_by_subcategory['Heat low temperature decentralised']].transpose())
    df_heat_low_DEC = rename_columns(df=df_heat_low_DEC, old_col=['DEC_HP_ELEC', 'DEC_ADVCOGEN_GAS', 'DEC_BOILER_GAS'],
                                     new_col=['DEC HP', 'DEC gas FC', 'DEC gas boiler'])
    df_heat_low_DHN = retrieve_non_zero_val(
        df=df_assets.loc[tech_by_subcategory['Heat low temperature centralised']].transpose())
    df_heat_low_DHN = rename_columns(df=df_heat_low_DHN,
                                     old_col=['DHN_HP_ELEC', 'DHN_COGEN_GAS', 'DHN_COGEN_BIO_HYDROLYSIS',
                                              'DHN_BOILER_GAS', 'DHN_SOLAR'],
                                     new_col=['DHN HP', 'DHN gas CHP', 'DHN wet biomass CHP', 'DHN gas boiler',
                                              'DHN solar thermal'])
    df_heat_high_T = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Heat high temperature']].transpose())
    df_heat_high_T = rename_columns(df=df_heat_high_T,
                                    old_col=['IND_COGEN_GAS', 'IND_BOILER_GAS', 'IND_BOILER_WASTE', 'IND_DIRECT_ELEC'],
                                    new_col=['I gas CHP', 'I gas boiler', 'I waste boiler', 'I elec.'])

    plot_stacked_bar(df_data=df_heat_low_DEC, xlabel=xlabel, ylabel='Capacity [GW]', ylim=35,
                     pdf_name=dir_plot + '/f-heat-low-DEC-' + pdf + '.pdf', ncol=1)
    plot_stacked_bar(df_data=df_heat_low_DHN, xlabel=xlabel, ylabel='Capacity [GW]', ylim=28,
                     pdf_name=dir_plot + '/f-heat-low-DHN-' + pdf + '.pdf', ncol=1)
    plot_stacked_bar(df_data=df_heat_high_T, xlabel=xlabel, ylabel='Capacity [GW]', ylim=25,
                     pdf_name=dir_plot + '/f-heat-high-T-' + pdf + '.pdf', ncol=1)

    df_mob_private = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Passenger private']].transpose())
    df_mob_private = rename_columns(df=df_mob_private, old_col=['CAR_NG', 'CAR_BEV'], new_col=['Gas car', 'Elec. car'])
    df_mob_public = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Passenger public']].transpose())
    df_mob_public = rename_columns(df=df_mob_public, old_col=['TRAMWAY_TROLLEY', 'BUS_COACH_CNG_STOICH', 'TRAIN_PUB'],
                                   new_col=['Tram or metro', 'Gas bus', 'Train'])
    df_mob_freight = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Freight']].transpose())
    df_mob_freight = rename_columns(df=df_mob_freight,
                                    old_col=['TRAIN_FREIGHT', 'BOAT_FREIGHT_NG', 'TRUCK_ELEC', 'TRUCK_NG'],
                                    new_col=['Train', 'Gas boat', 'Elec. truck', 'Gas truck'])

    plot_stacked_bar(df_data=df_mob_private, xlabel=xlabel, ylabel='Capacity [GW]', ylim=220,
                     pdf_name=dir_plot + '/f-mob-private-' + pdf + '.pdf', ncol=1)
    plot_stacked_bar(df_data=df_mob_public, xlabel=xlabel, ylabel='Capacity [GW]', ylim=40,
                     pdf_name=dir_plot + '/f-mob-public-' + pdf + '.pdf', ncol=1)
    plot_stacked_bar(df_data=df_mob_freight, xlabel=xlabel, ylabel='Capacity [GW]', ylim=95,
                     pdf_name=dir_plot + '/f-freight-' + pdf + '.pdf', ncol=1)


def fec_plots(df_fec_data: pd.DataFrame, pdf: str, dir_plot: str):
    """
    FEC PLOTS
    """
    xlabel= 'Yearly emissions [MtC02/y]'
    plot_stacked_bar(df_data=df_fec_data.transpose(), xlabel=xlabel,  ylabel='[TWh]', ylim=520, pdf_name=dir_plot + '/fec-details-' + pdf + '.pdf')

    # FEC detailed by EUD
    heat_list = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']
    df_fec_data_heat = df_fec_data.loc[heat_list].transpose().copy()
    df_fec_data_heat = rename_columns(df=df_fec_data_heat, old_col=heat_list, new_col=['Heat high T.', 'Heat low T. DHN', 'Heat low T. DEC'])
    plot_stacked_bar(df_data=df_fec_data_heat, xlabel=xlabel,  ylabel='FEC [TWh]', ylim=205, pdf_name=dir_plot + '/fec-details-heat-' + pdf + '.pdf')

    mob_list = ['MOB_PUBLIC', 'MOB_PRIVATE', 'MOB_FREIGHT_RAIL', 'MOB_FREIGHT_BOAT', 'MOB_FREIGHT_ROAD']
    df_fec_data_mob = df_fec_data.loc[mob_list].transpose().copy()
    df_fec_data_mob = rename_columns(df=df_fec_data_mob, old_col=mob_list, new_col=['Mob. public', 'Mob. private', 'Mob. freight rail', 'Mob. freight boat', 'Mob. freight road'])
    plot_stacked_bar(df_data=df_fec_data_mob, xlabel=xlabel, ylabel='FEC [TWh]', ylim=100, pdf_name=dir_plot + '/fec-details-mob-' + pdf + '.pdf')

    non_energy_list = ['HVC', 'AMMONIA', 'METHANOL', 'ELECTRICITY']
    df_fec_data_non_energy = df_fec_data.loc[non_energy_list].transpose().copy()
    df_fec_data_non_energy = rename_columns(df=df_fec_data_non_energy, old_col=non_energy_list, new_col=['HVC', 'Ammonia', 'Methanol', 'Electricity'])
    plot_stacked_bar(df_data=df_fec_data_non_energy, xlabel=xlabel, ylabel='FEC [TWh]', ylim=200,    pdf_name=dir_plot + '/fec-details-non-E-' + pdf + '.pdf')


def rename_columns(df: pd.DataFrame, old_col: list, new_col: list):
    """
    Rename columns of a pd.DataFrame.
    """
    new_cols = list(df.columns)
    for item_old, item_new in zip(old_col, new_col):
        new_cols = replace_item_in_list(l=new_cols, item_old=item_old, item_new=item_new)
    df.columns = new_cols
    return df

def replace_item_in_list(l: list, item_old: str, item_new: str):
    """
    Replace a specific item into a list.
    """
    for i in range(len(l)):
        if l[i] == item_old:
            l[i] = item_new
    return l


# parameters
domestic_RE_share = 0 # 0, 30 %
config_name_file = 'config_2035_with_nuc' # config_2035, config_2035_with_nuc

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
    if config_name_file == 'config_2035_with_nuc':
        dir = f"{config['case_studies_dir']}/{'einv_GWP_tot_nuc_' + str(domestic_RE_share)}"
    else:
        dir = f"{config['case_studies_dir']}/{'einv_GWP_tot_' + str(domestic_RE_share)}"

    df_res, df_fec_details = eroi_computation(dir=dir, user_data=config['user_data'], range_val=range_val)
    df_Einv_op, df_Einv_RES_cat, df_Einv_TECH_cat, df_EI_cat, df_EI = res_details(range_val=range_val, all_data=all_data, dir=dir, user_data=config['user_data'])
    df_GWP = gwp_computation(dir=dir, range_val=range_val)
    df_cost = cost_computation(dir=dir, range_val=range_val)
    Einv_const_dict = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data, dir=dir, user_data=config['user_data'])
    df_assets = res_assets_capacity(range_val=range_val, dir=dir)
    df_gwp_const, df_gwp_op = gwp_breakdown(dir=dir, range_val=range_val)

    ######
    # Share of energies
    for p in range(100, 0, -5):
        tot_EI = df_EI[p].sum()
        print('GWP_tot %.1f [MtCO2-eq./y]: EROI %.1f offshore %.1f [GW] onshore %.1f [GW] PV %.1f [GW] NUC %.1f [GW]' %(df_GWP.sum(axis=1).loc[p], df_res['EROI'].loc[p], df_assets[p].loc['WIND_OFFSHORE'], df_assets[p].loc['WIND_ONSHORE'], df_assets[p].loc['PV'], df_assets[p]['NUCLEAR']))
        print('GWh: Gas %.1f METHANOL_RE %.1f AMMONIA_RE %.1f H2_RE %.1f Gas-re %.1f PV %.1f Wind %.1f wood %.1f wet biomass %.1f waste %.1f' % ( df_EI[p]['GAS'] ,  df_EI[p]['METHANOL_RE'] ,  df_EI[p]['AMMONIA_RE'] ,  df_EI[p]['H2_RE'] , df_EI[p]['GAS_RE'] ,  df_EI[p]['RES_SOLAR'] ,  df_EI[p]['RES_WIND'] ,  df_EI[p]['WOOD'] ,  df_EI[p]['WET_BIOMASS'] ,   df_EI[p]['WASTE'] ))
        print('Percentage: Gas %.1f METHANOL_RE %.1f AMMONIA_RE %.1f H2_RE %.1f Gas-re %.1f PV %.1f Wind %.1f wood %.1f wet biomass %.1f waste %.1f' % (100 * df_EI[p]['GAS'] / tot_EI, 100 * df_EI[p]['METHANOL_RE'] / tot_EI, 100 * df_EI[p]['AMMONIA_RE'] / tot_EI, 100 * df_EI[p]['H2_RE'] / tot_EI,100 * df_EI[p]['GAS_RE'] / tot_EI, 100 * df_EI[p]['RES_SOLAR'] / tot_EI, 100 * df_EI[p]['RES_WIND'] / tot_EI, 100 * df_EI[p]['WOOD'] / tot_EI, 100 * df_EI[p]['WET_BIOMASS'] / tot_EI,  100 * df_EI[p]['WASTE'] / tot_EI))

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
    # df_energy_stored_50 = pd.read_csv(dir + '/run_50/' + "/output/hourly_data/energy_stored.csv", index_col=0).dropna(axis=1)
    # df_layer_elec_50 = pd.read_csv(dir + '/run_50/' + "/output/hourly_data/layer_ELECTRICITY.csv", index_col=0).dropna(axis=1)
    # df_layer_HEAT_LOW_T_DECEN_50 = pd.read_csv(dir + '/run_50/' + "/output/hourly_data/layer_HEAT_LOW_T_DECEN.csv", index_col=0).dropna(axis=1)
    # df_layer_HEAT_LOW_T_DHN_50 = pd.read_csv(dir + '/run_50/' + "/output/hourly_data/layer_HEAT_LOW_T_DHN.csv", index_col=0).dropna(axis=1)

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
    if config_name_file == 'config_2035_with_nuc':
        dir_plot = 'einv_GWP_tot_nuc_' + str(domestic_RE_share)
    else:
        dir_plot = 'einv_GWP_tot_' + str(domestic_RE_share)

    make_dir(cwd+'/export/')
    make_dir(cwd+'/export/'+dir_plot+'/')
    if config_name_file == 'config_2035_with_nuc':
        dir_plot = cwd + '/export/einv_GWP_tot_nuc_' + str(domestic_RE_share)
    else:
        dir_plot = cwd + '/export/einv_GWP_tot_' + str(domestic_RE_share)
    pdf = 'gwp-tot-' + str(domestic_RE_share)

    ####################################################################################################################
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    x_gwp_tot_index = df_GWP.sum(axis=1).values
    plot_one_serie(df_data=df_cost.sum(axis=1), label='Cost', pdf_name=dir_plot + '/cost_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[40, 100], ylabel='[bEUR/y]')
    plot_one_serie(df_data=df_res['EROI'], label='EROI', pdf_name=dir_plot + '/eroi_custom_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[1, 10], ylabel='[-]', yticks_val=[3,5,7,9])
    plot_one_serie(df_data=df_res['EROI'], label='EROI', pdf_name=dir_plot + '/eroi_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[2.5, 10], ylabel='[-]')
    plot_one_serie(df_data=df_res['FEC'], label='FEC', pdf_name=dir_plot + '/fec_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[300, 480], ylabel='[TWh/y]')
    plot_one_serie(df_data=df_res['Einv'], label='Einv', pdf_name=dir_plot + '/einv_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[30, 180], ylabel='[TWh/y]')
    plot_one_serie(df_data=df_EI.drop(columns=['Subcategory']).transpose().sum(axis=1), label='Primary energy', pdf_name=dir_plot + '/EI_tot_' + str(domestic_RE_share) + '.pdf', x_index=x_gwp_tot_index, ylim=[350, 550], ylabel='[TWh/y]')


    ####################################################################################################################
    # FEC
    df_fec_details.columns = np.round(x_gwp_tot_index, 1)
    fec_plots(df_fec_data=df_fec_details, pdf=pdf, dir_plot=dir_plot)

    ####################################################################################################################
    # PRIMARY ENERGY

    df_EI_cat = rename_columns(df=df_EI_cat.transpose(), old_col=['Biofuel', 'Non-biomass', 'Other non-renewable', 'Fossil fuel'], new_col=['RE-fuels', 'Wind+Solar', 'non-RE', 'Fossil'])
    df_EI_cat.index = np.round(x_gwp_tot_index, 1)
    # Waste+Methanol+Ammonia = other non-RE
    plot_stacked_bar(df_data=df_EI_cat.drop(columns=['Export']), xlabel='Yearly emissions limit [MtCO2-eq./y]',  ylabel='Primary energy [TWh]', ylim=600, pdf_name=dir_plot+'/EI-categories-'+pdf+'.pdf')

    # Renewable RES: biofuel + biomass + non-biomass
    RES_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS','WOOD', 'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    df_EI_RES_RE = retrieve_non_zero_val(df=df_EI.loc[RES_renewable].drop(columns=['Subcategory']).transpose())
    df_EI_RES_RE = rename_columns(df=df_EI_RES_RE, old_col=['WET_BIOMASS', 'WOOD', 'METHANOL_RE', 'GAS_RE', 'AMMONIA_RE', 'H2_RE', 'RES_HYDRO', 'RES_SOLAR', 'RES_WIND', 'RES_GEO'], new_col=['Wet biomass', 'Wood', 'Methanol-RE', 'Gas-RE', 'Ammonia-RE', 'H2-RE', 'Hydro', 'Solar', 'Wind', 'Geo'])
    # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    colors = plt.cm.tab20b(np.linspace(0, 1, 10))
    df_EI_RES_RE.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_EI_RES_RE[['Ammonia-RE', 'Methanol-RE', 'Gas-RE', 'Wet biomass', 'Wood', 'Hydro', 'Solar', 'Wind']], xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]', ylim=530, pdf_name=dir_plot + '/EI-RE-' + pdf + '.pdf', colors=colors)

    # Non renewable RES: Fossil fuel + Other non-renewable
    RES_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE', 'METHANOL', 'URANIUM']
    colors = plt.cm.tab20c(np.linspace(0, 1, 10))
    df_EI_RES_non_RE = retrieve_non_zero_val(df=df_EI.loc[RES_non_renewable].drop(columns=['Subcategory']).transpose())
    df_EI_RES_non_RE = rename_columns(df=df_EI_RES_non_RE, old_col=['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE', 'METHANOL', 'URANIUM'], new_col=['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'NG', 'Elec. import', 'Ammonia', 'H2', 'Waste', 'Methanol', 'URANIUM'])
    df_EI_RES_non_RE.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_EI_RES_non_RE, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Primary energy [TWh]', ylim=350, pdf_name=dir_plot + '/EI-non-RE-' + pdf + '.pdf', colors=colors)


    ####################################################################################################################
    # Einv_tot = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)

    # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    df_Einv_RES_cat.columns = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_Einv_RES_cat.transpose(), xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation energy [TWh]', ylim=160, pdf_name=dir_plot+'/einv-res-'+pdf+'.pdf')

    # Einv_op classed by RESOURCES (RE and non-RE)
    df_einv_op_filtered = retrieve_non_zero_val(df=df_Einv_op.transpose())
    df_einv_op_filtered.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_einv_op_filtered, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation energy [TWh]', ylim=160, pdf_name=dir_plot+'/einv-op-details-'+pdf+'.pdf')

    # Einv_op by RE-RESOURCES
    df_einv_op_RE_filtered = retrieve_non_zero_val(df=df_Einv_op.loc[RES_renewable].transpose())
    df_einv_op_RE_filtered.index = np.round(x_gwp_tot_index, 1)
    df_einv_op_RE_filtered = rename_columns(df=df_einv_op_RE_filtered, old_col=['AMMONIA_RE', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD'], new_col=['Ammonia-RE', 'Methanol-RE', 'Gas-RE', 'Wet biomass', 'Wood'])
    plot_stacked_bar(df_data=df_einv_op_RE_filtered, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation energy [TWh]', ylim=160, pdf_name=dir_plot+'/einv-op-re-res-'+pdf+'.pdf')

    # Einv_op by NON-RE-RESOURCES
    df_einv_op_non_RE_filtered = retrieve_non_zero_val(df=df_Einv_op.loc[RES_non_renewable].transpose())
    df_einv_op_non_RE_filtered.index = np.round(x_gwp_tot_index, 1)
    df_einv_op_non_RE_filtered = rename_columns(df=df_einv_op_non_RE_filtered, old_col=['GAS', 'ELECTRICITY', 'AMMONIA', 'WASTE', 'METHANOL'], new_col=['NG', 'Elec. import', 'Ammonia', 'Waste', 'Methanol'])
    plot_stacked_bar(df_data=df_einv_op_non_RE_filtered, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation energy [TWh]', ylim=30, pdf_name=dir_plot+'/einv-op-non-re-res-'+pdf+'.pdf')

    # 2. Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    df_Einv_TECH_cat.columns =np.round(x_gwp_tot_index, 1)
    df_Einv_TECH_cat = rename_columns(df=df_Einv_TECH_cat.transpose(), old_col=['Electricity', 'Heat', 'Mobility', 'Infrastructure', 'Synthetic fuels', 'Storage'], new_col=['Electricity', 'Heat', 'Mobility', 'Infrastructure', 'RE fuels','Storage'])
    plot_stacked_bar(df_data=df_Einv_TECH_cat.drop(columns=['Infrastructure']), xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Construction energy [TWh]', ylim=35, pdf_name=dir_plot+'/einv-tech-'+pdf+'.pdf')

    # Einv_const classed by categories of technologies: 'Electricity', 'Heat', 'Mobility', 'Infrastructure', 'Synthetic fuels', 'Storage'
    Einv_const_dict['Electricity'].index = np.round(x_gwp_tot_index, 1)
    ymax = Einv_const_dict['Electricity'].sum(axis=1).max() * 1.05
    elec_tech = list(Einv_const_dict['Electricity'].max(axis=0)[Einv_const_dict['Electricity'].max(axis=0) > 0.1].index)
    df_einv_constr_elec_tech = Einv_const_dict['Electricity'][elec_tech].copy()
    df_einv_constr_elec_tech = rename_columns(df=df_einv_constr_elec_tech, old_col=['CCGT', 'PV', 'WIND_ONSHORE', 'WIND_OFFSHORE'], new_col=['CCGT', 'PV', 'Onshore wind', 'Offshore wind'])
    plot_stacked_bar(df_data=df_einv_constr_elec_tech, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Construction energy [TWh]', ylim=ymax, pdf_name=dir_plot+'/einv_const-elec-'+pdf+'.pdf')

    Einv_const_dict['Mobility'].index = np.round(x_gwp_tot_index, 1)
    ymax = Einv_const_dict['Mobility'].sum(axis=1).max() * 1.05
    # select only the mobility technologies with Einv_const > 0.5 GWh/y
    mobility_tech = list(Einv_const_dict['Mobility'].max(axis=0)[Einv_const_dict['Mobility'].max(axis=0) > 0.5].index)
    df_einv_constr_mob_tech = Einv_const_dict['Mobility'][mobility_tech].copy()
    df_einv_constr_mob_tech = rename_columns(df=df_einv_constr_mob_tech, old_col=['CAR_NG', 'CAR_BEV', 'TRUCK_ELEC', 'TRUCK_NG'], new_col=['Gas car', 'Elec. car', 'Elec. truck', 'Gas truck'])
    plot_stacked_bar(df_data=df_einv_constr_mob_tech, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Construction energy [TWh]', ylim=ymax, pdf_name=dir_plot+'/einv_const-mob-'+pdf+'.pdf')


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
    df_gwp_const_concat.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_gwp_const_concat, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Construction emisisons [MtCO2-eq./y]', ylim=9, pdf_name=dir_plot + '/gwp_const-breakdown-' + pdf + '.pdf')

    # GHG emissions breakdown by resources
    df_gwp_op_filtered = retrieve_non_zero_val(df=df_gwp_op.transpose())
    df_gwp_op_filtered = rename_columns(df=df_gwp_op_filtered, old_col=['AMMONIA', 'ELECTRICITY', 'GAS', 'METHANOL', 'WASTE', 'WET_BIOMASS',
       'WOOD'], new_col=['Ammonia', 'Elec. import', 'NG', 'Methanol', 'Waste', 'Wet biomass','Wood'])
    df_gwp_op_filtered.index = np.round(x_gwp_tot_index, 1)
    plot_stacked_bar(df_data=df_gwp_op_filtered, xlabel='Yearly emissions limit [MtCO2-eq./y]', ylabel='Operation emissions [MtCO2-eq./y]', ylim=100, pdf_name=dir_plot + '/gwp_op-breakdown-' + pdf + '.pdf')


    ####################################################################################################################
    # Plot assets installed capacities with stacked bars
    df_assets.columns = np.round(x_gwp_tot_index, 1)
    plot_asset_capacities_by_tech(df_assets=df_assets, pdf=pdf, user_data=config['user_data'], dir_plot=dir_plot, xlabel='Yearly emissions limit [MtCO2-eq./y]')


    ####################################################################################################################
    # Plot assets installed capacities with lines
    # plot_asset_capacities_by_tech_line(df_assets=df_assets, pdf=pdf, user_data=config['user_data'], dir_plot=dir_plot, xlabel='Yearly emissions [MtC02]')

    def plot_asset_capacities_by_tech_line(df_assets: pd.DataFrame, pdf: str, user_data:str, dir_plot:str, xlabel:str='p (%)'):
        """
        Line plot of asset installed capacities by technology subcategories such as electricity, heat high temperature, etc.
        :param df_assets: data of asset installed capacities for all scenarios.
        :param pdf: pdf name.
        :param user_data: user_data path.
        """

        # Retrieve the list of technologies
        df_aux_tech = pd.read_csv(user_data + "/aux_technologies.csv", index_col=0)

        # Retrieve the list subcategory of technologies
        tech_subcategory_list = list(dict.fromkeys(list(df_aux_tech['Subcategory'])))
        tech_by_subcategory = dict()
        for cat in tech_subcategory_list:
            tech_by_subcategory[cat] = list(df_aux_tech[df_aux_tech['Subcategory'] == cat].index)

        # Retrieve for each technology subcategory the corresponding assets
        df_elec_tech = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Electricity']].transpose())
        df_heat_low_DEC = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Heat low temperature decentralised']].transpose())
        df_heat_low_DHN = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Heat low temperature centralised']].transpose())
        df_heat_high_T = retrieve_non_zero_val( df=df_assets.loc[tech_by_subcategory['Heat high temperature']].transpose())
        df_synthetic_fuels = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Synthetic fuels']].transpose())
        df_elec_storage = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Electricity storage']].transpose())
        df_thermal_storage = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Thermal storage']].transpose())
        df_mob_private = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Passenger private']].transpose())
        df_mob_public = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Passenger public']].transpose())
        df_mob_freight = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Freight']].transpose())
        df_other_storage = retrieve_non_zero_val(df=df_assets.loc[tech_by_subcategory['Other storage']].transpose())

        x_index = list(df_elec_tech.index)
        # Installed capacity for electricity production for different scenarios (hydro is removed because too small)
        plt.figure()
        plt.plot(x_index, df_elec_tech['PV'].values, '-D', color='gold', linewidth=3, markersize=5, label='PV')
        plt.plot(x_index, df_elec_tech['WIND_ONSHORE'].values + df_elec_tech['WIND_ONSHORE'].values, '-Dg', linewidth=3, markersize=5, label='Wind')
        plt.plot(x_index, df_elec_tech['CCGT'].values, '-Dk', linewidth=3, markersize=5, label='CCGT')
        plt.plot(x_index, df_heat_high_T['IND_COGEN_GAS'].values + df_heat_low_DHN['DHN_COGEN_GAS'].values, '--P', color='orange', linewidth=3, markersize=5, label='IND. +DHN gas CHP')
        plt.plot(x_index, df_heat_low_DHN['DHN_COGEN_BIO_HYDROLYSIS'].values, '--P', color='brown', linewidth=3, markersize=5, label='Bio. hydro. CHP')
        plt.xlabel(xlabel, fontsize=15)
        plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
        plt.gca().invert_xaxis()
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(fontsize=15)
        plt.tight_layout()
        plt.savefig(dir_plot+ '/f-elec-line-' + pdf + '.pdf')
        plt.show()

        # Installed capacity for decentralised low temperature heat production for different scenarios.
        plt.figure()
        plt.plot(x_index, df_heat_low_DEC['DEC_HP_ELEC'].values, '-D', linewidth=3, markersize=5, label='Heat pumps')
        # plt.plot(x_index, df_heat_low_DEC['DEC_ADVCOGEN_GAS'].values, '-D', linewidth=3, markersize=5, label='DEC_ADVCOGEN_GAS')
        plt.plot(x_index, df_heat_low_DEC['DEC_BOILER_GAS'].values, '-D', linewidth=3, markersize=5, label='Gas boilers')
        plt.xlabel(xlabel, fontsize=15)
        plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
        plt.gca().invert_xaxis()
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(fontsize=15)
        plt.tight_layout()
        plt.savefig(dir_plot+ '/f-heat-low-DEC-line-' + pdf + '.pdf')
        plt.show()

        # Installed capacity for centralised low temperature heat production for different scenarios.
        plt.figure()
        plt.plot(x_index, df_heat_low_DHN['DHN_HP_ELEC'].values, '-D', linewidth=3, markersize=5, label='Heat pumps')
        plt.plot(x_index, df_heat_low_DHN['DHN_BOILER_GAS'].values, '-D', linewidth=3, markersize=5, label='Gas boilers')
        plt.plot(x_index, df_heat_low_DHN['DHN_COGEN_GAS'].values, '-D', linewidth=3, markersize=5, label='Gas CHP')
        plt.plot(x_index, df_heat_low_DHN['DHN_COGEN_BIO_HYDROLYSIS'].values, '-D', linewidth=3, markersize=5, label='Bio. hydro. CHP')
        plt.plot(x_index, df_heat_low_DHN['DHN_SOLAR'].values, '-D', linewidth=3, markersize=5, label='Solar')
        plt.xlabel(xlabel, fontsize=15)
        plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
        plt.gca().invert_xaxis()
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(fontsize=15)
        plt.tight_layout()
        plt.savefig(dir_plot+ '/f-heat-low-DHN-line-' + pdf + '.pdf')
        plt.show()

        # Installed capacity for industrial heat production for different scenarios.
        plt.figure()
        plt.plot(x_index, df_heat_high_T['IND_BOILER_WASTE'].values, '-D', linewidth=3, markersize=5, label='Waste boilers')
        plt.plot(x_index, df_heat_high_T['IND_BOILER_GAS'].values, '-D', linewidth=3, markersize=5, label='Gas boilers')
        plt.plot(x_index, df_heat_high_T['IND_COGEN_GAS'].values, '-D', linewidth=3, markersize=5, label='Gas CHP')
        plt.plot(x_index, df_heat_high_T['IND_DIRECT_ELEC'].values, '-D', linewidth=3, markersize=5, label='Direct electricity')
        plt.xlabel(xlabel, fontsize=15)
        plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
        plt.gca().invert_xaxis()
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(fontsize=15)
        plt.tight_layout()
        plt.savefig(dir_plot+ '/f-heat-high-T-line-' + pdf + '.pdf')
        plt.show()

        # Installed capacity for synthetic gas production for different scenarios.
        plt.figure()
        plt.plot(x_index, df_synthetic_fuels['SMR'].values, '-D', linewidth=3, markersize=5, label='Methane reforming')
        plt.plot(x_index, df_synthetic_fuels['METHANE_TO_METHANOL'].values, '-D', linewidth=3, markersize=5, label='Methane to methanol')
        plt.plot(x_index, df_synthetic_fuels['BIOMASS_TO_METHANOL'].values, '-D', linewidth=3, markersize=5, label='Biomass methanolation')
        plt.plot(x_index, df_synthetic_fuels['HABER_BOSCH'].values, '-D', linewidth=3, markersize=5, label='Haber Bosch')
        plt.plot(x_index, df_synthetic_fuels['METHANOL_TO_HVC'].values, '-D', linewidth=3, markersize=5, label='Methanol to HVC')
        plt.xlabel(xlabel, fontsize=15)
        plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
        plt.gca().invert_xaxis()
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(fontsize=15)
        plt.tight_layout()
        plt.savefig(dir_plot+ '/f-synthetic-fuels-line-' + pdf + '.pdf')
        plt.show()

        # Installed storage capacity for different scenarios.
        plt.figure()
        plt.plot(x_index, df_thermal_storage['TS_DEC_HP_ELEC'].values, '-D', linewidth=3, markersize=5, label='TS DEC HP')
        plt.plot(x_index, df_thermal_storage['TS_DEC_ADVCOGEN_GAS'].values, '-D', linewidth=3, markersize=5, label='TS DEC FC CHP gas')
        plt.plot(x_index, df_thermal_storage['TS_DEC_BOILER_GAS'].values, '-D', linewidth=3, markersize=5, label='TS DEC boiler gas')
        plt.plot(x_index, df_thermal_storage['TS_DHN_SEASONAL'].values, '-D', linewidth=3, markersize=5, label='TS DHN')
        plt.plot(x_index, df_other_storage['GAS_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Gas')
        plt.plot(x_index, df_other_storage['AMMONIA_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Ammonia')
        plt.plot(x_index, df_other_storage['METHANOL_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Methanol')
        plt.plot(x_index, df_elec_storage['PHS'].values, '-+', linewidth=3, markersize=5, label='PHS')
        plt.plot(x_index, df_elec_storage['BATT_LI'].values, '-+', linewidth=3, markersize=5, label='LI Batteries')
        plt.plot(x_index, df_elec_storage['BEV_BATT'].values, '-+', linewidth=3, markersize=5, label='BEV batteries')
        plt.xlabel(xlabel, fontsize=15)
        plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
        plt.gca().invert_xaxis()
        plt.xticks(fontsize=15)
        plt.yticks(fontsize=15)
        plt.legend(fontsize=15)
        plt.tight_layout()
        plt.savefig(dir_plot+ '/f-storages-line-' + pdf + '.pdf')
        plt.show()

        # # Installed storage capacity for different scenarios.
        # plt.figure()
        # plt.plot(x_index, df_thermal_storage['TS_DEC_HP_ELEC'].values, '-D', linewidth=3, markersize=5, label='TS DEC HP')
        # plt.plot(x_index, df_thermal_storage['TS_DEC_ADVCOGEN_GAS'].values, '-D', linewidth=3, markersize=5, label='TS DEC FC CHP gas')
        # plt.plot(x_index, df_thermal_storage['TS_DEC_BOILER_GAS'].values, '-D', linewidth=3, markersize=5, label='TS DEC boiler gas')
        # plt.plot(x_index, df_thermal_storage['TS_DHN_SEASONAL'].values, '-D', linewidth=3, markersize=5, label='TS DHN')
        # plt.plot(x_index, df_other_storage['GAS_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Gas')
        # plt.plot(x_index, df_other_storage['AMMONIA_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Ammonia')
        # plt.plot(x_index, df_other_storage['METHANOL_STORAGE'].values, '-P', linewidth=3, markersize=5, label='Methanol')
        # plt.plot(x_index, df_elec_storage['PHS'].values, '-+', linewidth=3, markersize=5, label='PHS')
        # plt.plot(x_index, df_elec_storage['BATT_LI'].values, '-+', linewidth=3, markersize=5, label='LI Batteries')
        # plt.plot(x_index, df_elec_storage['BEV_BATT'].values, '-+', linewidth=3, markersize=5, label='BEV batteries')
        # plt.xlabel(xlabel, fontsize=15)
        # plt.ylabel('Installed capacity [GW]', rotation=90, fontsize=15)
        # plt.gca().invert_xaxis()
        # plt.xticks(fontsize=15)
        # plt.yticks(fontsize=15)
        # plt.legend(fontsize=15)
        # plt.tight_layout()
        # plt.savefig(dir_plot+ '/f-storages-line-' + pdf + '.pdf')
        # plt.show()



    ##############
    #
    df_EI_filtered = retrieve_non_zero_val(df=df_EI.drop(columns=['Subcategory']).transpose())
    df_EI_percentage = df_EI_filtered.divide(df_EI_filtered.sum(axis=1), axis=0) * 100
    df_EI_percentage.index = np.round(x_gwp_tot_index, 1)