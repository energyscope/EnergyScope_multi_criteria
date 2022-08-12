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

    # config['all_data'] = es.import_data(config['data_folders'])
    all_data = es.import_data(config['user_data'], config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # Optimal runs
    objectives = ["cost", "einv", "gwp"]
    objectives = []
    for obj in objectives:
        print(obj)

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

    # --- COMPUTE APPROXIMATE PARETO FRONT --- #

    # Get optimal cost
    opt_cost = es.get_total_cost(f"{config['case_studies_dir']}/{config['case_study_name']}/cost")
    # Get optimal einv
    opt_einv = es.get_total_einv(f"{config['case_studies_dir']}/{config['case_study_name']}/einv")
    # Get optimal einv
    opt_gwp = es.get_total_gwp(f"{config['case_studies_dir']}/{config['case_study_name']}/gwp")

    # Minimizing einv with constraint on cost
    runs = {# 'run1': ('einv', 'cost', opt_cost, [0.003125, 0.00625, 0.0125, 0.025, 0.05, 0.1, 0.15]),
            'run2': ('gwp', 'cost', opt_cost, [0.05, 0.1, 0.2, 0.4]),
            'run3': ('gwp', 'einv', opt_einv, [0.025, 0.05, 0.1, 0.2]),
            }
    # runs = {}
    for run_name in runs.keys():
        print(run_name)
        minimized_obj, constrained_obj, optimal_constrained_obj, epsilons = runs[run_name]
        for epsilon in epsilons:
            print("Run for epsilon", epsilon)
            empty_temp(config['temp_dir'])

            # Printing the .dat files for the optimisation problem
            td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
            es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
            estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
            es.print_estd(estd_out_path, all_data, config["system_limits"])
            # Add specific elements
            es.newline(estd_out_path)
            es.print_param(f"TOTAL_{constrained_obj.upper()}_OP", optimal_constrained_obj,
                           f"Optimal {constrained_obj} of the system", estd_out_path)
            es.newline(estd_out_path)
            es.print_param("EPSILON", epsilon, "Epsilon value", estd_out_path)
            data_fns = [estd_out_path, td12_out_path]

            # Run the model
            mod_fns = [f"{config['model_path']}/main.mod",
                       f"{config['model_path']}/min_{minimized_obj}_epsilon_{constrained_obj}.mod"]
            cs = f"{config['case_studies_dir']}/{config['case_study_name']}/" \
                 f"min_{minimized_obj}_{constrained_obj}_epsilon_{epsilon}/"
            es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                             dump_res_only=True)

    # --- Necessary conditions --- #
    res_to_minimize = {'locals': ["WOOD", "WET_BIOMASS", "WASTE", "RES_WIND", "RES_SOLAR", "RES_HYDRO", "RES_GEO"],
                       'imports': ["ELECTRICITY", "METHANOL", "AMMONIA", "H2", "COAL", "GAS", "LFO", "DIESEL",
                                   "GASOLINE", "BIODIESEL", "BIOETHANOL", "H2_RE", "GAS_RE", "AMMONIA_RE",
                                   "METHANOL_RE"]}
    run_name = 'imports'
    # Pairs (dev cost, dev einv, dev gwp)
    epsilons_tuples = [
        (5/100, 20/100, 100/100), (5/100, 20/100, 200/100),
        (5/100, 40/100, 100/100), (5/100, 40/100, 200/100),
        (10/100, 20/100, 100/100), (10/100, 20/100, 200/100),
        (10/100, 40/100, 100/100), (10/100, 40/100, 200/100)
    ]
    epsilons_tuples = []
    for epsilons_tuple in epsilons_tuples:

        epsilon_cost, epsilon_einv, epsilon_gwp = epsilons_tuple
        print("Run for epsilon", epsilons_tuple)
        empty_temp(config['temp_dir'])

        # Printing the .dat files for the optimisation problem
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(estd_out_path, all_data, config["system_limits"])
        # Add specific elements
        es.newline(estd_out_path)
        es.print_param("TOTAL_COST_OP", opt_cost, "Optimal cost of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("EPSILON_COST", epsilon_cost, "Epsilon value for cost", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("TOTAL_EINV_OP", opt_einv, "Optimal einv of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("EPSILON_EINV", epsilon_einv, "Epsilon value for einv", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("TOTAL_GWP_OP", opt_gwp, "Optimal gwp of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("EPSILON_GWP", epsilon_gwp, "Epsilon value for gwp", estd_out_path)

        es.newline(estd_out_path)
        # es.print_set(technologies_to_minimize, "TECHNOLOGIES_TO_MINIMIZE", estd_out_path)
        es.print_set(res_to_minimize[run_name], "RESOURCES_TO_MINIMIZE", estd_out_path)
        data_fns = [estd_out_path, td12_out_path]

        # Run the model
        # mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/technologies.mod"]
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/resources_3d.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}/" \
             f"{run_name}_{epsilon_cost}_{epsilon_einv}_{epsilon_gwp}/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                         dump_res_only=True)
