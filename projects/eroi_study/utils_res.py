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

def compute_einv_res(cs: str, all_data: dict):
    """
    Compute the Einv by RESOURCES part (Einv_op).
    :param cs: case study path
    :param user_data: user_data directory
    :param all_data: the data into a dict of pd.DataFrames.
    :return: the data into pd.DataFrames
    """
    # Load Einv data
    df_einv = pd.read_csv(f"{cs}/output/einv_breakdown.csv", index_col=0)
    # Define the RESOURCES list
    RESOURCES = list(all_data['Resources'].index)
    return df_einv.loc[RESOURCES].copy()['Einv_op']

def compute_einv_tech(cs: str, all_data: dict):
    """
    Compute the Einv by TECHNOLOGIES part (Einv_const).
    :param cs: case study path
    :param user_data: user_data directory
    :param all_data: the data into a dict of pd.DataFrames.
    :return: the data into pd.DataFrames
    """
    # Load Einv data
    df_einv = pd.read_csv(f"{cs}/output/einv_breakdown.csv", index_col=0)
    # Define the TECHNOLOGIES list
    TECHNOLOGIES = list(all_data['Technologies'].index)
    return df_einv.loc[TECHNOLOGIES].copy()['Einv_constr']


def retrieve_einv_const_by_categories(range_val, all_data: dict, dir: str, user_data: str):
    """
    Retrieve the Einv_const values for all case studies classed by categories of technologies.
    :param range_val: range of GWP constrained values.
    :param all_data: the data into a dict of pd.DataFrames.
    :param dir: case study path and name.
    :param user_data: user_data directory.
    :return: dict with keys being the categories of technologies. For each catagory, a pd.DataFrame with Einv_const values for all scenarios.
    """
    # Retrieve all Einv_const values for all case studies
    einv_tech = []
    for run in ['run_' + str(i) for i in range_val]:
        cs_temp = dir + '/' + run
        einv_tech.append(compute_einv_tech(cs=cs_temp, all_data=all_data))
    df_einv_tech = pd.concat(einv_tech, axis=1)
    df_einv_tech.columns = [i for i in range_val]

    # Retrieve the technologies categories:
    df_aux_tech = pd.read_csv(user_data + "/aux_technologies.csv", index_col=0)
    # tech_cat = ['Electricity', 'Heat', 'Mobility', 'Infrastructure', 'Synthetic fuels', 'Storage']
    tech_cat = list(df_aux_tech['Category'].values)
    tech_cat = list(dict.fromkeys(tech_cat))  # remove duplicate

    # Class the technologies by categories into a dict
    tech_by_cat = dict()
    for cat in tech_cat:
        tech_by_cat[cat] = list(df_aux_tech['Category'][df_aux_tech['Category'] == cat].index)

    # Retrieve the values of Einv_const per category of technology (and remove tech where Einv_const is always 0)
    tech_classed_by_cat = dict()
    for cat in tech_by_cat.keys():
        tech_classed_by_cat[cat] = retrieve_non_zero_val(df=df_einv_tech.loc[tech_by_cat[cat]].transpose()) /1000 # TWh

    return tech_classed_by_cat


def compute_einv_details(cs: str, user_data: str, all_data: dict):
    """
    Compute the Einv by RESOURCES and TECHNOLOGIES, it details the breakdown by subcategories of RESOURCES and categories of TECHNOLOGIES.
    :param cs: case study path
    :param user_data: user_data directory
    :param all_data: the data into a dict of pd.DataFrames.
    :return: the data into pd.DataFrames
    """
    # Load Einv data
    df_einv = pd.read_csv(f"{cs}/output/einv_breakdown.csv", index_col=0)
    # Define the RESOURCES and TECHNOLOGIES lists
    RESOURCES = list(all_data['Resources'].index)
    TECHNOLOGIES = list(all_data['Technologies'].index)
    df_inv_res = df_einv.loc[RESOURCES].copy()
    df_inv_tech = df_einv.loc[TECHNOLOGIES].copy()
    # Get the category and subcategory indexes
    df_aux_res = pd.read_csv(user_data + "/aux_resources.csv", index_col=0)
    df_aux_tech = pd.read_csv(user_data + "/aux_technologies.csv", index_col=0)

    # 1. Compute the Einv by subcategory of resources
    res_subcat = list(df_aux_res['Subcategory'].values)
    res_subcat = list(dict.fromkeys(res_subcat))  # remove duplicate

    res_by_subcat = dict()
    for sub_cat in res_subcat:
        res_by_subcat[sub_cat] = list(df_aux_res['Subcategory'][df_aux_res['Subcategory'] == sub_cat].index)

    einv_res_by_subcat = dict()
    for sub_cat in res_by_subcat.keys():
        einv_res_by_subcat[sub_cat] = df_inv_res.loc[res_by_subcat[sub_cat]]
    df_inv_res_by_subcat = pd.DataFrame(
        data=[einv_res_by_subcat[sub_cat].sum().sum() for sub_cat in einv_res_by_subcat.keys()],
        index=einv_res_by_subcat.keys(), columns=['RESSOURCES'])

    # 2. Compute the Einv by category of technologies
    tech_cat = list(df_aux_tech['Category'].values)
    tech_cat = list(dict.fromkeys(tech_cat))  # remove duplicate

    tech_by_cat = dict()
    for cat in tech_cat:
        tech_by_cat[cat] = list(df_aux_tech['Category'][df_aux_tech['Category'] == cat].index)

    einv_tech_by_cat = dict()
    for cat in tech_by_cat.keys():
        einv_tech_by_cat[cat] = df_inv_tech.loc[tech_by_cat[cat]]
    df_inv_tech_by_cat = pd.DataFrame(data=[einv_tech_by_cat[cat].sum().sum() for cat in einv_tech_by_cat.keys()],
                                      index=einv_tech_by_cat.keys(), columns=['TECHNOLOGIES'])

    return df_inv_res_by_subcat, df_inv_tech_by_cat


