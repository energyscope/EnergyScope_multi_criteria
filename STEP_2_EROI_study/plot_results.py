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

from STEP_2_EROI_study.run_eroi import get_GWP_op_ini
from energyscope.misc.utils import make_dir
from energyscope.postprocessing.utils import get_total_einv


def load_config(config_fn: str):
    """
    Load the configuration into a dict.
    :param config_fn: configuration file name.
    :return: a dict with the configuration.
    """

    # Load parameters
    cfg = yaml.load(open(config_fn, 'r'), Loader=yaml.FullLoader)

    if platform == "linux":
        cfg['energyscope_dir'] = '/home/jdumas/PycharmProjects/EnergyScope_multi_criteria/'
        cfg['AMPL_path'] = '/home/jdumas/PycharmProjects/ampl_linux-intel64/ampl'
    else:
        cfg['energyscope_dir'] = '/Users/dumas/PycharmProjects/EnergyScope_multi_criteria/'
        cfg['AMPL_path'] = '/Users/dumas/PycharmProjects/ampl_macos64/ampl'
        cfg['options']['solver'] = "cplex"

    # Extend path
    for param in ['case_studies_dir', 'user_data', 'developer_data', 'temp_dir', 'ES_path', 'step1_output']:
        cfg[param] = os.path.join(cfg['energyscope_dir'], cfg[param])

    return cfg


def get_FEC_from_sankey(case_study_dir: str, col:str):
    """
    Compute the FEC from the Sankey.
    :param case_study_dir: path to the case study directory.
    Return the final energy consumption (FEC) (TWh) by use sector: 'Non-energy demand', 'Loss DHN', 'Heat LT DHN', 'Exp & Loss', 'Mob public', 'Heat LT Dec', 'Elec demand', 'Freight', 'Mob priv', 'Heat HT'
    """
    df_sankey = pd.read_csv(f"{case_study_dir}/output/sankey/input2sankey.csv", index_col=0, sep=',')
    ef_list = ['Non-energy demand', 'Loss DHN', 'Heat LT DHN', 'Exp & Loss', 'Mob public', 'Heat LT Dec', 'Elec demand',
               'Freight', 'Mob priv', 'Heat HT']
    ef_final_val = []
    for final_demand in ef_list:
        ef_final_val.append(df_sankey[df_sankey['target'] == final_demand]['realValue'].sum())

    return pd.DataFrame(index=ef_list, data=ef_final_val, columns=[col])

