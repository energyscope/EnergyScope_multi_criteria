# -*- coding: utf-8 -*-
"""
Results of system Einv_tot minimization with several scenarios computed by constraining GWP_tot/GWP_op with different GHG emissions targets.
The methods to constrain the GHG emissions are compared.

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
from projects.eroi_study.utils_plot import plot_stacked_bar, plot_two_series
from projects.eroi_study.utils_res import compute_fec, compute_einv_details, compute_primary_energy, \
    eroi_computation, res_details, gwp_computation, retrieve_non_zero_val, retrieve_einv_const_by_categories, \
    res_assets_capacity


def res_by_sub_cat(res_list: list, res_subcat: pd.DataFrame):
    """
    Provide a DataFrame with index being the resources subcategories and the column the resource.
    """
    primary_dict = dict()
    for res in res_list:
        primary_dict[res] = res_subcat.loc[res]
    return pd.DataFrame(index=primary_dict.values(), data=res_list).sort_index()


def plot_asset_capacities_by_tech(df_assets: pd.DataFrame, pdf: str, user_data:str, dir_plot:str, xlabel:str='p (%)'):
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

    plot_stacked_bar(df_data=df_elec_tech, xlabel=xlabel, ylabel='[GW]', ylim=90, pdf_name=dir_plot + '/f-elec-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_heat_low_DEC, xlabel=xlabel, ylabel='[GW]', ylim=35, pdf_name=dir_plot + '/f-heat-low-DEC-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_heat_low_DHN, xlabel=xlabel, ylabel='[GW]', ylim=28, pdf_name=dir_plot + '/f-heat-low-DHN-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_heat_high_T, xlabel=xlabel, ylabel='[GW]', ylim=25,pdf_name=dir_plot + '/f-heat-high-T-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_synthetic_fuels, xlabel=xlabel, ylabel='[GW]', ylim=20,  pdf_name=dir_plot + '/f-synthetic-fuels-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_elec_storage, xlabel=xlabel, ylabel='[GWh]', ylim=150, pdf_name=dir_plot + '/f-elec-storage-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_thermal_storage, xlabel=xlabel, ylabel='[GWh]', ylim=1300, pdf_name=dir_plot + '/f-thermal-storage-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_other_storage, xlabel=xlabel, ylabel='[GWh]', ylim=45000,  pdf_name=dir_plot + '/f-other-storage-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_mob_private, xlabel=xlabel, ylabel='[GW]', ylim=220, pdf_name=dir_plot + '/f-mob-private-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_mob_public, xlabel=xlabel, ylabel='[GW]', ylim=40,  pdf_name=dir_plot + '/f-mob-public-' + pdf + '.pdf')
    plot_stacked_bar(df_data=df_mob_freight, xlabel=xlabel,  ylabel='[GW]', ylim=95,   pdf_name=dir_plot + '/f-freight-' + pdf + '.pdf')


def fec_plots(df_fec_data: pd.DataFrame, pdf: str, dir_plot: str):
    """
    FEC PLOTS
    """
    xlabel= 'Yearly emissions [MtC02/y]'
    plot_stacked_bar(df_data=df_fec_data.transpose(), xlabel=xlabel,  ylabel='[TWh]', ylim=520, pdf_name=dir_plot + '/fec-details-' + pdf + '.pdf')

    # FEC detailed by EUD
    heat_list = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']
    plot_stacked_bar(df_data=df_fec_data.loc[heat_list].transpose(), xlabel=xlabel,  ylabel='[TWh]', ylim=205, pdf_name=dir_plot + '/fec-details-heat-' + pdf + '.pdf')

    mob_list = ['MOB_PUBLIC', 'MOB_PRIVATE', 'MOB_FREIGHT_RAIL', 'MOB_FREIGHT_BOAT', 'MOB_FREIGHT_ROAD']
    plot_stacked_bar(df_data=df_fec_data.loc[mob_list].transpose(), xlabel=xlabel, ylabel='[TWh]', ylim=100, pdf_name=dir_plot + '/fec-details-mob-' + pdf + '.pdf')

    non_energy_list = ['HVC', 'AMMONIA', 'METHANOL', 'ELECTRICITY']
    plot_stacked_bar(df_data=df_fec_data.loc[non_energy_list].transpose(), xlabel=xlabel, ylabel='[TWh]', ylim=200,    pdf_name=dir_plot + '/fec-details-non-E-' + pdf + '.pdf')


def primary_energy_plots(df_EI_1: pd.DataFrame, df_EI_2: pd.DataFrame, pdf_1: str, pdf_2: str, dir_plot: str):
    """
    Primary energy plots by RES categories: RE, Non-RE
    """
    # Renewable RES: biofuel + biomass + non-biomass
    RES_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS',
                     'WOOD',
                     'RES_HYDRO',
                     'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    df_1 = retrieve_non_zero_val(df=df_EI_1.loc[RES_renewable].drop(columns=['Subcategory']).transpose())
    plot_stacked_bar(df_data=df_1, xlabel='p (%)', ylabel='(TWh)', ylim=520, pdf_name=dir_plot + '/EI-RE-' + pdf_1 + '.pdf')
    df_2 = retrieve_non_zero_val(df=df_EI_2.loc[RES_renewable].drop(columns=['Subcategory']).transpose())
    # reorder df_2 columns in the same order than df_1 to have the same colors on the plot
    l_new = list(df_1.columns) + [x for x in list(df_2.columns) if x not in list(df_1.columns)]
    plot_stacked_bar(df_data=df_2[l_new], xlabel='p (%)', ylabel='(TWh)', ylim=520, pdf_name=dir_plot + '/EI-RE-' + pdf_2 + '.pdf')

    # Non renewable RES: Fossil fuel + Other non-renewable
    RES_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
                         'METHANOL', 'URANIUM']
    df_1 = retrieve_non_zero_val(df=df_EI_1.loc[RES_non_renewable].drop(columns=['Subcategory']).transpose())
    plot_stacked_bar(df_data=df_1, xlabel='p (%)',  ylabel='(TWh)', ylim=400, pdf_name=dir_plot + '/EI-non-RE-' + pdf_1 + '.pdf')
    df_2 = retrieve_non_zero_val(df=df_EI_2.loc[RES_non_renewable].drop(columns=['Subcategory']).transpose())
    plot_stacked_bar(df_data=df_2, xlabel='p (%)',  ylabel='(TWh)', ylim=400, pdf_name=dir_plot + '/EI-non-RE-' + pdf_2 + '.pdf')

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
    # s.t. GWP_tot <= p * GWP_op^i -> construction and operation GHG emissions are constrained
    # s.t. GWP_op <= p * GWP_op^i  -> construction GHG emissions are constrained
    #  with p a percentage and GWP_op^i the GHG emissions target.
    # -----------------------------------------------

    range_val = range(100, 0, -5)
    dir_1 = f"{config['case_studies_dir']}/{'einv_GWP_op_' + str(domestic_RE_share)}"
    dir_2 = f"{config['case_studies_dir']}/{'einv_GWP_tot_' + str(domestic_RE_share)}"
    df_res_1, df_fec_details_1 = eroi_computation(dir=dir_1, user_data=config['user_data'], range_val=range_val)
    df_res_2, df_fec_details_2 = eroi_computation(dir=dir_2, user_data=config['user_data'], range_val=range_val)
    df_Einv_op_1, df_Einv_RES_cat_1, df_Einv_TECH_cat_1, df_EI_cat_1, df_EI_1 = res_details(range_val=range_val, all_data=all_data, dir=dir_1, user_data=config['user_data'])
    df_Einv_op_2, df_Einv_RES_cat_2, df_Einv_TECH_cat_2, df_EI_cat_2, df_EI_2 = res_details(range_val=range_val, all_data=all_data, dir=dir_2, user_data=config['user_data'])
    df_GWP_1 = gwp_computation(dir=dir_1, range_val=range_val)
    df_GWP_2 = gwp_computation(dir=dir_2, range_val=range_val)
    df_Einv_const_1 = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data, dir=dir_1, user_data=config['user_data'])
    df_Einv_const_2 = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data, dir=dir_2, user_data=config['user_data'])
    df_assets_1 = res_assets_capacity(range_val=range_val, dir=dir_1)
    df_assets_2 = res_assets_capacity(range_val=range_val, dir=dir_2)

    ####################################################################################################################
    # Compare the case p = 100, 20, 10 and 5
    # When GWP_tot <= p * gwp_limit
    # Use fec_details DataFrame to identify the technologies that satisfy the different EDU and the FEC related
    df_year_balance_100 = pd.read_csv(dir_2 +'/run_100/' + "/output/year_balance.csv", index_col=0)
    fec_details_100, fec_tot_100 = compute_fec(data=df_year_balance_100, user_data=config['user_data'])

    df_year_balance_10 = pd.read_csv(dir_2 +'/run_10/' + "/output/year_balance.csv", index_col=0)
    fec_details_10, fec_tot_10 = compute_fec(data=df_year_balance_10, user_data=config['user_data'])

    df_year_balance_5 = pd.read_csv(dir_2 +'/run_5/' + "/output/year_balance.csv", index_col=0)
    fec_details_5, fec_tot_5 = compute_fec(data=df_year_balance_5, user_data=config['user_data'])

    # Compare technologies that produce electricity between p = 5 and 10 %
    # For instance, when p = 5  -> CCGT mainly produced electricity for the case where GWP_tot is constrained
    print(df_year_balance_10[df_year_balance_10['ELECTRICITY'] > 0]['ELECTRICITY'])
    print(df_year_balance_5[df_year_balance_5['ELECTRICITY'] > 0]['ELECTRICITY'])

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
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    label1 = r'${GWP}_{op} \leq p \cdot gwp^0$' # x^{op} = \frac{\text{GWP}_{op}}{\alpha^0}
    label2 = r'${GWP}_{tot} \leq p \cdot gwp^0$' # x^{tot} = \frac{\text{GWP}_{tot}}{\alpha^0}
    plot_two_series(df_data_1=df_res_1['EROI'], df_data_2=df_res_2['EROI'], label_1=label1, label_2=label2, pdf_name=dir_plot+'/eroi_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[2.5, 10], ylabel='EROI [-]', xlabel='p [%]')
    plot_two_series(df_data_1=df_res_1['FEC'], df_data_2=df_res_2['FEC'], label_1=label1, label_2=label2, pdf_name=dir_plot+'/fec_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[300, 480], ylabel='FEC [TWh/y]', xlabel='p [%]')
    plot_two_series(df_data_1=df_res_1['Einv'], df_data_2=df_res_2['Einv'], label_1=label1, label_2=label2, pdf_name=dir_plot+'/einv_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[30, 180], ylabel=r'$Einv{tot}$ [TWh/y]', xlabel='p [%]')
    plot_two_series(df_data_1=df_GWP_1.sum(axis=1), df_data_2=df_GWP_2.sum(axis=1), label_1=label1, label_2=label2, pdf_name=dir_plot+'/gwp_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[0, 105], ylabel=r'$GWP_{tot}$ [MtC02/y]', xlabel='p [%]')
    plot_two_series(df_data_1=df_GWP_1['GWP_cons'], df_data_2=df_GWP_2['GWP_cons'], label_1=label1, label_2=label2, pdf_name=dir_plot+'/gwp_const_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[0, 10], ylabel=r'$GWP_{const}$ [MtC02/y]', xlabel='p [%]')
    plot_two_series(df_data_1=df_GWP_1['GWP_op'], df_data_2=df_GWP_2['GWP_op'], label_1=label1, label_2=label2, pdf_name=dir_plot+'/gwp_op_'+ str(domestic_RE_share)+'.pdf', x_index=[i for i in range_val], ylim=[0, 100], ylabel=r'$GWP_{op}$ [MtC02/y]', xlabel='p [%]')


    # To illustrate the shift between constraining GWP_tot & GWP_op
    plt.figure()
    plt.plot(df_GWP_1.sum(axis=1).values, df_res_1['EROI'].values, ':Dk', linewidth=3, markersize=10, label=label1, alpha=0.75)
    plt.plot(df_GWP_2.sum(axis=1).values, df_res_2['EROI'].values, ':Pb', linewidth=3, markersize=10, label=label2, alpha=1)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('EROI [-]', fontsize=15)
    plt.xlabel(xlabel='GWP total [MtC'+r'$0_2$'+'/y]', fontsize=15)
    plt.ylim(2.5, 10)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(dir_plot+'/eroi_shift_'+ str(domestic_RE_share)+'.pdf')
    plt.close()

    ####################################################################################################################
    # FEC
    fec_plots(df_fec_data=df_fec_details_1, pdf=pdf_1, dir_plot=dir_plot)
    fec_plots(df_fec_data=df_fec_details_2, pdf=pdf_2, dir_plot=dir_plot)

    ####################################################################################################################
    # PRIMARY ENERGY
    # RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_data=df_EI_cat_1.transpose(), xlabel='p (%)',  ylabel='(TWh)', ylim=520, pdf_name=dir_plot+'/EI-details-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_EI_cat_2.transpose(), xlabel='p (%)',  ylabel='(TWh)', ylim=520, pdf_name=dir_plot+'/EI-details-'+pdf_2+'.pdf')
    # Provides the list of resources by subcategories
    # res_1_list = list(retrieve_non_zero_val(df=df_EI_1.drop(columns=['Subcategory']).transpose()).columns)
    # res_2_list = list(retrieve_non_zero_val(df=df_EI_2.drop(columns=['Subcategory']).transpose()).columns)
    # df_1_res_by_subcat = res_by_sub_cat(res_list=res_1_list, res_subcat=df_EI_1['Subcategory'])
    # df_2_res_by_subcat = res_by_sub_cat(res_list=res_2_list, res_subcat=df_EI_2['Subcategory'])

    # Primary energy plots by RES categories: RE, Non-RE
    primary_energy_plots(df_EI_1=df_EI_1, df_EI_2=df_EI_2, pdf_1=pdf_1, pdf_2=pdf_2, dir_plot=dir_plot)

    ####################################################################################################################
    # Einv_tot = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)

    # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_data=df_Einv_RES_cat_1.transpose(), xlabel='p (%)',  ylabel='(TWh)', ylim=160, pdf_name=dir_plot+'/einv-res-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_Einv_RES_cat_2.transpose(), xlabel='p (%)', ylabel='(TWh)', ylim=160, pdf_name=dir_plot+'/einv-res-'+pdf_2+'.pdf')

    # Einv_op classed by RESOURCES
    df_1 = retrieve_non_zero_val(df=df_Einv_op_1.transpose())
    plot_stacked_bar(df_data=df_1, xlabel='p (%)', ylabel='(TWh)', ylim=160, pdf_name=dir_plot+'/einv-res-details-'+pdf_1+'.pdf')
    df_2 = retrieve_non_zero_val(df=df_Einv_op_2.transpose())
    plot_stacked_bar(df_data=df_2, xlabel='p (%)', ylabel='(TWh)', ylim=160, pdf_name=dir_plot+'/einv-res-details-'+pdf_2+'.pdf')

    # 2. Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    plot_stacked_bar(df_data=df_Einv_TECH_cat_1.transpose(), xlabel='p (%)', ylabel='(TWh)', ylim=35, pdf_name=dir_plot+'/einv-tech-'+pdf_1+'.pdf')
    plot_stacked_bar(df_data=df_Einv_TECH_cat_2.transpose(), xlabel='p (%)', ylabel='(TWh)', ylim=35, pdf_name=dir_plot+'/einv-tech-'+pdf_2+'.pdf')

    # Einv_const classed by categories of technologies: 'Electricity', 'Heat', 'Mobility', 'Infrastructure', 'Synthetic fuels', 'Storage'
    for cat in df_Einv_const_1.keys():
        ymax = max(df_Einv_const_1[cat].sum(axis=1).max(), df_Einv_const_2[cat].sum(axis=1).max())
        ymax = ymax * 1.05
        if len(df_Einv_const_1[cat].columns) > 0:
            plot_stacked_bar(df_data=df_Einv_const_1[cat], xlabel='p (%)', ylabel='(TWh)', ylim=ymax, pdf_name=dir_plot+'/einv_const-'+cat+'-'+pdf_1+'.pdf')
        if len(df_Einv_const_2[cat].columns) > 0:
            plot_stacked_bar(df_data=df_Einv_const_2[cat], xlabel='p (%)', ylabel='(TWh)', ylim=ymax, pdf_name=dir_plot+'/einv_const-'+cat+'-'+pdf_2+'.pdf')

    ####################################################################################################################
    # PLot assets installed capacities
    plot_asset_capacities_by_tech(df_assets=df_assets_1, pdf=pdf_1, user_data=config['user_data'], dir_plot=dir_plot)
    plot_asset_capacities_by_tech(df_assets=df_assets_2, pdf=pdf_2, user_data=config['user_data'], dir_plot=dir_plot)