def compute_primary_energy(cs: str, user_data: str, run: str, all_data: dict):
    """
    Compute the primary energy for a given case study.
    :param cs: case study path.
    :param user_data: user_data directory
    :param run: run name.
    :return: the data into pd.DataFrames.
    """
    # load year_balance.csv
    df_y_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0)

    # list the ressources
    RESOURCES = list(all_data['Resources'][all_data['Resources']['Category'] != 'Others'].index)  # remove ressources related to CO2
    RESOURCES.remove('CO2_EMISSIONS')

    # select primary energy from the year_balance.csv into a pd.DataFrame
    # df_temp = df_y_balance.loc[RESOURCES].sum().loc[['ELECTRICITY', 'GASOLINE', 'DIESEL', 'LFO', 'GAS', 'WOOD',
    #                                                  'WET_BIOMASS', 'COAL', 'URANIUM', 'WASTE', 'H2', 'AMMONIA',
    #                                                  'METHANOL',
    #                                                  'RES_WIND', 'RES_SOLAR', 'RES_HYDRO', 'RES_GEO']] / 1000  # TWh

    df_temp = df_y_balance.loc[RESOURCES].sum(axis=1) / 1000  # TWh
    df_primary_energy = pd.DataFrame(data=df_temp.values, index=df_temp.index, columns=['RESSOURCES'])

    # Label each ressource by its subcategory: ['Other non-renewable', 'Fossil fuel', 'Biomass', 'Non-biomass']
    df_primary_energy['Subcategory'] = ''
    df_aux_res = pd.read_csv(user_data + "/aux_resources.csv", index_col=0)
    for ind in df_primary_energy.index:
        df_primary_energy['Subcategory'].loc[ind] = df_aux_res.loc[ind]['Subcategory']

    # List of the subcategories into a list
    res_subcat = list(df_primary_energy['Subcategory'].values)
    res_subcat = list(dict.fromkeys(res_subcat))  # remove duplicate

    # aggregate the primary energy by subcategory
    primary_dict = dict()
    for subcat in res_subcat:
        primary_dict[subcat] = df_primary_energy[df_primary_energy['Subcategory'] == subcat]['RESSOURCES'].sum()

    return pd.DataFrame(data=primary_dict.values(), index=primary_dict.keys(), columns=[run]), df_primary_energy.sort_values(by=['Subcategory'])

def fec_given_tech(tech: str, data: pd.DataFrame, prod_corr:float):
    """
    Compute the FEC related to a given EUD and TECHNO.
    :param tech: technology type to satisfy this EUD type such as IND_COGEN_GAS if EUD = HEAT_HIGH_T
    :param data: dataframe with the year_balance.csv
    return: FEC value
    """

    # get the inputs for a given technology: electricity, gas, H2, etc.
    inputs_tech = data.loc[tech][data.loc[tech] < 0].copy()
    # get the outputs for a given technology: electricity, heat high T, heat low T FHN, etc.
    outputs_tech = data.loc[tech][data.loc[tech] > 0].copy()
    if outputs_tech.sum() == 0:
       return
    else:
        # remove C02 emissions
        outputs_labels = list(outputs_tech.index)
        for lab in ['CO2_ATM', 'CO2_INDUSTRY', 'CO2_CAPTURED']:
            if lab in outputs_labels:
                outputs_tech = outputs_tech.drop([lab], axis=0)
        # Ex: eud = 'HEAT_HIGH_T' and tech = 'IND_COGEN_GAS'
        # IND_COGEN_GAS inputs: gas with 2.1739
        # IND_COGEN_GAS outputs: electricity with 0.9565 and HEAT_HIGH_T with 1
        # -> FEC = (1 * (1+0.9565)) * (2.1739)
        # Warning a technology may have several inputs such as CAR_PHEV with 0.1376 of ELECTRICITY and 0.1087 of GASOLINE for 1 of MOB_PRIVATE
        return (prod_corr / outputs_tech.sum()) * (-inputs_tech.sum())


