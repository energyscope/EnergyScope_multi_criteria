# -*- coding: utf-8 -*-
"""
Results of system Einv_tot minimization with several scenarios computed
by constraining GWP_tot/GWP_op with different GHG emissions targets.
The methods to constrain the GHG emissions are compared.

@author: Jonathan Dumas
"""

# import yaml
import os

import pandas as pd
import energyscope as es
# import numpy as np
import matplotlib.pyplot as plt

# from sys import platform

# from energyscope.utils import get_fec_from_sankey
from energyscope.utils import make_dir
# from energyscope.postprocessing import get_total_einv, compute_einv_details, compute_primary_energy
from energyscope.postprocessing import compute_fec
from projects.eroi_study.utils_plot import plot_stacked_bar, plot_two_series
from projects.eroi_study.utils_res import eroi_computation, res_details, gwp_computation, retrieve_non_zero_val,\
    retrieve_einv_const_by_categories, res_assets_capacity
from projects.eroi_study.utils import load_config


def res_by_sub_cat(res_list: list, res_subcat: pd.DataFrame):
    """
    Provide a DataFrame with index being the resources subcategories and the column the resource.
    """
    primary_dict = dict()
    for res in res_list:
        primary_dict[res] = res_subcat.loc[res]
    return pd.DataFrame(index=primary_dict.values(), data=res_list).sort_index()


def plot_asset_capacities_by_tech(assets_df: pd.DataFrame, user_data: str, save_dir: str, fn_suffix: str,
                                  xlabel: str = 'p (%)'):
    """
    Stacked bar plot of asset installed capacities by technology subcategories
    such as electricity, heat high temperature, etc.
    :param assets_df: data of asset installed capacities for all scenarios.
    :param user_data: user_data path.
    :param save_dir: path to directory where the plots are saved
    :param fn_suffix: suffix at the end of the name of the files where the plots are saved.
    :param xlabel: FIXME: complete
    """

    # Retrieve the list of technologies
    df_aux_tech = pd.read_csv(user_data + "/aux_technologies.csv", index_col=0)

    # Retrieve the list subcategory of technologies
    tech_subcategory_list = list(dict.fromkeys(list(df_aux_tech['Subcategory'])))
    tech_by_subcategory = dict()
    for cat in tech_subcategory_list:
        tech_by_subcategory[cat] = list(df_aux_tech[df_aux_tech['Subcategory'] == cat].index)

    # Retrieve for each technology subcategory the corresponding assets
    df_elec_tech = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Electricity']].transpose())
    df_heat_low_dec = retrieve_non_zero_val(
        df=assets_df.loc[tech_by_subcategory['Heat low temperature decentralised']].transpose())
    df_heat_low_dhn = retrieve_non_zero_val(
        df=assets_df.loc[tech_by_subcategory['Heat low temperature centralised']].transpose())
    df_heat_high_t = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Heat high temperature']].transpose())
    df_synthetic_fuels = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Synthetic fuels']].transpose())
    df_elec_storage = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Electricity storage']].transpose())
    df_thermal_storage = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Thermal storage']].transpose())
    df_mob_private = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Passenger private']].transpose())
    df_mob_public = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Passenger public']].transpose())
    df_mob_freight = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Freight']].transpose())
    df_other_storage = retrieve_non_zero_val(df=assets_df.loc[tech_by_subcategory['Other storage']].transpose())

    plot_stacked_bar(df_elec_tech, xlabel=xlabel, ylabel='[GW]', ylim=90,
                     pdf_name=save_dir + '/f-elec-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_heat_low_dec, xlabel=xlabel, ylabel='[GW]', ylim=35,
                     pdf_name=save_dir + '/f-heat-low-DEC-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_heat_low_dhn, xlabel=xlabel, ylabel='[GW]', ylim=28,
                     pdf_name=save_dir + '/f-heat-low-DHN-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_heat_high_t, xlabel=xlabel, ylabel='[GW]', ylim=25,
                     pdf_name=save_dir + '/f-heat-high-T-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_synthetic_fuels, xlabel=xlabel, ylabel='[GW]', ylim=20,
                     pdf_name=save_dir + '/f-synthetic-fuels-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_elec_storage, xlabel=xlabel, ylabel='[GWh]', ylim=150,
                     pdf_name=save_dir + '/f-elec-storage-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_thermal_storage, xlabel=xlabel, ylabel='[GWh]', ylim=1300,
                     pdf_name=save_dir + '/f-thermal-storage-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_other_storage, xlabel=xlabel, ylabel='[GWh]', ylim=45000,
                     pdf_name=save_dir + '/f-other-storage-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_mob_private, xlabel=xlabel, ylabel='[GW]', ylim=220,
                     pdf_name=save_dir + '/f-mob-private-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_mob_public, xlabel=xlabel, ylabel='[GW]', ylim=40,
                     pdf_name=save_dir + '/f-mob-public-' + fn_suffix + '.pdf')
    plot_stacked_bar(df_mob_freight, xlabel=xlabel,  ylabel='[GW]', ylim=95,
                     pdf_name=save_dir + '/f-freight-' + fn_suffix + '.pdf')


