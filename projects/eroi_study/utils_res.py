# -*- coding: utf-8 -*-
"""
This script makes plots of relevant data.

@author: Jonathan Dumas
"""

# import yaml
# import os

import pandas as pd
import energyscope as es
import numpy as np
# import matplotlib.pyplot as plt

# from sys import platform
# from energyscope.utils import make_dir
from energyscope.utils import load_config, get_fec_from_sankey
from energyscope.postprocessing import get_total_einv, get_cost, get_gwp, compute_fec, \
    compute_einv_details, compute_primary_energy, compute_einv_tech, compute_einv_res


def retrieve_non_zero_val(df: pd.DataFrame):
    """
    Retrieve columns of a DataFrame with 0 values for all rows.
    :param df: DataFrame of shape (n_scenarios, n_cols).
    :return: DataFrame of shape (n_scenarios, n_cols_new) with n_cols_new <= n_cols.
    """
    return df.loc[:, (df != 0).any(axis=0)].copy()


def retrieve_einv_const_by_categories(range_val, all_data: dict, dir_name: str, user_data: str):
    """
    Retrieve the Einv_const values for all case studies classed by categories of technologies.
    :param range_val: range of GWP constrained values.
    :param all_data: the data into a dict of pd.DataFrames.
    :param dir_name: case study path and name.
    :param user_data: user_data directory.
    :return: dict with keys being the categories of technologies. For each catagory, a pd.DataFrame
    with Einv_const values for all scenarios.
    """
    # Retrieve all Einv_const values for all case studies
    einv_tech = []
    for run in ['run_' + str(i) for i in range_val]:
        cs_temp = dir_name + '/' + run
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
        tech_classed_by_cat[cat] = retrieve_non_zero_val(df=df_einv_tech.loc[tech_by_cat[cat]].transpose())/1000.  # TWh

    return tech_classed_by_cat


def eroi_computation(dir_name: str, user_data: str, range_val):
    """
    EROI, Einv, and FEC computation for several case studies.
    :param dir_name: directory to the case studies.
    :param user_data: FIXME: complete
    :param range_val: GWP_ini values.
    :return: results into pd.DataFrame.
    """
    fec_tot_list = []
    eroi_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir_name + '/' + run
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


def res_details(range_val, all_data: dict, dir_name: str, user_data: str):
    """
    Compute the Einv and primary energy details.

    :param range_val: range of GWP constrained values.
    :param all_data: the data into a dict of pd.DataFrames.
    :param dir_name: case study path and name.
    :param user_data: user_data directory.
    :return: Einv and primary energy results in pd.DataFrames.
    """
    einv_res_cat_list = []
    einv_tech_cat_list = []
    einv_res_list = []
    ei_by_cat_list = []
    ei_list = []
    for run in ['run_' + str(i) for i in range_val]:
        cs_temp = dir_name + '/' + run

        # Compute the Einv details divided into resources and technologies by categories
        df_einv_res_cat_temp, df_einv_tech_cat_temp = compute_einv_details(cs=cs_temp,
                                                                           user_data=user_data,
                                                                           all_data=all_data)
        einv_res_cat_list.append(df_einv_res_cat_temp)
        einv_tech_cat_list.append(df_einv_tech_cat_temp)

        # Einv_op only
        einv_res_list.append(compute_einv_res(cs=cs_temp, all_data=all_data))

        # Compute the primary energy
        df_ei_cat_temp, df_ei_temp = compute_primary_energy(cs=cs_temp, user_data=user_data, run=run, all_data=all_data)

        ei_by_cat_list.append(df_ei_cat_temp)
        ei_list.append(df_ei_temp.drop(columns=['Subcategory']))

    cols = [i for i in range_val]
    df_einv_op = pd.concat(einv_res_list, axis=1) / 1000  # TWh
    df_einv_op.columns = cols
    df_ei = pd.concat(ei_list, axis=1)
    df_ei.columns = cols
    df_ei['Subcategory'] = df_ei_temp['Subcategory'].copy()
    df_einv_res_cat = pd.concat(einv_res_cat_list, axis=1) / 1000  # TWh
    df_einv_res_cat.columns = cols
    df_einv_tech_cat = pd.concat(einv_tech_cat_list, axis=1) / 1000  # TWh
    df_einv_tech_cat.columns = cols
    df_ei_cat = pd.concat(ei_by_cat_list, axis=1)
    df_ei_cat.columns = cols

    return df_einv_op, df_einv_res_cat, df_einv_tech_cat, df_ei_cat, df_ei


def gwp_computation(dir_name: str, range_val):
    """
    GWP computation for several case studies.
    :param dir_name: directory to the case studies.
    :param range_val: GWP_ini values.
    :return: GWP in MtC02eq/y
    """
    gwp_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir_name + '/' + run
        gwp_val = get_gwp(cs=dir_temp)
        gwp_list.append([gwp_val['GWP_constr'], gwp_val['GWP_op']])
    return pd.DataFrame(data=np.asarray(gwp_list)/1000, index=[i for i in range_val], columns=['GWP_cons', 'GWP_op'])


