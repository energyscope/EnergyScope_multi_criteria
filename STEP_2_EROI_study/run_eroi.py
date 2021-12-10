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


def energy_final(case_study_dir: str, col:str):
    """
    Run ES using Python.
    :param case_study_dir: path to the case study directory.
    Return the final energy demand (TWh) by use sector: 'Non-energy demand', 'Loss DHN', 'Heat LT DHN', 'Exp & Loss', 'Mob public', 'Heat LT Dec', 'Elec demand', 'Freight', 'Mob priv', 'Heat HT'
    """
    df_sankey = pd.read_csv(f"{case_study_dir}/output/sankey/input2sankey.csv", index_col=0, sep=',')
    ef_list = ['Non-energy demand', 'Loss DHN', 'Heat LT DHN', 'Exp & Loss', 'Mob public', 'Heat LT Dec', 'Elec demand',
               'Freight', 'Mob priv', 'Heat HT']
    ef_final_val = []
    for final_demand in ef_list:
        ef_final_val.append(df_sankey[df_sankey['target'] == final_demand]['realValue'].sum())

    return pd.DataFrame(index=ef_list, data=ef_final_val, columns=[col])

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
    es.print_estd(out_path=estd_out_path, data=all_data, import_capacity=config["import_capacity"], system_limits=config["system_limits"])
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

    # Running EnergyScope
    cs = f"{config['case_studies_dir']}/{config['case_study_name']}"
    run_fn = f"{config['ES_path']}/master.run"
    es.run_energyscope(cs, run_fn, config['AMPL_path'], config['temp_dir'])

    # Example to print the sankey from this script
    output_dir = f"{config['case_studies_dir']}/{config['case_study_name']}/output/"
    es.drawSankey(path=f"{output_dir}/sankey")

    # GWP op
    cs = f"{config['case_studies_dir']}/{'run_100'}"
    gwp = pd.read_csv(f"{cs}/output/gwp_breakdown.csv", index_col=0, sep=',')
    gwp_op_tot = gwp.sum()['GWP_op']

    # -----------------------------------------------
    # Minimize the Einv for several GWP maximum values
    # -----------------------------------------------
    for gwp_limit, cs_name in zip(np.asarray([i for i in range(95, 0, -5)]) * gwp_op_tot/100,['run_'+str(i) for i in range(95, 0, -5)]):
        print('Case in progess %s' %(cs_name))
        cs = f"{config['case_studies_dir']}/{cs_name}"
        # Update the GWP limit
        config["system_limits"]['GWP_limit'] = gwp_limit
        # Saving data to .dat files into the config['temp_dir'] directory
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(out_path=estd_out_path, data=all_data, import_capacity=config["import_capacity"],  system_limits=config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

        # Running EnergyScope
        run_fn = f"{config['ES_path']}/master.run"
        es.run_energyscope(cs, run_fn, config['AMPL_path'], config['temp_dir'])

        # Example to print the sankey from this script
        output_dir = f"{config['case_studies_dir']}/{cs_name}/output/"
        es.drawSankey(path=f"{output_dir}/sankey")

    # -----------------------------------------------
    # Post treatment
    # -----------------------------------------------
    eroi_list = []
    einv_list = []
    df_ef_list = []
    for gwp_limit, cs_name in zip(np.asarray([i for i in range(100, 0, -5)]) * gwp_op_tot/100,['run_'+str(i) for i in range(100, 0, -5)]):
        cs = f"{config['case_studies_dir']}/{cs_name}"

        # Compute the energy final demand
        ef_temp = energy_final(case_study_dir=cs, col=cs_name)
        df_ef_list.append(ef_temp)

        # Compute the EROI
        ef_temp_tot = ef_temp.sum()
        einv_temp = get_total_einv(cs) / 1000  # TWh
        einv_list.append(einv_temp)
        eroi_temp = ef_temp_tot / einv_temp
        eroi_list.append(eroi_temp.values[0])
        print('case %s Einv %.1f Energy demand %.1f EROI %.2f GWP op MtC02eq %.2f' %(cs_name, einv_temp, ef_temp_tot, eroi_temp, gwp_limit))

    df_ef = pd.concat(df_ef_list, axis=1)
    df_eroi = pd.DataFrame(index=[i for i in range(100, 0, -5)], data=eroi_list, columns=['EROI'])
    df_inv = pd.DataFrame(index=[i for i in range(100, 0, -5)], data=einv_list, columns=['Einv'])

    # -----------------------------------------------
    # PLOT
    # -----------------------------------------------
    make_dir(cwd+'/export/')

    # Plot EROI vs GWP
    plt.figure()
    plt.plot([i for i in range(100, 0, -5)], df_eroi.values, '-Dk', linewidth=3, markersize=10, label='EROI=Ef/Einv')
    plt.gca().invert_xaxis()
    plt.xticks([i for i in range(100, 0, -5)])
    plt.ylabel('(-)')
    plt.xlabel('GWP op (%)')
    plt.tight_layout()
    plt.savefig(cwd+'/export/eroi.pdf')
    plt.show()

    # Plot Total final energy demand vs GWP
    plt.figure()
    plt.plot([i for i in range(100, 0, -5)], df_ef.sum().values, '-Db', linewidth=3, markersize=10, label='Ef')
    plt.plot([i for i in range(100, 0, -5)], df_inv.values, '-Dr', linewidth=3, markersize=10, label='Einv')
    plt.gca().invert_xaxis()
    plt.xticks([i for i in range(100, 0, -5)])
    plt.ylabel('(TWh)')
    plt.xlabel('GWP op (%)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(cwd+'/export/final-energy-demand.pdf')
    plt.show()

    # Bar plot of the final energy demand
    df_ef.columns = [str(i) for i in range(100, 0, -5)]
    plt.figure()
    df_ef[['100', '50', '25', '5']].transpose().plot.bar()
    plt.ylabel('(TWh)')
    plt.xlabel('GWP op (%)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(cwd+'/export/final-energy-demand-share.pdf')
    plt.show()