def fec_plots(df_fec_data: pd.DataFrame, save_dir: str, fn_suffix: str):
    """
    FEC PLOTS
    """
    xlabel = 'Yearly emissions [MtC02/y]'
    plot_stacked_bar(df_fec_data.transpose(), xlabel=xlabel,  ylabel='[TWh]', ylim=520,
                     pdf_name=save_dir + '/fec-details-' + fn_suffix + '.pdf')

    # FEC detailed by EUD
    heat_list = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN']
    plot_stacked_bar(df_fec_data.loc[heat_list].transpose(), xlabel=xlabel,  ylabel='[TWh]', ylim=205,
                     pdf_name=save_dir + '/fec-details-heat-' + fn_suffix + '.pdf')

    mob_list = ['MOB_PUBLIC', 'MOB_PRIVATE', 'MOB_FREIGHT_RAIL', 'MOB_FREIGHT_BOAT', 'MOB_FREIGHT_ROAD']
    plot_stacked_bar(df_fec_data.loc[mob_list].transpose(), xlabel=xlabel, ylabel='[TWh]', ylim=100,
                     pdf_name=save_dir + '/fec-details-mob-' + fn_suffix + '.pdf')

    non_energy_list = ['HVC', 'AMMONIA', 'METHANOL', 'ELECTRICITY']
    plot_stacked_bar(df_fec_data.loc[non_energy_list].transpose(), xlabel=xlabel, ylabel='[TWh]', ylim=200,
                     pdf_name=save_dir + '/fec-details-non-E-' + fn_suffix + '.pdf')


def primary_energy_plots(df_ei_1: pd.DataFrame, df_ei_2: pd.DataFrame, pdf_1: str, pdf_2: str, dir_plot: str):
    """
    Primary energy plots by RES categories: RE, Non-RE
    """
    # Renewable RES: biofuel + biomass + non-biomass
    res_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS',
                     'WOOD',
                     'RES_HYDRO',
                     'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    df_1 = retrieve_non_zero_val(df=df_ei_1.loc[res_renewable].drop(columns=['Subcategory']).transpose())
    plot_stacked_bar(df_1, xlabel='p (%)', ylabel='(TWh)', ylim=520,
                     pdf_name=dir_plot + '/EI-RE-' + pdf_1 + '.pdf')
    df_2 = retrieve_non_zero_val(df=df_ei_2.loc[res_renewable].drop(columns=['Subcategory']).transpose())
    # reorder df_2 columns in the same order than df_1 to have the same colors on the plot
    l_new = list(df_1.columns) + [x for x in list(df_2.columns) if x not in list(df_1.columns)]
    plot_stacked_bar(df_2[l_new], xlabel='p (%)', ylabel='(TWh)', ylim=520,
                     pdf_name=dir_plot + '/EI-RE-' + pdf_2 + '.pdf')

    # Non-renewable RES: Fossil fuel + Other non-renewable
    res_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
                         'METHANOL', 'URANIUM']
    df_1 = retrieve_non_zero_val(df=df_ei_1.loc[res_non_renewable].drop(columns=['Subcategory']).transpose())
    plot_stacked_bar(df_1, xlabel='p (%)',  ylabel='(TWh)', ylim=400,
                     pdf_name=dir_plot + '/EI-non-RE-' + pdf_1 + '.pdf')
    df_2 = retrieve_non_zero_val(df=df_ei_2.loc[res_non_renewable].drop(columns=['Subcategory']).transpose())
    plot_stacked_bar(df_2, xlabel='p (%)',  ylabel='(TWh)', ylim=400,
                     pdf_name=dir_plot + '/EI-non-RE-' + pdf_2 + '.pdf')