def compute_fec(data: pd.DataFrame, user_data:str):
    """
    Compute the system FEC for a given simulation in GWh.
    :param data: year_balance.csv
    :return FEC detailed by EUD and technologies into fec_details dict, and FEC aggregated by EUD into fec_tot dict.
    Assumption: FEC ELECTRICITY = EUF ELECTRICITY
    See the FEC computation details for a given EUD in the function fec_given_tech(eud=eud, tech=tech, data=data)
    """
    EUD_types = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN', 'MOB_PUBLIC', 'MOB_PRIVATE', 'MOB_FREIGHT_RAIL',
                 'MOB_FREIGHT_BOAT', 'MOB_FREIGHT_ROAD', 'HVC', 'AMMONIA', 'METHANOL']

    df_aux_res = pd.read_csv(user_data + "/aux_resources.csv", index_col=0)
    RESOURCES = list(df_aux_res.index)
    fec_details = dict()
    fec_tot = dict()
    prod_tech_EUD = dict()
    for eud in EUD_types:
        fec_EUD = []
        # list of tech that produced this eud
        prod_tech_EUD[eud] = data[eud].drop(index=['END_USES_DEMAND'])[data[eud] > 0]
        prod_sum = prod_tech_EUD[eud].sum()
        # total consumption of this energy
        conso_sum= -data[eud].drop(index=['END_USES_DEMAND'])[data[eud] < 0].sum()
        # Note: conso_eud + eud = prod_sum
        # We calculate the FEC of the eud and not of conso_eud + eud! -> a correction factor is required
        for tech in list(prod_tech_EUD[eud].index):
            # correction factor to calculate the FEC corresponding at the consumption of the eud
            corr_factor = prod_tech_EUD[eud][tech] / prod_sum
            prod_corr = prod_tech_EUD[eud][tech] - conso_sum * corr_factor
            if tech not in RESOURCES:
                fec_tech_corr = fec_given_tech(tech=tech, data=data, prod_corr=prod_corr)
                # fec_tech = fec_given_tech(tech=tech, data=data, prod_corr=prod_tech_EUD[eud][tech])
            else:
                fec_tech_corr = prod_corr
                # fec_tech = prod_tech_EUD[eud][tech]
            # print('%s %s %.1f %.1f %.1f' %(eud, tech, fec_tech, fec_tech_corr, corr_factor))
            fec_EUD.append([tech, fec_tech_corr])
        fec_details[eud] = pd.DataFrame(fec_EUD)
        fec_tot[eud] = pd.DataFrame(fec_EUD)[1].sum()
    fec_details['ELECTRICITY'] = data['ELECTRICITY'].loc['END_USES_DEMAND']
    fec_tot['ELECTRICITY'] = data['ELECTRICITY'].loc['END_USES_DEMAND']
    return fec_details, fec_tot


def eroi_computation(dir: str, user_data: str, range_val):
    """
    EROI, Einv, and FEC computation for several case studies.
    :param dir: directory to the case studies.
    :param range: GWP_ini values.
    :return: results into pd.DataFrame.
    """
    fec_tot_list = []
    eroi_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir + '/' + run
        df_year_balance = pd.read_csv(dir_temp + "/output/year_balance.csv", index_col=0)
        fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=user_data)
        fec_temp = sum(fec_tot.values())
        einv_temp = get_total_einv(dir_temp)
        eroi_temp = fec_temp / einv_temp
        fec_tot_list.append(pd.DataFrame(data=fec_tot.values(), index=fec_tot.keys(), columns=[run]))
        eroi_list.append([eroi_temp, fec_temp / 1000, einv_temp / 1000])
    df_fec_details = pd.concat(fec_tot_list, axis=1) / 1000  # TWh
    df_fec_details.columns = [i for i in range_val]
    df_eroi = pd.DataFrame(data=np.asarray(eroi_list), index=[i for i in range_val], columns=['EROI', 'FEC', 'Einv'])
    return df_eroi, df_fec_details


