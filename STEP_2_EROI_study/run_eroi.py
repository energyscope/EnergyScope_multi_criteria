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


def get_GWP_op_ini(cs:str):
    """
    Get the GWP_op initial.
    :param cs: case study path and name.
    :return GWP_op initial into a pd.DataFrames.
    """
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
    # Min Einv
    # GWP_tot is not constrained
    # -> allows to compute GWP_op^i
    # -------------------------------------------------

    dir_name = 're_be_0'

    # Running EnergyScope
    cs = f"{config['case_studies_dir']}/{dir_name+'/'+config['case_study_name']}"
    run_fn = f"{config['ES_path']}/master.run"
    es.run_energyscope(cs, run_fn, config['AMPL_path'], config['temp_dir'])

    # Print the Sankey (html)
    output_dir = f"{config['case_studies_dir']}/{dir_name+'/'+config['case_study_name']}/output/"
    es.drawSankey(path=f"{output_dir}/sankey")

    ################################################
    # Compute the EROI "final":
    # -> compute the FEC=Eout from the SANKEY (TWh)
    # -> get the Einv
    # -> EROI "final" = Eout/Einv with Eout = FEC
    # Note: Eout could be also defined as: Eout = EUD * conversion_factor
    ################################################
    ef = get_FEC_from_sankey(case_study_dir=cs, col=config['case_study_name'])
    ef_tot = ef.sum()
    einv = get_total_einv(cs) / 1000  # TWh
    eroi = ef_tot / einv
    print('EROI "final" %.2f' % (eroi))

    # -----------------------------------------------
    # Min Einv
    # s.t. GWP_tot <= p * GWP_op^i with p a percentage and GWP_op^i the value obtained by Min Einv without contraint on GWP_tot
    # -----------------------------------------------

    GWP_op_ini = get_GWP_op_ini(cs=cs)
    range_val = range(95, 0, -5)
    loop_computation(range_val=range_val, dir_name=dir_name, GWP_op_ini=GWP_op_ini, config=config)