def post_treatment(range_val, GWP_op_ini: float, all_data: dict, cs:str, user_data:str):
    """
    Compute the EROI "final", Eout=FEC, and Einv from the simulation results and dat.

    Compute the EROI "final":
    -> compute the FEC=Eout from the SANKEY (TWh)
    -> get the Einv
    -> EROI "final" = Eout/Einv with Eout = FEC
    Note: Eout could be also defined as: Eout = EUD * conversion_factor

    :param range_val: range of GWP constrained values.
    :param GWP_op_ini: GWP_op value obtained by minimizing Einv without constraint on the GWP_tot.
    :param all_data: the data into a dict of pd.DataFrames.
    :param cs: case study path and name.
    :param user_data: user_data directory.
    :return: EROI "final", Eout=FEC, and Einv in pd.DataFrames.
    """
    eroi_sankey_list = []
    eroi_list = []
    einv_list = []
    df_ef_list = []
    einv_res_by_subcat_list = []
    einv_tech_by_cat_list = []
    primary_energy_subcat_list = []
    primary_energy_list = []
    fec_list = []
    fec_tot_list = []
    for gwp_limit, run in zip(np.asarray([i for i in range_val]) * GWP_op_ini / 100, ['run_' + str(i) for i in range_val]):
        cs_temp = cs + '/' + run

        # Compute FEC: final energy consumption (TWh)
        ef_temp = get_FEC_from_sankey(case_study_dir=cs_temp, col=run)
        df_ef_list.append(ef_temp)

        # Compute the EROI
        ef_temp_tot = ef_temp.sum()
        einv_temp = get_total_einv(cs_temp) / 1000  # TWh
        einv_list.append(einv_temp)
        eroi_sankey_temp = ef_temp_tot / einv_temp
        eroi_sankey_list.append(eroi_sankey_temp.values[0])
        # Compute FEC from year_balance.csv
        df_year_balance = pd.read_csv(f"{cs_temp}/output/year_balance.csv", index_col=0).drop(['Unnamed: 30'], axis=1)
        fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=user_data)
        fec_system_temp = sum(fec_tot.values()) / 1000  # TWh
        fec_list.append(fec_system_temp)
        fec_tot_list.append(pd.DataFrame(data=fec_tot.values(), index=fec_tot.keys(), columns=[run]))
        eroi_temp = fec_system_temp / einv_temp
        eroi_list.append(eroi_temp)

        # print('Case %s Einv %.1f Eout %.1f EROI "final" %.2f GWP_op %.2f (MtC02eq)' % (run, einv_temp, ef_temp_tot, eroi_sankey_temp, gwp_limit))

        df_inv_res_by_subcat, df_inv_tech_by_cat = compute_einv_details(cs=cs_temp,
                                                                        user_data=user_data,
                                                                        all_data=all_data)

        # Compute the primary energy
        df_primary_energy_subcat_temp, df_primary_energy_temp = compute_primary_energy(cs=cs_temp, user_data=user_data, run=run, all_data=all_data)

        primary_energy_subcat_list.append(df_primary_energy_subcat_temp)
        primary_energy_list.append(df_primary_energy_temp.drop(columns=['Subcategory']))
        einv_res_by_subcat_list.append(df_inv_res_by_subcat)
        einv_tech_by_cat_list.append(df_inv_tech_by_cat)

    df_primary_energy = pd.concat(primary_energy_list, axis=1)
    df_primary_energy.columns = [i for i in range_val]
    df_primary_energy['Subcategory'] = df_primary_energy_temp['Subcategory'].copy()
    df_ef = pd.concat(df_ef_list, axis=1)
    df_einv_res_by_subcat = pd.concat(einv_res_by_subcat_list, axis=1) / 1000 # TWh
    df_einv_res_by_subcat.columns = [i for i in range_val]
    df_einv_tech_by_cat = pd.concat(einv_tech_by_cat_list, axis=1) / 1000 # TWh
    df_einv_tech_by_cat.columns = [i for i in range_val]
    df_eroi_sankey = pd.DataFrame(index=[i for i in range_val], data=eroi_sankey_list, columns=['EROI'])
    df_eroi = pd.DataFrame(index=[i for i in range_val], data=eroi_list, columns=['EROI'])
    df_inv = pd.DataFrame(index=[i for i in range_val], data=einv_list, columns=['Einv'])
    df_primary_energy_subcat = pd.concat(primary_energy_subcat_list, axis=1)
    df_primary_energy_subcat.columns = [i for i in range_val]
    df_fec = pd.DataFrame(data=fec_list, index=[i for i in range_val])
    df_fec_details = pd.concat(fec_tot_list, axis=1) / 1000 # TWh
    df_fec_details.columns = [i for i in range_val]

    return df_ef, df_eroi_sankey, df_eroi, df_inv, df_einv_res_by_subcat, df_einv_tech_by_cat, df_primary_energy_subcat, df_primary_energy, df_fec, df_fec_details

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
    df_y_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0).drop(['Unnamed: 30'], axis=1)

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
        prod_tech_EUD[eud] = df_year_balance[eud].drop(index=['END_USES_DEMAND'])[df_year_balance[eud] > 0]
        prod_sum = prod_tech_EUD[eud].sum()
        # total consumption of this energy
        conso_sum= -df_year_balance[eud].drop(index=['END_USES_DEMAND'])[df_year_balance[eud] < 0].sum()
        # Note: conso_eud + eud = prod_sum
        # We calculate the FEC of the eud and not of conso_eud + eud! -> a correction factor is required
        for tech in list(prod_tech_EUD[eud].index):
            # correction factor to calculate the FEC corresponding at the consumption of the eud
            corr_factor = prod_tech_EUD[eud][tech] / prod_sum
            prod_corr = prod_tech_EUD[eud][tech] - conso_sum * corr_factor
            if tech not in RESOURCES:
                fec_tech_corr = fec_given_tech(tech=tech, data=data, prod_corr=prod_corr)
                fec_tech = fec_given_tech(tech=tech, data=data, prod_corr=prod_tech_EUD[eud][tech])
            else:
                fec_tech_corr = prod_corr
                fec_tech = prod_tech_EUD[eud][tech]
            # print('%s %s %.1f %.1f %.1f' %(eud, tech, fec_tech, fec_tech_corr, corr_factor))
            fec_EUD.append([tech, fec_tech_corr])
        fec_details[eud] = pd.DataFrame(fec_EUD)
        fec_tot[eud] = pd.DataFrame(fec_EUD)[1].sum()
    fec_details['ELECTRICITY'] = df_year_balance['ELECTRICITY'].loc['END_USES_DEMAND']
    fec_tot['ELECTRICITY'] = df_year_balance['ELECTRICITY'].loc['END_USES_DEMAND']
    return fec_details, fec_tot