def res_details(range_val, all_data: dict, dir: str, user_data: str):
    """
    Compute the Einv and primary energy details.

    :param range_val: range of GWP constrained values.
    :param all_data: the data into a dict of pd.DataFrames.
    :param dir: case study path and name.
    :param user_data: user_data directory.
    :return: Einv and primary energy results in pd.DataFrames.
    """
    Einv_Res_cat_list = []
    Einv_Tech_cat_list = []
    Einv_res_list = []
    EI_by_cat_list = []
    EI_list = []
    for run in ['run_' + str(i) for i in range_val]:
        cs_temp = dir + '/' + run

        # Compute the Einv details divided into resources and technologies by categories
        df_Einv_RES_cat_temp, df_Einv_TECH_cat_temp = compute_einv_details(cs=cs_temp,
                                                                           user_data=user_data,
                                                                           all_data=all_data)
        Einv_Res_cat_list.append(df_Einv_RES_cat_temp)
        Einv_Tech_cat_list.append(df_Einv_TECH_cat_temp)

        # Einv_op only
        Einv_res_list.append(compute_einv_res(cs=cs_temp, all_data=all_data))

        # Compute the primary energy
        df_EI_cat_temp, df_EI_temp = compute_primary_energy(cs=cs_temp, user_data=user_data, run=run, all_data=all_data)

        EI_by_cat_list.append(df_EI_cat_temp)
        EI_list.append(df_EI_temp.drop(columns=['Subcategory']))

    cols = [i for i in range_val]
    df_Einv_op = pd.concat(Einv_res_list, axis=1) / 1000  # TWh
    df_Einv_op.columns = cols
    df_EI = pd.concat(EI_list, axis=1)
    df_EI.columns = cols
    df_EI['Subcategory'] = df_EI_temp['Subcategory'].copy()
    df_Einv_RES_cat = pd.concat(Einv_Res_cat_list, axis=1) / 1000  # TWh
    df_Einv_RES_cat.columns = cols
    df_Einv_tech_cat = pd.concat(Einv_Tech_cat_list, axis=1) / 1000  # TWh
    df_Einv_tech_cat.columns = cols
    df_EI_cat = pd.concat(EI_by_cat_list, axis=1)
    df_EI_cat.columns = cols

    return df_Einv_op, df_Einv_RES_cat, df_Einv_tech_cat, df_EI_cat, df_EI


def get_gwp(cs: str):
    """
    Get the GWP from gwp_breakdown.csv.
    :param cs: directory name.
    :return GWP value.
    """
    gwp = pd.read_csv(f"{cs}/output/gwp_breakdown.csv", index_col=0, sep=',')

    return gwp.sum()

def get_cost(cs: str):
    """
    Get the cost from cost_breakdown.csv.
    :param cs: directory name.
    :return cost values breakdown between C_inv, C_maint, and C_op.
    """
    cost = pd.read_csv(f"{cs}/output/cost_breakdown.csv", index_col=0, sep=',')

    return cost.sum()

def gwp_computation(dir: str, range_val):
    """
    GWP computation for several case studies.
    :param dir: directory to the case studies.
    :param range: GWP_ini values.
    :return: GWP in MtC02eq/y
    """
    GWP_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir + '/' + run
        GWP_val = get_gwp(cs=dir_temp)
        GWP_list.append([GWP_val['GWP_constr'], GWP_val['GWP_op']])
    return pd.DataFrame(data=np.asarray(GWP_list)/1000, index=[i for i in range_val], columns=['GWP_cons', 'GWP_op'])


def cost_computation(dir: str, range_val):
    """
    Cost computation for several case studies.
    :param dir: directory to the case studies.
    :param range: GWP_ini values.
    :return: Cost in bEUR/y
    """
    cost_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir + '/' + run
        cost_val = get_cost(cs=dir_temp)
        cost_list.append([cost_val['C_inv'], cost_val['C_maint'], cost_val['C_op']])
    return pd.DataFrame(data=np.asarray(cost_list)/1000, index=[i for i in range_val], columns=['C_inv', 'C_maint', 'C_op'])


