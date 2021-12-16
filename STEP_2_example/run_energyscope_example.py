# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model

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

    # Saving data to .dat files
    out_path = f"{config['temp_dir']}/ESTD_data.dat"
    es.print_estd(out_path, all_data, config["import_capacity"], config["GWP_limit"])
    out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
    es.print_12td(out_path, all_data['Time_series'], config["step1_output"])

    # Running EnergyScope
    cs = f"{config['case_studies_dir']}/{config['case_study_name']}"
    run_fn = f"{config['ES_path']}/ESTD_main.run"
    es.run_energyscope(cs, run_fn, config['AMPL_path'], config['temp_dir'])

    # Example to print the sankey from this script
    output_dir = f"{config['case_studies_dir']}/{config['case_study_name']}/output/"
    es.drawSankey(path=f"{output_dir}/sankey")