def cost_computation(dir_name: str, range_val):
    """
    Cost computation for several case studies.
    :param dir_name: directory to the case studies.
    :param range_val: GWP_ini values.
    :return: Cost in bEUR/y
    """
    cost_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir_name + '/' + run
        cost_val = get_cost(cs=dir_temp)
        cost_list.append([cost_val['C_inv'], cost_val['C_maint'], cost_val['C_op']])
    return pd.DataFrame(data=np.asarray(cost_list)/1000, index=[i for i in range_val],
                        columns=['C_inv', 'C_maint', 'C_op'])


def gwp_breakdown(dir_name: str, range_val):
    """
    GWP breakdown for several scenarios.
    :param dir_name: directory to the case studies.
    :param range_val: scenario values.
    :return: GWP_const and GWP_op into pd.DataFrame
    """
    gwp_const_list = []
    gwp_op_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir_name + '/' + run
        gwp = pd.read_csv(f"{dir_temp}/output/gwp_breakdown.csv", index_col=0, sep=',')
        gwp_const_list.append(gwp['GWP_constr'])
        gwp_op_list.append(gwp['GWP_op'])
    df_gwp_const = pd.concat(gwp_const_list, axis=1)
    df_gwp_const.columns = [i for i in range_val]
    df_gwp_op = pd.concat(gwp_op_list, axis=1)
    df_gwp_op.columns = [i for i in range_val]
    return df_gwp_const / 1000, df_gwp_op / 1000  # MtC02/y


def cost_breakdown(dir_name: str, range_val):
    """
    Cost breakdown for several scenarios.
    :param dir_name: directory to the case studies.
    :param range_val: scenario values.
    :return: GWP_const and GWP_op into pd.DataFrame
    """
    cost_inv_list = []
    cost_maint_list = []
    cost_op_list = []
    for run in ['run_' + str(i) for i in range_val]:
        dir_temp = dir_name + '/' + run
        gwp = pd.read_csv(f"{dir_temp}/output/cost_breakdown.csv", index_col=0, sep=',')
        cost_inv_list.append(gwp['C_inv'])
        cost_maint_list.append(gwp['C_maint'])
        cost_op_list.append(gwp['C_op'])
    df_cost_inv = pd.concat(cost_inv_list, axis=1)
    df_cost_inv.columns = [i for i in range_val]
    df_cost_maint = pd.concat(cost_maint_list, axis=1)
    df_cost_maint.columns = [i for i in range_val]
    df_cost_op = pd.concat(cost_op_list, axis=1)
    df_cost_op.columns = [i for i in range_val]
    return df_cost_inv / 1000, df_cost_maint / 1000, df_cost_op / 1000  # bEUR/y


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


def res_assets_capacity(range_val, dir_name: str):
    """
    Retrieve the asset installed capacities.
    :param range_val: range of GWP constrained values.
    :param dir_name: case study path and name.
    :return: Asset installed capacities into a pd.DataFrame.
    """
    assets_list = []
    for run in ['run_' + str(i) for i in range_val]:
        df_asset_temp = pd.read_csv(dir_name + '/' + run + "/output/assets.csv", index_col=0)
        assets_list.append(df_asset_temp['f'])
    df_assets = pd.concat(assets_list, axis=1)
    df_assets.index.name = ''
    df_assets.columns = [i for i in range_val]
    return df_assets.drop(index='UNITS').astype(float)


if __name__ == '__main__':

    # Load configuration into a dict
    config_ = load_config(config_fn='config.yaml')

    # Loading data
    all_data_ = es.import_data(user_data_dir=config_['user_data'], developer_data_dir=config_['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech_ in config_['Technologies']['f_min']:
        all_data_['Technologies']['f_min'].loc[tech_] = config_['Technologies']['f_min'][tech_]

    gwp_tot_ = True
    if gwp_tot_:
        dir_name_ = 're_be_GWP_tot'
    else:
        dir_name_ = 're_be_GWP_op'

    # Read case study name
    run_ = 'run_100'
    cs_test_ = f"{config_['case_studies_dir']}/{dir_name_ + '_0/' + run_}"

    # Compute the FEC from the year_balance.csv
    df_year_balance_ = pd.read_csv(f"{cs_test_}/output/year_balance.csv", index_col=0)
    fec_details_, fec_tot_ = compute_fec(year_balance=df_year_balance_, user_data_dir=config_['user_data'])
    fec_tot_val_ = sum(fec_tot_.values()) / 1000  # TWh
    # Compute the FEC from SANKEY
    ef_ = get_fec_from_sankey(case_study_dir=cs_test_, col=run_)
    fec_sankey_ = ef_.sum()
    einv_ = get_total_einv(cs_test_) / 1000  # TWh
    print('FEC SANKEY %.2f vs year_balance %.2f [TWh/y]' % (fec_sankey_, fec_tot_val_))
    print('EROI %.2f %.2f' % (fec_sankey_ / einv_, fec_tot_val_ / einv_))
    gwp_val_ = get_gwp(cs=cs_test_)
    print('GWP_cons %.1f GWP_op %.1f [ktC02/y]' % (gwp_val_['GWP_constr'], gwp_val_['GWP_op']))

    # Compute Einv by resources and technologies
    df_inv_res_by_subcat_, df_inv_tech_by_cat_ = \
        compute_einv_details(cs=cs_test_, user_data=config_['user_data'], all_data=all_data_)

    # Primary Energy by subcategory
    df_primary_energy_subcat_, df_primary_energy_ = \
        compute_primary_energy(cs=cs_test_, user_data=config_['user_data'], run=run_, all_data=all_data_)
