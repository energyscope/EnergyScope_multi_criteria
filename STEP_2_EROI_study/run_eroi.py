# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model.

@author: Paolo Thiran, Matija Pavičević, Antoine Dubois, Jonathan Dumas
"""

import yaml
import os

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt

from sys import platform
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
        cfg['solver'] = "cplex"

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


def get_GWP_op_ini(dir_name: str):
    """
    Get the GWP_op initial.
    :param dir_name: directory name.
    :return GWP_op initial into a pd.DataFrames.
    """
    cs = f"{config['case_studies_dir']}/{dir_name + '/run_100'}"
    gwp = pd.read_csv(f"{cs}/output/gwp_breakdown.csv", index_col=0, sep=',')

    # FIXME # sum only of the GWP operation -> maybe to adapt to take into account the GWP construction
    return gwp.sum()['GWP_op']

def loop_computation(range_val, dir_name: str, GWP_op_ini: float, config: dict):
    """
    Minimize the Einv for several GWP_tot <= p*GWP_op_ini with p a percentage.
    :param range_val: range of GWP constrained values.
    :param dir_name: directory name.
    :param GWP_op_ini: GWP_op value computed by minimizing the energy invested without contraint on the GWP_tot.
    :param config: configuration file.
    """
    for gwp_tot_max, cs_name in zip(np.asarray([i for i in range_val]) * GWP_op_ini / 100,
                                    ['run_' + str(i) for i in range_val]):
        print('Case in progress %s' % (cs_name))
        cs = f"{config['case_studies_dir']}/{dir_name + '/' + cs_name}"
        # Update the GWP limit
        config["system_limits"]['GWP_limit'] = gwp_tot_max
        # Saving data to .dat files into the config['temp_dir'] directory
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(out_path=estd_out_path, data=all_data,
                      system_limits=config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'],
                      step1_output_path=config["step1_output"])

        # Running EnergyScope
        run_fn = f"{config['ES_path']}/master.run"
        es.run_energyscope(cs, run_fn, config['AMPL_path'], config['temp_dir'])

        # Example to print the sankey from this script
        output_dir = f"{config['case_studies_dir']}/{dir_name + '/' + cs_name}/output/"
        es.drawSankey(path=f"{output_dir}/sankey")

def post_treatment(range_val, dir_name: str, GWP_op_ini: float):
    """
    Postreat data to get the EROI, FEC, and Einv.
    :param range_val: range of GWP constrained values.
    :param dir_name: directory name.
    :param GWP_op_ini: GWP_op value computed by minimizing the energy invested without contraint on the GWP_tot.
    :return: EROI, FEC, and Einv in pd.DataFrames.
    """
    eroi_list = []
    einv_list = []
    df_ef_list = []
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
        print('case %s Einv %.1f Energy demand %.1f EROI %.2f GWP op MtC02eq %.2f' % (
        cs_name, einv_temp, ef_temp_tot, eroi_temp, gwp_limit))

    df_ef = pd.concat(df_ef_list, axis=1)
    df_eroi = pd.DataFrame(index=[i for i in range_val], data=eroi_list, columns=['EROI'])
    df_inv = pd.DataFrame(index=[i for i in range_val], data=einv_list, columns=['Einv'])

    return df_ef, df_eroi, df_inv

def compute_einv_details(cs: str, energyscope_dir: str, all_data: dict):
    """
    Compute the Einv by RESSOURCES and TECHNOLOGIES, it details the breakdown by subcategories of RESSOURCES and categories of TECHNOLOGIES.
    :param cs: case study path
    :param energyscope_dir: energy scopre directory
    :param all_data: the data into a dict of pd.DataFrames.
    :return: the data into pd.DataFrames
    """
    # Load Einv data
    df_einv = pd.read_csv(f"{cs}/output/einv_breakdown.csv", index_col=0)
    # Define the RESSOURCES and TECHNOLOGIES lists
    RESSOURCES = list(all_data['Resources'].index)
    TECHNOLOGIES = list(all_data['Technologies'].index)
    df_inv_res = df_einv.loc[RESSOURCES].copy()
    df_inv_tech = df_einv.loc[TECHNOLOGIES].copy()
    # Get the category and subcategory indexes
    df_aux_res = pd.read_csv(energyscope_dir + "/Data/User_data/aux_resources.csv", index_col=0)
    df_aux_tech = pd.read_csv(energyscope_dir + "/Data/User_data/aux_technologies.csv", index_col=0)

    # 1. Compute the Einv by subcategory of ressources
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

    # Create the temp_dir if it does not exist
    make_dir(config['temp_dir'])

    # Loading data
    all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # Saving data to .dat files into the config['temp_dir'] directory
    estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
    es.print_estd(out_path=estd_out_path, data=all_data, system_limits=config["system_limits"])
    td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
    # WARNING
    if not os.path.isfile(config["step1_output"]):
        print('WARNING: the STEP1 that consists of generating the 12 typical days must be conducted before to compute the TD_of_days.out file located in %s' %(config["step1_output"]))
    es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

    # Print run file
    run_fn = f"{config['ES_path']}/master.run"
    mod_fns = [f"{config['ES_path']}/ESTD_model.mod"]
    es.print_run(run_fn, mod_fns, [estd_out_path, td12_out_path], config['options'], f"{config['temp_dir']}/output")

    # --------------------------------------------------
    # Minimize the Einv with the GWP that is not constrained
    # -------------------------------------------------

    dir_name = 're_be_0'

    # Running EnergyScope
    cs = f"{config['case_studies_dir']}/{dir_name+'/'+config['case_study_name']}"
    run_fn = f"{config['ES_path']}/master.run"
    es.run_energyscope(cs, run_fn, config['AMPL_path'], config['temp_dir'])

    # Print the Sankey (html)
    output_dir = f"{config['case_studies_dir']}/{dir_name+'/'+config['case_study_name']}/output/"
    es.drawSankey(path=f"{output_dir}/sankey")

    # Compute the FEC: final energy consumption (TWh)
    ef = get_FEC_from_sankey(case_study_dir=cs, col=config['case_study_name'])
    # Compute the EROI
    ef_tot = ef.sum()
    einv = get_total_einv(cs) / 1000  # TWh
    eroi = ef_tot / einv
    print('EROI %.2f' % (eroi))

    # Compute Einv by ressources and technologies
    df_inv_res_by_subcat, df_inv_tech_by_cat = compute_einv_details(cs=cs, energyscope_dir=config['energyscope_dir'], all_data=all_data)

    # TODO: plot of df_inv_res_by_subcat and df_inv_tech_by_cat

    # TODO: breakdown primary energy by ressource: natural gas, solar, wind, RE gas import

    # -----------------------------------------------
    # Minimize the Einv for several GWP maximum values
    # -----------------------------------------------

    GWP_op_ini = get_GWP_op_ini(dir_name=dir_name)
    range_val = range(95, 0, -5)
    loop_computation(range_val=range_val, dir_name=dir_name, GWP_op_ini=GWP_op_ini, config=config)

    # -----------------------------------------------
    # Post treatment: compare two case studies
    # -----------------------------------------------

    # GWP op
    dir_name_0 = 're_be_0'
    dir_name_30 = 're_be_30'
    GWP_op_ini_0 = get_GWP_op_ini(dir_name=dir_name_0)
    GWP_op_ini_30 = get_GWP_op_ini(dir_name=dir_name_30)


    range_val_0 = range(100, 0, -5)
    range_val_30 = range(100, 5, -5)
    df_ef_0, df_eroi_0, df_inv_0, = post_treatment(range_val=range_val_0, dir_name=dir_name_0, GWP_op_ini=GWP_op_ini_0)
    df_ef_30, df_eroi_30, df_inv_30, = post_treatment(range_val=range_val_30, dir_name=dir_name_30, GWP_op_ini=GWP_op_ini_30)

    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    dir_name = 'comparison'
    make_dir(cwd+'/export/'+dir_name+'/')

    range_val = range_val_0

    # Plot EROI vs GWP
    plt.figure()
    plt.plot([i for i in range_val_0], df_eroi_0.values, '-Dk', linewidth=3, markersize=10, label='EROI BE RE share 0%')
    plt.plot([i for i in range_val_30], df_eroi_30.values, '-Db', linewidth=3, markersize=10, label='EROI BE RE share 30%')
    plt.gca().invert_xaxis()
    plt.xticks([i for i in range_val])
    plt.ylabel('(-)')
    plt.xlabel('GWP op (%)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(cwd+'/export/'+dir_name+'/eroi.pdf')
    plt.show()

    # Plot Total final energy demand vs GWP
    plt.figure()
    plt.plot([i for i in range_val_0], df_ef_0.sum().values, '-Db', linewidth=3, markersize=10, label='Ef BE RE share 0%')
    plt.plot([i for i in range_val_0], df_inv_0.values, '-Dr', linewidth=3, markersize=10, label='Einv BE RE share 0%')
    plt.plot([i for i in range_val_30], df_ef_30.sum().values, '-Dg', linewidth=3, markersize=10, label='Ef BE RE share 30%')
    plt.plot([i for i in range_val_30], df_inv_30.values, '-Dy', linewidth=3, markersize=10, label='Einv BE RE share 30%')
    plt.gca().invert_xaxis()
    plt.xticks([i for i in range_val])
    plt.ylabel('(TWh)')
    plt.xlabel('GWP op (%)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(cwd+'/export/'+dir_name+'/final-energy-demand.pdf')
    plt.show()

    # Bar plot of the final energy demand
    df_ef_0.columns = [str(i) for i in range_val_0]
    plt.figure()
    df_ef_0[['100', '50', '25', '10']].transpose().plot.bar()
    plt.ylabel('(TWh)')
    plt.xlabel('GWP op (%)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(cwd+'/export/'+dir_name+'/final-energy-demand-share-0.pdf')
    plt.show()

    df_ef_30.columns = [str(i) for i in range_val_30]
    plt.figure()
    df_ef_30[['100', '50', '25', '10']].transpose().plot.bar()
    plt.ylabel('(TWh)')
    plt.xlabel('GWP op (%)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(cwd+'/export/'+dir_name+'/final-energy-demand-share-30.pdf')
    plt.show()