if __name__ == '__main__':

    # Get the current working directory
    cwd = os.getcwd()
    # Print the current working directory
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config.yaml')

    # Loading data
    all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # --------------------------------------------------
    # Minimize the Einv with the GWP that is not constrained
    # -------------------------------------------------

    dir_name = 're_be_0'
    run = 'run_10'
    # Read case study name
    cs = f"{config['case_studies_dir']}/{dir_name+'/'+run}"

    # Compute the FEC from the year_balance.csv
    df_year_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0).drop(['Unnamed: 30'], axis=1)
    fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
    fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
    # Compute the FEC from SANKEY
    ef = get_FEC_from_sankey(case_study_dir=cs, col=run)
    fec_sankey = ef.sum()
    einv = get_total_einv(cs) / 1000  # TWh
    print('FEC SANKEY %.2f vs year_balance %.2f [TWh/y]' % (fec_sankey, fec_tot_val))
    print('EROI %.2f %.2f' % (fec_sankey / einv, fec_tot_val / einv))

    # Compute Einv by ressources and technologies
    df_inv_res_by_subcat, df_inv_tech_by_cat = compute_einv_details(cs=cs, user_data=config['user_data'], all_data=all_data)

    # Primary Energy by subcategory
    df_primary_energy_subcat, df_primary_energy = compute_primary_energy(cs=cs, user_data=config['user_data'], run=run, all_data=all_data)

    #FIXME: problem quand on calcule la FEC dans la fonction post_treatment()
    fec_tot_list = []
    eroi_list = []
    for run in ['run_' + str(i) for i in range(100, 5, -5)]:
        cs = f"{config['case_studies_dir']}/{'re_be_0'}"
        df_year_balance = pd.read_csv(f"{cs + '/' + run}/output/year_balance.csv", index_col=0).drop(['Unnamed: 30'], axis=1)
        fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
        einv = get_total_einv(cs + '/' + run)
        eroi_temp = sum(fec_tot.values()) / einv
        fec_tot_list.append(pd.DataFrame(data=fec_tot.values(), index=fec_tot.keys(), columns=[run]))
        eroi_list.append(eroi_temp)
    df_fec_details = pd.concat(fec_tot_list, axis=1) / 1000 # TWh
    df_fec_details.columns = [i for i in range(100, 5, -5)]


    # -----------------------------------------------
    # Compare two case studies with a RE minimal share of 0% and 30%.
    # Min Einv
    # s.t. GWP_tot <= p * GWP_op^i with p a percentage and GWP_op^i the value obtained by Min Einv without contraint on GWP_tot
    # -----------------------------------------------

    # GWP op
    cs_0 = f"{config['case_studies_dir']}/{'re_be_0/run_100'}"
    cs_30 = f"{config['case_studies_dir']}/{'re_be_30/run_100'}"
    GWP_op_ini_0 = get_GWP_op_ini(cs=cs_0)
    GWP_op_ini_30 = get_GWP_op_ini(cs=cs_30)

    range_val = range(100, 5, -5)
    df_Eout_0, df_eroi_sankey_0, df_eroi_0, df_inv_0, df_einv_res_by_subcat_0, df_einv_tech_by_cat_0, df_primary_energy_subcat_0, df_primary_energy_0, df_fec_0, df_fec_details_0 = post_treatment(
        range_val=range_val, GWP_op_ini=GWP_op_ini_0, all_data=all_data,
        cs=f"{config['case_studies_dir']}/{'re_be_0'}", user_data=config['user_data'])
    df_Eout_30, df_eroi_sankey_30, df_eroi_30, df_inv_30, df_einv_res_by_subcat_30, df_einv_tech_by_cat_30, df_primary_energy_subcat_30, df_primary_energy_30, df_fec_30, df_fec_details_30 = post_treatment(
        range_val=range_val, GWP_op_ini=GWP_op_ini_30, all_data=all_data,
        cs=f"{config['case_studies_dir']}/{'re_be_30'}", user_data=config['user_data'])
    #
    # ####################################################################################################################
    # # -----------------------------------------------
    # # PLOT
    # # -----------------------------------------------
    # ####################################################################################################################
    # dir_name = 'comparison'
    # make_dir(cwd+'/export/'+dir_name+'/')
    #
    # ####################################################################################################################
    # # Plot EROI (computed with FEC from SANKEY and year_balance.csv) vs GWP
    # plt.figure()
    # plt.plot([i for i in range_val], df_eroi_0.values, '-Dk', linewidth=3, markersize=10, label='EROIf: RE share 0%')
    # plt.plot([i for i in range_val], eroi_list, '-Dr', linewidth=3, markersize=10, label='EROIf bis: RE share 0%')
    # plt.plot([i for i in range_val], df_eroi_30.values, '-Db', linewidth=3, markersize=10, label='EROIf: RE share 30%')
    # plt.gca().invert_xaxis()
    # plt.xticks([i for i in range_val])
    # plt.ylabel('(-)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 11)
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/eroi.pdf')
    # plt.show()
    #
    # ####################################################################################################################
    # # Plot compare FEC
    # # plt.figure()
    # plt.plot([i for i in range_val], df_fec_0.values, '-Dk', linewidth=3, markersize=10, label='FEC: RE share 0%')
    # plt.plot([i for i in range_val], df_fec_30.values, '-Db', linewidth=3, markersize=10, label='FEC: RE share 30%')
    # plt.gca().invert_xaxis()
    # plt.xticks([i for i in range_val])
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # # plt.ylim(0, 11)
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/fec.pdf')
    # plt.show()
    #
    # plt.figure()
    # df_fec_details_0.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 400)
    # plt.tight_layout()
    # # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-res-0-stacked-bar.pdf')
    # plt.show()
    # plt.figure()
    # df_fec_details.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 400)
    # plt.tight_layout()
    # # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-res-0-stacked-bar.pdf')
    # plt.show()
    # plt.figure()
    # df_fec_details_30.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 400)
    # plt.tight_layout()
    # # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-res-0-stacked-bar.pdf')
    # plt.show()
    #
    #
    #
    # # plt.figure()
    # # plt.plot([i for i in range_val_0], df_eroi_sankey_0.values, '-Dk', linewidth=3, markersize=10, label='EROIf: RE share 0%')
    # # plt.plot([i for i in range_val_30], df_eroi_sankey_30.values, '-Db', linewidth=3, markersize=10, label='EROIf: RE share 30%')
    # # plt.gca().invert_xaxis()
    # # plt.xticks([i for i in range_val])
    # # plt.ylabel('(-)')
    # # plt.xlabel(r"$GWP_{tot} \leq p \cdot GWP_{op}^0$")
    # # plt.ylim(0, 11)
    # # plt.legend()
    # # plt.tight_layout()
    # # plt.savefig(cwd+'/export/'+dir_name+'/eroi-sankey.pdf')
    # # plt.show()
    #
    # ####################################################################################################################
    # # PLOT: primary energy by subcategory
    # # RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    # # RE share: 0%
    # plt.figure()
    # df_primary_energy_subcat_0.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 450)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/primary-energy-breakdown-res-0-stacked-bar.pdf')
    # plt.show()
    #
    # # Renewable RES: biofuel + biomass + non-biomass
    # RES_renewable = ['AMMONIA_RE', 'H2_RE', 'BIOETHANOL', 'BIODIESEL', 'METHANOL_RE', 'GAS_RE', 'WET_BIOMASS', 'WOOD',
    #                  'RES_HYDRO',
    #                  'RES_SOLAR', 'RES_WIND', 'RES_GEO']
    # df_copy = df_primary_energy_0.loc[RES_renewable].drop(columns=['Subcategory']).copy().transpose()
    # df_copy.columns.name = ''
    # plt.figure()
    # df_copy.loc[:, (df_copy != 0).any(axis=0)].plot(kind='bar', stacked=True)  # plot only colmumns where all values are > 0
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # # plt.ylim(0, 550)
    # plt.tight_layout()
    # plt.savefig(cwd + '/export/' + dir_name + '/primary-energy-renewable-stacked-bar-0.pdf')
    # plt.show()
    #
    # # Non renewable RES: Fossil fuel + Other non-renewable
    # RES_non_renewable = ['LFO', 'DIESEL', 'COAL', 'GASOLINE', 'GAS', 'ELECTRICITY', 'AMMONIA', 'H2', 'WASTE',
    #                      'METHANOL', 'URANIUM']
    # df_copy = df_primary_energy_0.loc[RES_non_renewable].drop(columns=['Subcategory']).copy().transpose()
    # df_copy.columns.name = ''
    # plt.figure()
    # df_copy.loc[:, (df_copy != 0).any(axis=0)].plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # # plt.ylim(0, 550)
    # plt.tight_layout()
    # plt.savefig(cwd + '/export/' + dir_name + '/primary-energy-non-renewable-stacked-bar-0.pdf')
    # plt.show()
    #
    # # RE share: 30%
    # plt.figure()
    # df_primary_energy_subcat_30.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 450)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/primary-energy-breakdown-res-30-stacked-bar.pdf')
    # plt.show()
    # ####################################################################################################################
    #
    #
    # ####################################################################################################################
    # # Plot Einv breakdown by subcategories and categories of ressources and technologies, respectively.
    # # Einv = Einv_operation + Einv_construction
    # # RESOURCES -> use Einv only for the operation (0 for construction)
    # # TECHNOLOGIES -> use Einv only for the construction (0 for operation)
    #
    # # 1. RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    # # RE share: 0%
    # plt.figure()
    # df_einv_res_by_subcat_0.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 90)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-res-0-stacked-bar.pdf')
    # plt.show()
    # # RE share: 30%
    # plt.figure()
    # df_einv_res_by_subcat_30.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 90)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-res-30-stacked-bar.pdf')
    # plt.show()
    #
    #
    # # 2. TECHNOLOGIES categories: electricity, mobility, heat, ...
    # # WARNING: the energy invested for technologies is 0 for the operation part
    # # RE share: 0%
    # plt.figure()
    # df_einv_tech_by_cat_0.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 35)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-tech-0-stacked-bar.pdf')
    # plt.show()
    # # RE share: 30%
    # plt.figure()
    # df_einv_tech_by_cat_30.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('p (%)')
    # plt.ylim(0, 35)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-tech-30-stacked-bar.pdf')
    # plt.show()