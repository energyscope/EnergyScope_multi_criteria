# -*- coding: utf-8 -*-
"""
This script allows to compute necessary conditions in a 3-objective space

@author: Antoine Dubois
"""
import yaml
import os
import shutil

import energyscope as es


def empty_temp(temp_dir: str):
    shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)


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
    main_path = f"{config['case_studies_dir']}/{config['case_study_name']}"

    # config['all_data'] = es.import_data(config['data_folders'])
    all_data = es.import_data(config['user_data'], config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # --- Necessary conditions --- #
    res_to_minimize = {'locals': ["WOOD", "WET_BIOMASS", "WASTE", "RES_WIND", "RES_SOLAR", "RES_HYDRO", "RES_GEO"],
                       'imports': ["ELECTRICITY", "METHANOL", "AMMONIA", "H2", "COAL", "GAS", "LFO", "DIESEL",
                                   "GASOLINE", "BIODIESEL", "BIOETHANOL", "H2_RE", "GAS_RE", "AMMONIA_RE",
                                   "METHANOL_RE"]}
    run_name = 'locals'
    # Pairs (dev cost, dev einv)
    epsilon_tuples = [(0.1, 0.1), (0.2, 0.2)]
    cost_epsilons_on_pareto = [0.003125, 0.00625, 0.0125, 0.025, 0.05]
    # epsilons_tuples = []
    for cost_epsilon_on_pareto in cost_epsilons_on_pareto:

        if
            solution_path = f"{main_path}/cost_epsilon_{cost_epsilon_on_pareto}"
        # Get cost of solution
        opt_cost = es.get_total_cost(solution_path)
        # Get einv of solution
        opt_einv = es.get_total_einv(solution_path)

        print(f"Run for solution with cost {opt_cost} and einv {opt_einv}")
        empty_temp(config['temp_dir'])

        for epsilon_cost, epsilon_einv in epsilon_tuples:
            # Printing the .dat files for the optimisation problem
            td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
            es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
            estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
            es.print_estd(estd_out_path, all_data, config["system_limits"])
            # Add specific elements
            es.newline(estd_out_path)
            es.print_param("PARETO_SOLUTION_COST", opt_cost, "Cost at the Pareto solution", estd_out_path)
            es.newline(estd_out_path)
            es.print_param("EPSILON_COST", epsilon_cost, "Epsilon value for cost", estd_out_path)
            es.newline(estd_out_path)
            es.print_param("PARETO_SOLUTION_EINV", opt_einv, "Einv at the Pareto solution the system", estd_out_path)
            es.newline(estd_out_path)
            es.print_param("EPSILON_EINV", epsilon_einv, "Epsilon value for einv", estd_out_path)

            es.newline(estd_out_path)
            es.print_set(res_to_minimize[run_name], "RESOURCES_TO_MINIMIZE", estd_out_path)
            data_fns = [estd_out_path, td12_out_path]

            # Run the model
            mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/resources_def2.mod"]
            cs = f"{main_path}/{run_name}_def2_{epsilon_cost}_{epsilon_einv}_{cost_epsilon_on_pareto}/"
            es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                             dump_res_only=True)