def gwp_breakdown(dir: str, range_val):
    """
    GWP breakdown for several scenarios.
    :param dir: directory to the case studies.
    :param range: GWP_ini values.
    :return: GWP_const and GWP_op into pd.DataFrame
    """
    gwp_const_list = []
    gwp_op_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir + '/' + run
        gwp = pd.read_csv(f"{dir_temp}/output/gwp_breakdown.csv", index_col=0, sep=',')
        gwp_const_list.append(gwp['GWP_constr'])
        gwp_op_list.append(gwp['GWP_op'])
    df_gwp_const = pd.concat(gwp_const_list, axis=1)
    df_gwp_const.columns = [i for i in range_val]
    df_gwp_op = pd.concat(gwp_op_list, axis=1)
    df_gwp_op.columns = [i for i in range_val]
    return df_gwp_const / 1000, df_gwp_op / 1000 # MtC02/y


def gwp_const_per_category(df_gwp_const: pd.DataFrame, user_data: str):
    """
    Build a dict with technology categories as keys.
    In each category a pd.DataFrame lists the GWP_const of the corresponding technologies for several scenarios.
    :param df_gwp_const: GWP_const raw data for several scenarios.
    :param user_data: path to user_data.
    :return: dict.
    """

    df_aux_tech = pd.read_csv(user_data + "/aux_technologies.csv", index_col=0)

    # Retrieve the list subcategory of technologies
    tech_subcategory_list = list(dict.fromkeys(list(df_aux_tech['Subcategory'])))
    tech_by_subcategory = dict()
    for cat in tech_subcategory_list:
        tech_by_subcategory[cat] = list(df_aux_tech[df_aux_tech['Subcategory'] == cat].index)

    # Select per technology category the GWP_const
    gwp_const_by_tech_cat = dict()
    for cat in tech_by_subcategory.keys():
        temp_list = []
        for tech in tech_by_subcategory[cat]:
            if tech in list(df_gwp_const.columns):
                temp_list.append(df_gwp_const[tech])
        if len(temp_list) > 0:
            gwp_const_by_tech_cat[cat] = pd.concat(temp_list, axis=1)
        else:
            gwp_const_by_tech_cat[cat] = None
    return gwp_const_by_tech_cat

def retrieve_non_zero_val(df: pd.DataFrame):
    """
    Retrieve columns of a DataFrame with 0 values for all rows.
    :param df: DataFrame of shape (n_scenarios, n_cols).
    :return: DataFrame of shape (n_scenarios, n_cols_new) with n_cols_new <= n_cols.
    """
    return df.loc[:, (df != 0).any(axis=0)].copy()


def res_assets_capacity(range_val, dir: str):
    """
    Retrieve the asset installed capacities.
    :param range_val: range of GWP constrained values.
    :param dir: case study path and name.
    :return: Asset installed capacities into a pd.DataFrame.
    """
    assets_list = []
    for run in ['run_' + str(i) for i in range_val]:
        df_asset_temp = pd.read_csv(dir + '/' + run + "/output/assets.csv", index_col=0)
        assets_list.append(df_asset_temp['f'])
    df_assets = pd.concat(assets_list, axis=1)
    df_assets.index.name = ''
    df_assets.columns = [i for i in range_val]
    return df_assets.drop(index='UNITS').astype(float)
if __name__ == '__main__':

    # Load configuration into a dict
    config = load_config(config_fn='config.yaml')

    # Loading data
    all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    GWP_tot = True
    if GWP_tot:
        dir_name = 're_be_GWP_tot'
    else:
        dir_name = 're_be_GWP_op'

    # Read case study name
    run = 'run_100'
    cs_test = f"{config['case_studies_dir']}/{dir_name + '_0/' + run}"

    # Compute the FEC from the year_balance.csv
    df_year_balance = pd.read_csv(f"{cs_test}/output/year_balance.csv", index_col=0)
    fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
    fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
    # Compute the FEC from SANKEY
    ef = get_FEC_from_sankey(case_study_dir=cs_test, col=run)
    fec_sankey = ef.sum()
    einv = get_total_einv(cs_test) / 1000  # TWh
    print('FEC SANKEY %.2f vs year_balance %.2f [TWh/y]' % (fec_sankey, fec_tot_val))
    print('EROI %.2f %.2f' % (fec_sankey / einv, fec_tot_val / einv))
    GWP_val = get_gwp(cs=cs_test)
    print('GWP_cons %.1f GWP_op %.1f [ktC02/y]' %(GWP_val['GWP_constr'], GWP_val['GWP_op']))

    # Compute Einv by ressources and technologies
    df_inv_res_by_subcat, df_inv_tech_by_cat = compute_einv_details(cs=cs_test, user_data=config['user_data'], all_data=all_data)

    # Primary Energy by subcategory
    df_primary_energy_subcat, df_primary_energy = compute_primary_energy(cs=cs_test, user_data=config['user_data'], run=run, all_data=all_data)