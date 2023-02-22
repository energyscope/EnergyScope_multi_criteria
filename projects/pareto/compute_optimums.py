# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model

@author: Antoine Dubois
"""


import energyscope as es
from utils import load_config, load_data, empty_temp


if __name__ == '__main__':

    # Load configuration and data
    config = load_config('config.yaml')
    all_data = load_data(config)

    # Objective to optimise
    obj = 'cost'

    # Empty temp dir
    empty_temp(config['temp_dir'])

    # Saving .dat files
    estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
    es.print_estd(estd_out_path, all_data, config["system_limits"])
    td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
    es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
    data_fns = [estd_out_path, td12_out_path]

    # Running EnergyScope
    mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/optimal_{obj}.mod"]
    cs = f"{config['case_studies_dir']}/{config['case_study_name']}/{obj}/"
    es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                     dump_res_only=True)
    es.extract_results_step2(cs[:-1])

    # Display sankey
    # es.draw_sankey(f"{cs}output/sankey")
