# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model

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

    # New optimal solution run
    if 1:  # not os.path.isdir(f"{config['case_studies_dir']}/{config['case_study_name']}"):

        # Empty temp dir
        empty_temp(config['temp_dir'])

        # Saving .dat files
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(estd_out_path, all_data, config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
        data_fns = [estd_out_path, td12_out_path]

        # Running EnergyScope
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/optimal_cost.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}/cost/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                         dump_res_only=True)
        es.extract_results_step2(cs[:-1])

        # Display sankey
        # es.draw_sankey(f"{cs}output/sankey")

    if 1:
        empty_temp(config['temp_dir'])

        # Optimal solution in terms of EINV
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(estd_out_path, all_data, config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
        data_fns = [estd_out_path, td12_out_path]

        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/optimal_einv.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}/einv/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                         dump_res_only=True)
        es.extract_results_step2(cs[:-1])

        # Example to print the sankey from this script
        # es.draw_sankey(f"{cs}output/sankey")

    # Get optimal cost
    opt_cost = es.get_total_cost(f"{config['case_studies_dir']}/{config['case_study_name']}/cost")
    # Get optimal einv
    opt_einv = es.get_total_einv(f"{config['case_studies_dir']}/{config['case_study_name']}/einv")

    # Get approximation of pareto front minimizing einv with constraint on cost
    # epsilons = [0.003125, 0.00625, 0.0125, 0.025, 0.05, 0.1, 0.15]
    epsilons = []
    for epsilon in epsilons:

        print("Run for epsilon", epsilon)
        empty_temp(config['temp_dir'])

        # Printing the .dat files for the optimisation problem
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
        estd_out_path = f"{config['temp_dir']}/ESTD_data_epsilon.dat"
        es.print_estd(estd_out_path, all_data, config["system_limits"])
        # Add specific elements
        es.newline(estd_out_path)
        es.print_param("TOTAL_COST_OP", opt_cost, "Optimal cost of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("EPSILON", epsilon, "Epsilon value", estd_out_path)
        data_fns = [estd_out_path, td12_out_path]

        # Run the model
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/min_einv_epsilon_cost.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}/cost_epsilon_{epsilon}/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                         dump_res_only=True)

    # Get approximation of pareto front minimizing COST with constraint on EINV
    epsilons = []
    for epsilon in epsilons:

        print("Run for epsilon", epsilon)
        empty_temp(config['temp_dir'])

        # Printing the .dat files for the optimisation problem
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
        estd_out_path = f"{config['temp_dir']}/ESTD_data_epsilon.dat"
        es.print_estd(estd_out_path, all_data, config["system_limits"])
        # Add specific elements
        es.newline(estd_out_path)
        es.print_param("TOTAL_EINV_OP", opt_einv, "Optimal einv of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param("EPSILON_EINV", epsilon, "Epsilon value for einv", estd_out_path)
        data_fns = [estd_out_path, td12_out_path]

        # Run the model
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/epsilon_einv.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}_einv_epsilon_{epsilon}/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                         dump_res_only=True)

    # Get epsilon necessary condition
    technologies_to_minimize = ["DEC_HP_ELEC", "DEC_THHP_GAS", "DHN_HP_ELEC"]  # - Heat Pumps
    res_to_minimize = {'locals': ["WOOD", "WET_BIOMASS", "WASTE", "RES_WIND", "RES_SOLAR", "RES_HYDRO", "RES_GEO"],
                       'imports': ["ELECTRICITY", "METHANOL", "AMMONIA", "H2", "COAL", "GAS", "LFO", "DIESEL", "GASOLINE",
                             "BIODIESEL", "BIOETHANOL", "H2_RE", "GAS_RE", "AMMONIA_RE", "METHANOL", "METHANOL_RE"]}
    run_name = 'locals'
    # Pairs (dev cost, dev einv, dev gwp)
    epsilons_tuples = [(5/100, 40/100), (2.5/100, 30/100), (2.5/100, 20/100),
                       (5/100, 30/100), (5/100, 20/100), (5/100, 10/100),
                       (7.5/100, 20/100), (7.5/100, 10/100)]
    epsilons_pairs = []
    for epsilon_pair in epsilons_pairs:

        epsilon_cost, epsilon_einv = epsilon_pair
        print("Run for epsilon", epsilon_pair)
        empty_temp(config['temp_dir'])

        # Printing the .dat files for the optimisation problem
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
        estd_out_path = f"{config['temp_dir']}/ESTD_data_{run_name}.dat"
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
        es.print_set(technologies_to_minimize, "TECHNOLOGIES_TO_MINIMIZE", estd_out_path)
        # es.print_set(technologies_to_minimize, "RESOURCES_TO_MINIMIZE", estd_out_path)
        data_fns = [estd_out_path, td12_out_path]

        # Run the model
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/technologies.mod"]
        # mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/resources.mod"]
        cs = f"{config['case_studies_dir']}/{config['case_study_name']}/{run_name}_{epsilon_cost}_{epsilon_einv}/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                         dump_res_only=True)

        # Example to print the sankey from this script
        # output_dir = f"{cs}output"
        # es.draw_sankey(path=f"{cs}output/sankey")
