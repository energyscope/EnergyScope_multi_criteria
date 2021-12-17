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

def post_treatment(range_val, dir_name: str, GWP_op_ini: float, all_data: dict):
    """
    Compute the EROI "final", Eout=FEC, and Einv from the simulation results and dat.

    Compute the EROI "final":
    -> compute the FEC=Eout from the SANKEY (TWh)
    -> get the Einv
    -> EROI "final" = Eout/Einv with Eout = FEC
    Note: Eout could be also defined as: Eout = EUD * conversion_factor

    :param range_val: range of GWP constrained values.
    :param dir_name: directory name.
    :param GWP_op_ini: GWP_op value obtained by minimizing Einv without constraint on the GWP_tot.
    :param all_data: the data into a dict of pd.DataFrames.
    :return: EROI "final", Eout=FEC, and Einv in pd.DataFrames.
    """
    eroi_list = []
    einv_list = []
    df_ef_list = []
    einv_res_by_subcat_list = []
    einv_tech_by_cat_list = []
    for gwp_limit, cs_name in zip(np.asarray([i for i in range_val]) * GWP_op_ini / 100, ['run_' + str(i) for i in range_val]):
        cs = f"{config['case_studies_dir']}/{dir_name + '/' + cs_name}"

        # Compute FEC: final energy consumption (TWh)
        ef_temp = get_FEC_from_sankey(case_study_dir=cs, col=cs_name)
        df_ef_list.append(ef_temp)

        # Compute the EROI
        ef_temp_tot = ef_temp.sum()
        einv_temp = get_total_einv(cs) / 1000  # TWh
        einv_list.append(einv_temp)
        eroi_temp = ef_temp_tot / einv_temp
        eroi_list.append(eroi_temp.values[0])
        print('Case %s Einv %.1f Eout %.1f EROI "final" %.2f GWP_op %.2f (MtC02eq)' % (cs_name, einv_temp, ef_temp_tot, eroi_temp, gwp_limit))

        df_inv_res_by_subcat, df_inv_tech_by_cat = compute_einv_details(cs=cs,
                                                                        energyscope_dir=config['energyscope_dir'],
                                                                        all_data=all_data)
        einv_res_by_subcat_list.append(df_inv_res_by_subcat)
        einv_tech_by_cat_list.append(df_inv_tech_by_cat)


    df_ef = pd.concat(df_ef_list, axis=1)
    df_einv_res_by_subcat = pd.concat(einv_res_by_subcat_list, axis=1) / 1000 # TWh
    df_einv_res_by_subcat.columns = [i for i in range_val]
    df_einv_tech_by_cat = pd.concat(einv_tech_by_cat_list, axis=1) / 1000 # TWh
    df_einv_tech_by_cat.columns = [i for i in range_val]
    df_eroi = pd.DataFrame(index=[i for i in range_val], data=eroi_list, columns=['EROI'])
    df_inv = pd.DataFrame(index=[i for i in range_val], data=einv_list, columns=['Einv'])

    return df_ef, df_eroi, df_inv, df_einv_res_by_subcat, df_einv_tech_by_cat