# parameters
domestic_re_share = 0  # 0, 30 %
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
    # Compare minimization of the system Einv:
    # s.t. GWP_tot <= p * GWP_op^i -> construction and operation GHG emissions are constrained
    # s.t. GWP_op <= p * GWP_op^i  -> construction GHG emissions are constrained
    #  with p a percentage and GWP_op^i the GHG emissions target.
    # -----------------------------------------------

    range_val = range(100, 0, -5)
    dir_1 = f"{config['case_studies_dir']}/{'einv_GWP_op_' + str(domestic_re_share)}"
    dir_2 = f"{config['case_studies_dir']}/{'einv_GWP_tot_' + str(domestic_re_share)}"
    df_res_1, df_fec_details_1 = eroi_computation(dir_name=dir_1, user_data=config['user_data'], range_val=range_val)
    df_res_2, df_fec_details_2 = eroi_computation(dir_name=dir_2, user_data=config['user_data'], range_val=range_val)
    df_einv_op_1, df_einv_res_cat_1, df_einv_tech_cat_1, df_EI_cat_1, df_ei_1_ = \
        res_details(range_val=range_val, all_data=all_data, dir_name=dir_1, user_data=config['user_data'])
    df_einv_op_2, df_einv_res_cat_2, df_einv_tech_cat_2, df_EI_cat_2, df_ei_2_ = \
        res_details(range_val=range_val, all_data=all_data, dir_name=dir_2, user_data=config['user_data'])
    df_gwp_1 = gwp_computation(dir_name=dir_1, range_val=range_val)
    df_gwp_2 = gwp_computation(dir_name=dir_2, range_val=range_val)
    df_einv_const_1 = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data, dir_name=dir_1,
                                                        user_data=config['user_data'])
    df_einv_const_2 = retrieve_einv_const_by_categories(range_val=range_val, all_data=all_data, dir_name=dir_2,
                                                        user_data=config['user_data'])
    assets_df_1 = res_assets_capacity(range_val=range_val, dir_name=dir_1)
    assets_df_2 = res_assets_capacity(range_val=range_val, dir_name=dir_2)

    ####################################################################################################################
    # Compare the case p = 100, 20, 10 and 5
    # When GWP_tot <= p * gwp_limit
    # Use fec_details DataFrame to identify the technologies that satisfy the different EDU and the FEC related
    df_year_balance_100 = pd.read_csv(dir_2 + '/run_100/' + "/output/year_balance.csv", index_col=0)
    fec_details_100, fec_tot_100 = compute_fec(year_balance=df_year_balance_100, user_data_dir=config['user_data'])

    df_year_balance_10 = pd.read_csv(dir_2 + '/run_10/' + "/output/year_balance.csv", index_col=0)
    fec_details_10, fec_tot_10 = compute_fec(year_balance=df_year_balance_10, user_data_dir=config['user_data'])

    df_year_balance_5 = pd.read_csv(dir_2 + '/run_5/' + "/output/year_balance.csv", index_col=0)
    fec_details_5, fec_tot_5 = compute_fec(year_balance=df_year_balance_5, user_data_dir=config['user_data'])

    # Compare technologies that produce electricity between p = 5 and 10 %
    # For instance, when p = 5  -> CCGT mainly produced electricity for the case where GWP_tot is constrained
    print(df_year_balance_10[df_year_balance_10['ELECTRICITY'] > 0]['ELECTRICITY'])
    print(df_year_balance_5[df_year_balance_5['ELECTRICITY'] > 0]['ELECTRICITY'])

    ####################################################################################################################
    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    ####################################################################################################################
    dir_plot_ = 'comparison_GWP_' + str(domestic_re_share)
    make_dir(cwd+'/export/')
    make_dir(cwd+'/export/'+dir_plot_+'/')
    dir_plot_ = cwd+'/export/comparison_GWP_' + str(domestic_re_share)
    pdf_1_ = 'GWP-op-' + str(domestic_re_share)
    pdf_2_ = 'GWP-tot-' + str(domestic_re_share)

    ####################################################################################################################
    # EROI, FEC, Einv_tot, and GWP_tot
    # \alpha^0 = \text{GWP}_{op}^0
    label1 = r'${GWP}_{op} \leq p \cdot gwp^0$'  # x^{op} = \frac{\text{GWP}_{op}}{\alpha^0}
    label2 = r'${GWP}_{tot} \leq p \cdot gwp^0$'  # x^{tot} = \frac{\text{GWP}_{tot}}{\alpha^0}
    plot_two_series(df_data_1=df_res_1['EROI'], df_data_2=df_res_2['EROI'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot_+'/eroi_'+str(domestic_re_share)+'.pdf',
                    x_index=[i for i in range_val], ylim=[2.5, 10], ylabel='EROI [-]', xlabel='p [%]')
    plot_two_series(df_data_1=df_res_1['FEC'], df_data_2=df_res_2['FEC'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot_+'/fec_'+str(domestic_re_share)+'.pdf',
                    x_index=[i for i in range_val], ylim=[300, 480], ylabel='FEC [TWh/y]', xlabel='p [%]')
    plot_two_series(df_data_1=df_res_1['Einv'], df_data_2=df_res_2['Einv'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot_+'/einv_'+str(domestic_re_share)+'.pdf',
                    x_index=[i for i in range_val], ylim=[30, 180], ylabel=r'$Einv{tot}$ [TWh/y]', xlabel='p [%]')
    plot_two_series(df_data_1=df_gwp_1.sum(axis=1), df_data_2=df_gwp_2.sum(axis=1), label_1=label1, label_2=label2,
                    pdf_name=dir_plot_+'/gwp_'+str(domestic_re_share)+'.pdf',
                    x_index=[i for i in range_val], ylim=[0, 105], ylabel=r'$GWP_{tot}$ [MtC02/y]', xlabel='p [%]')
    plot_two_series(df_data_1=df_gwp_1['GWP_cons'], df_data_2=df_gwp_2['GWP_cons'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot_+'/gwp_const_'+str(domestic_re_share)+'.pdf',
                    x_index=[i for i in range_val], ylim=[0, 10], ylabel=r'$GWP_{const}$ [MtC02/y]', xlabel='p [%]')
    plot_two_series(df_data_1=df_gwp_1['GWP_op'], df_data_2=df_gwp_2['GWP_op'], label_1=label1, label_2=label2,
                    pdf_name=dir_plot_+'/gwp_op_'+str(domestic_re_share)+'.pdf',
                    x_index=[i for i in range_val], ylim=[0, 100], ylabel=r'$GWP_{op}$ [MtC02/y]', xlabel='p [%]')

    # To illustrate the shift between constraining GWP_tot & GWP_op
    plt.figure()
    plt.plot(df_gwp_1.sum(axis=1).values, df_res_1['EROI'].values,
             ':Dk', linewidth=3, markersize=10, label=label1, alpha=0.75)
    plt.plot(df_gwp_2.sum(axis=1).values, df_res_2['EROI'].values,
             ':Pb', linewidth=3, markersize=10, label=label2, alpha=1)
    plt.gca().invert_xaxis()
    plt.xticks(fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('EROI [-]', fontsize=15)
    plt.xlabel(xlabel='GWP total [MtC'+r'$0_2$'+'/y]', fontsize=15)
    plt.ylim(2.5, 10)
    plt.legend(fontsize=15)
    plt.tight_layout()
    plt.savefig(dir_plot_+'/eroi_shift_'+str(domestic_re_share)+'.pdf')
    plt.close()

    ####################################################################################################################
    # FEC
    fec_plots(df_fec_data=df_fec_details_1, save_dir=dir_plot_, fn_suffix=pdf_1_)
    fec_plots(df_fec_data=df_fec_details_2, save_dir=dir_plot_, fn_suffix=pdf_2_)

    ####################################################################################################################
    # PRIMARY ENERGY
    # RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_EI_cat_1.transpose(), xlabel='p (%)',  ylabel='(TWh)', ylim=520,
                     pdf_name=dir_plot_+'/EI-details-'+pdf_1_+'.pdf')
    plot_stacked_bar(df_EI_cat_2.transpose(), xlabel='p (%)',  ylabel='(TWh)', ylim=520,
                     pdf_name=dir_plot_+'/EI-details-'+pdf_2_+'.pdf')
    # Provides the list of resources by sub-categories
    # res_1_list = list(retrieve_non_zero_val(df=df_ei_1_.drop(columns=['Subcategory']).transpose()).columns)
    # res_2_list = list(retrieve_non_zero_val(df=df_ei_2_.drop(columns=['Subcategory']).transpose()).columns)
    # df_1_res_by_subcat = res_by_sub_cat(res_list=res_1_list, res_subcat=df_ei_1_['Subcategory'])
    # df_2_res_by_subcat = res_by_sub_cat(res_list=res_2_list, res_subcat=df_ei_2_['Subcategory'])

    # Primary energy plots by RES categories: RE, Non-RE
    primary_energy_plots(df_ei_1=df_ei_1_, df_ei_2=df_ei_2_, pdf_1=pdf_1_, pdf_2=pdf_2_, dir_plot=dir_plot_)

    ####################################################################################################################
    # Einv_tot = Einv_operation + Einv_construction
    # RESOURCES -> use Einv only for the operation (0 for construction)
    # TECHNOLOGIES -> use Einv only for the construction (0 for operation)

    # Einv_op by RESOURCES subcategories: Other non-renewable, Fossil fuel,
    # Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    plot_stacked_bar(df_einv_res_cat_1.transpose(), xlabel='p (%)',  ylabel='(TWh)', ylim=160,
                     pdf_name=dir_plot_+'/einv-res-'+pdf_1_+'.pdf')
    plot_stacked_bar(df_einv_res_cat_2.transpose(), xlabel='p (%)', ylabel='(TWh)', ylim=160,
                     pdf_name=dir_plot_+'/einv-res-'+pdf_2_+'.pdf')

    # Einv_op classed by RESOURCES
    df_1_ = retrieve_non_zero_val(df=df_einv_op_1.transpose())
    plot_stacked_bar(df_1_, xlabel='p (%)', ylabel='(TWh)', ylim=160,
                     pdf_name=dir_plot_+'/einv-res-details-'+pdf_1_+'.pdf')
    df_2_ = retrieve_non_zero_val(df=df_einv_op_2.transpose())
    plot_stacked_bar(df_2_, xlabel='p (%)', ylabel='(TWh)', ylim=160,
                     pdf_name=dir_plot_+'/einv-res-details-'+pdf_2_+'.pdf')

    # 2. Einv_const by TECHNOLOGIES categories: electricity, mobility, heat, ...
    plot_stacked_bar(df_einv_tech_cat_1.transpose(), xlabel='p (%)', ylabel='(TWh)', ylim=35,
                     pdf_name=dir_plot_+'/einv-tech-'+pdf_1_+'.pdf')
    plot_stacked_bar(df_einv_tech_cat_2.transpose(), xlabel='p (%)', ylabel='(TWh)', ylim=35,
                     pdf_name=dir_plot_+'/einv-tech-'+pdf_2_+'.pdf')

    # Einv_const classed by categories of technologies: 'Electricity', 'Heat', 'Mobility',
    # 'Infrastructure', 'Synthetic fuels', 'Storage'
    for cat_ in df_einv_const_1.keys():
        ymax = max(df_einv_const_1[cat_].sum(axis=1).max(), df_einv_const_2[cat_].sum(axis=1).max())
        ymax = ymax * 1.05
        if len(df_einv_const_1[cat_].columns) > 0:
            plot_stacked_bar(df_einv_const_1[cat_], xlabel='p (%)', ylabel='(TWh)', ylim=ymax,
                             pdf_name=dir_plot_+'/einv_const-'+cat_+'-'+pdf_1_+'.pdf')
        if len(df_einv_const_2[cat_].columns) > 0:
            plot_stacked_bar(df_einv_const_2[cat_], xlabel='p (%)', ylabel='(TWh)', ylim=ymax,
                             pdf_name=dir_plot_+'/einv_const-'+cat_+'-'+pdf_2_+'.pdf')

    ####################################################################################################################
    # PLot assets installed capacities
    plot_asset_capacities_by_tech(assets_df=assets_df_1, user_data=config['user_data'],
                                  save_dir=dir_plot_, fn_suffix=pdf_1_)
    plot_asset_capacities_by_tech(assets_df=assets_df_2, user_data=config['user_data'],
                                  save_dir=dir_plot_, fn_suffix=pdf_2_)
