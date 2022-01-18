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
    for param in ['case_studies_dir', 'user_data', 'developer_data', 'temp_dir', 'model_path', 'step1_output']:
        cfg[param] = os.path.join(cfg['energyscope_dir'], cfg[param])
    return cfg


if __name__ == '__main__':

    # Load configuration
    config = load_config('config.yaml')

    # config['all_data'] = es.import_data(config['data_folders'])
    all_data = es.import_data(config['user_data'], config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # New optimal solution run
    if 1:  # not os.path.isdir(f"{config['case_studies_dir']}/{config['case_study_name']}"):

        # Saving .dat files
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(estd_out_path, all_data, config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
        data_fns = [estd_out_path, td12_out_path]

        # Running EnergyScope
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/optimal_cost.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'])

        # Example to print the sankey from this script
        # output_dir = f"{config['case_studies_dir']}/{config['case_study_name']}/output/"
        # es.draw_sankey(path=f"{output_dir}sankey")

    exit()

    if 0:
        # Optimal solution in terms of EINV
        data_fns = [f"{config['temp_dir']}/ESTD_data.dat", f"{config['temp_dir']}/ESTD_12TD.dat"]
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/optimal_einv.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}_einv/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'])

        # Example to print the sankey from this script
        # output_dir = f"{config['case_studies_dir']}/{config['case_study_name']}_einv/output/"
        # es.draw_sankey(path=f"{output_dir}sankey")

    # Get total cost
    cost = es.get_total_cost(f"{config['case_studies_dir']}/{config['case_study_name']}")
    # Get total einv
    einv = es.get_total_einv(f"{config['case_studies_dir']}/{config['case_study_name']}")

    # Get approximation of pareto front
    epsilons = [0.0125, 0.025, 0.05, 0.1, 0.15]
    for epsilon in epsilons:

        print("Run for epsilon", epsilon)

        # Printing the .dat files for the optimisation problem
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        estd_out_path = f"{config['temp_dir']}/ESTD_data_epsilon.dat"
        es.print_estd(estd_out_path, all_data, config["system_limits"])
        # Add specific elements
        es.newline(estd_out_path)
        es.print_param("TOTAL_COST_OP", cost, "Optimal cost of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("EPSILON", epsilon, "Epsilon value", estd_out_path)
        data_fns = [estd_out_path, td12_out_path]

        # newline(out_path)
        # technologies_to_minimize = ["WIND_ONSHORE", "WIND_OFFSHORE"]
        # print_set(technologies_to_minimize, "TECHNOLOGIES_TO_MINIMIZE", out_path)

        # Run the model
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/epsilon.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}_epsilon_{epsilon}/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'])

        # Example to print the sankey from this script
        # output_dir = f"{config['case_studies_dir']}/{config['case_study_name']}_epsilon_{epsilon}/output/"
        # es.draw_sankey(path=f"{output_dir}sankey")

    exit()
    # Get epsilon necessary condition
    epsilons_pairs = []  # , (0.1, 0.1), (0.1, 0.2), (0.15, 0.1), (0.15, 0.2), (0.15, 0.3)]
    for epsilon_pair in epsilons_pairs:

        epsilon_cost, epsilon_einv = epsilon_pair
        print("Run for epsilon", epsilon_pair)

        # Printing the .dat files for the optimisation problem
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        estd_out_path = f"{config['temp_dir']}/ESTD_data_wind.dat"
        es.print_estd(estd_out_path, all_data, config["system_limits"])
        # Add specific elements
        es.newline(estd_out_path)
        es.print_param("TOTAL_COST_OP", cost, "Optimal cost of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("EPSILON_COST", epsilon_cost, "Epsilon value for cost", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("TOTAL_EINV_OP", einv, "Optimal einv of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("EPSILON_EINV", epsilon_einv, "Epsilon value for einv", estd_out_path)

        es.newline(estd_out_path)
        technologies_to_minimize = ["WIND_ONSHORE", "WIND_OFFSHORE"]
        es.print_set(technologies_to_minimize, "TECHNOLOGIES_TO_MINIMIZE", estd_out_path)
        data_fns = [estd_out_path, td12_out_path]

        # Run the model
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/wind.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}_wind_{epsilon_cost}_{epsilon_einv}/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'])

        # Example to print the sankey from this script
        # output_dir = f"{cs}output"
        # es.draw_sankey(path=f"{cs}output/sankey")
