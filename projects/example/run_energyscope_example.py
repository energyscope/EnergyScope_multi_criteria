# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScopeTD STEP 2

@author: Paolo Thiran, Matija Pavičević, Antoine Dubois
"""

import yaml
import os

import energyscope as es


def load_config(config_fn: str):

    # Load parameters
    cfg = yaml.load(open(config_fn, 'r'), Loader=yaml.FullLoader)

    # Extend path
    for param in ['case_studies_dir', 'user_data', 'developer_data', 'temp_dir', 'ES_path', 'step1_output']:
        cfg[param] = os.path.join(cfg['energyscope_dir'], cfg[param])
    return cfg


if __name__ == '__main__':

    # Load configuration
    config = load_config('config.default.yaml')

    # Loading data
    all_data = es.import_data(config['user_data'], config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # Saving data to .dat files
    estd_path = f"{config['temp_dir']}/ESTD_data.dat"
    es.print_estd(estd_path, all_data, config["system_limits"])
    td12_path = f"{config['temp_dir']}/ESTD_12TD.dat"
    es.print_12td(td12_path, all_data['Time_series'], config["step1_output"])
    data_fns = [estd_path, td12_path]

    # Running EnergyScope
    cs = f"{config['case_studies_dir']}/{config['case_study_name']}"
    mod_fns = [f"{config['ES_path']}/ESTD_model.mod"]
    es.run_energyscope_new(cs, config['AMPL_path'], config["options"], mod_fns, data_fns, config['temp_dir'])

    # Example to print the sankey from this script
    # output_dir = f"{config['case_studies_dir']}/{config['case_study_name']}/output/"
    # es.drawSankey(path=f"{output_dir}/sankey")