def compute_einv_details(cs: str, energyscope_dir: str, all_data: dict):
    """
    Compute the Einv by RESOURCES and TECHNOLOGIES, it details the breakdown by subcategories of RESOURCES and categories of TECHNOLOGIES.
    :param cs: case study path
    :param energyscope_dir: energy scopre directory
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
    df_aux_res = pd.read_csv(energyscope_dir + "/Data/User_data/aux_resources.csv", index_col=0)
    df_aux_tech = pd.read_csv(energyscope_dir + "/Data/User_data/aux_technologies.csv", index_col=0)

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

    # Read case study name
    cs = f"{config['case_studies_dir']}/{dir_name+'/'+config['case_study_name']}"

    # Compute the FEC: final energy consumption (TWh)
    ef = get_FEC_from_sankey(case_study_dir=cs, col=config['case_study_name'])
    # Compute the EROI
    ef_tot = ef.sum()
    einv = get_total_einv(cs) / 1000  # TWh
    eroi = ef_tot / einv
    print('EROI %.2f' % (eroi))

    # Compute Einv by ressources and technologies
    df_inv_res_by_subcat, df_inv_tech_by_cat = compute_einv_details(cs=cs, energyscope_dir=config['energyscope_dir'], all_data=all_data)

    # TODO: breakdown primary energy by ressource: natural gas, solar, wind, RE gas import
    # Primary Energy = resource in the YEAR_BALANCE -> filter by resource in the index column
    df_year_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0).drop(['Unnamed: 30'], axis=1)
    RESOURCES = list(all_data['Resources'].index)
    df_primary_energy = df_year_balance.loc[RESOURCES].sum() / 1000 # TWh
    # Remove CO2 ?
    # Est ce que ça correspond forcément à la partie gauche du SANKEY ?

    # TODO: Eout = FEC computation from YEAR_BALANCE.csv
    df_year_balance_without_eud = df_year_balance.drop('END_USES_DEMAND', axis=0).copy()
    df_eud = df_year_balance.loc['END_USES_DEMAND'].copy()
    for layer in df_year_balance_without_eud.columns:
        print('%s %.2f %.2f' %(layer, df_year_balance_without_eud[layer].sum(), df_eud.loc[layer]))
    #
    # # -----------------------------------------------
    # # Compare two case studies with a RE minimal share of 0% and 30%.
    # # Min Einv
    # # s.t. GWP_tot <= p * GWP_op^i with p a percentage and GWP_op^i the value obtained by Min Einv without contraint on GWP_tot
    # # -----------------------------------------------
    #
    # # GWP op
    # dir_name_0 = 're_be_0'
    # dir_name_30 = 're_be_30'
    # GWP_op_ini_0 = get_GWP_op_ini(dir_name=dir_name_0)
    # GWP_op_ini_30 = get_GWP_op_ini(dir_name=dir_name_30)
    #
    #
    # range_val_0 = range(100, 0, -5)
    # range_val_30 = range(100, 5, -5)
    # df_Eout_0, df_eroi_0, df_inv_0, df_einv_res_by_subcat_0, df_einv_tech_by_cat_0 = post_treatment(range_val=range_val_0, dir_name=dir_name_0, GWP_op_ini=GWP_op_ini_0, all_data=all_data)
    # df_Eout_30, df_eroi_30, df_inv_30, df_einv_res_by_subcat_30, df_einv_tech_by_cat_30 = post_treatment(range_val=range_val_30, dir_name=dir_name_30, GWP_op_ini=GWP_op_ini_30, all_data=all_data)
    #
    # ####################################################################################################################
    # # -----------------------------------------------
    # # PLOT
    # # -----------------------------------------------
    # ####################################################################################################################
    # dir_name = 'comparison'
    # make_dir(cwd+'/export/'+dir_name+'/')
    #
    # range_val = range_val_0
    #
    # ####################################################################################################################
    # # Plot EROI vs GWP
    # plt.figure()
    # plt.plot([i for i in range_val_0], df_eroi_0.values, '-Dk', linewidth=3, markersize=10, label='EROIf: RE share 0%')
    # plt.plot([i for i in range_val_30], df_eroi_30.values, '-Db', linewidth=3, markersize=10, label='EROIf: RE share 30%')
    # plt.gca().invert_xaxis()
    # plt.xticks([i for i in range_val])
    # plt.ylabel('(-)')
    # plt.xlabel('GWP op (%)')
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/eroi.pdf')
    # plt.show()
    #
    # ####################################################################################################################
    # # Plot Einv and Eout = Ef = FEC vs GWP
    # plt.figure()
    # plt.plot([i for i in range_val_0], df_Eout_0.sum().values, '-Db', linewidth=3, markersize=10, label='Eout: RE share 0%')
    # plt.plot([i for i in range_val_0], df_inv_0.values, '-Dr', linewidth=3, markersize=10, label='Einv: RE share 0%')
    # plt.plot([i for i in range_val_30], df_Eout_30.sum().values, '-Dg', linewidth=3, markersize=10, label='Eout: RE share 30%')
    # plt.plot([i for i in range_val_30], df_inv_30.values, '-Dy', linewidth=3, markersize=10, label='Einv: RE share 30%')
    # plt.gca().invert_xaxis()
    # plt.xticks([i for i in range_val])
    # plt.ylabel('(TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/eout-einv.pdf')
    # plt.show()
    #
    # ####################################################################################################################
    # # Bar plot of the final energy demand = Ef = Eout
    # df_Eout_0.columns = [str(i) for i in range_val_0]
    # plt.figure()
    # df_Eout_0[['100', '50', '25', '10']].transpose().plot.bar()
    # plt.ylabel('(TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/eout-share-0.pdf')
    # plt.show()
    #
    # df_Eout_30.columns = [str(i) for i in range_val_30]
    # plt.figure()
    # df_Eout_30[['100', '50', '25', '10']].transpose().plot.bar()
    # plt.ylabel('(TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/eout-share-30.pdf')
    # plt.show()
    #
    # ####################################################################################################################
    # # Plot Einv breakdown by subcategories and categories of ressources and technologies, respectively.
    # # Einv = Einv_operation + Einv_construction
    # # RESOURCES -> use Einv only for the operation (0 for construction)
    # # TECHNOLOGIES -> use Einv only for the construction (0 for operation)
    #
    # # 1. RESOURCES subcategories: Other non-renewable, Fossil fuel, Biofuel, Non-biomass (WIND, SOLAR, HYDRO, ...)
    # # 1.1 Lines
    # plt.figure()
    # for subcat in df_einv_res_by_subcat_0.index:
    #     plt.plot(list(df_einv_res_by_subcat_0.columns), df_einv_res_by_subcat_0.loc[subcat].values, 'D', linewidth=3, markersize=5, label=subcat)
    # plt.gca().invert_xaxis()
    # plt.xticks([i for i in range_val])
    # plt.ylabel('Einv operation (TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-res-0.pdf')
    # plt.show()
    #
    # # 1.2 Stacked bar
    # # RE share: 0%
    # plt.figure()
    # df_einv_res_by_subcat_0.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.ylim(0, 160)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-res-0-stacked-bar.pdf')
    # plt.show()
    # # RE share: 30%
    # plt.figure()
    # df_einv_res_by_subcat_30[5] = 0 # because no data for 5 % of GWP ini
    # df_einv_res_by_subcat_30.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.ylim(0, 160)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-res-30-stacked-bar.pdf')
    # plt.show()
    #
    #
    # # 2. TECHNOLOGIES categories: electricity, mobility, heat, ...
    # # WARNING: the energy invested for technologies is 0 for the operation part
    # plt.figure()
    # for subcat in df_einv_tech_by_cat_0.index:
    #     plt.plot(list(df_einv_tech_by_cat_0.columns), df_einv_tech_by_cat_0.loc[subcat].values, 'D', linewidth=3, markersize=5, label=subcat)
    # plt.gca().invert_xaxis()
    # plt.xticks([i for i in range_val])
    # plt.ylabel('Einv construction (TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-tech-0.pdf')
    # plt.show()
    #
    # # 2. with stacked bar
    # # RE share: 0%
    # plt.figure()
    # df_einv_tech_by_cat_0.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.ylim(0, 35)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-tech-0-stacked-bar.pdf')
    # plt.show()
    # # RE share: 30%
    # plt.figure()
    # df_einv_tech_by_cat_30[5] = 0 # because no data for 5 % of GWP ini
    # df_einv_tech_by_cat_30.transpose().plot(kind='bar', stacked=True)
    # plt.ylabel('(TWh)')
    # plt.xlabel('GWP op (%)')
    # plt.ylim(0, 35)
    # plt.tight_layout()
    # plt.savefig(cwd+'/export/'+dir_name+'/einv-breakdown-tech-30-stacked-bar.pdf')
    # plt.show()