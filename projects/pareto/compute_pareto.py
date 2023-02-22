# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model

@author: Antoine Dubois
"""
import energyscope as es
from utils import load_config, load_data, empty_temp

obj_functions = {
    "cost": es.get_total_cost,
    "einv": es.get_total_einv,
    "gwp": es.get_total_gwp
}

if __name__ == '__main__':

    # Load configuration
    config = load_config('config.yaml')
    case_study_dir = f"{config['case_studies_dir']}/{config['case_study_name']}"

    # config['all_data'] = es.import_data(config['data_folders'])
    all_data = load_data(config)

    # Get approximation of pareto front minimizing one objective and constraining the other
    # epsilons = [0.003125, 0.00625, 0.0125, 0.025, 0.05, 0.1, 0.15]
    epsilons = []  # [0.0025, 0.005, 0.01, 0.025, 0.05, 0.075]
    min_obj = 'einv'
    constr_obj = 'cost'

    # Get optimal value of objective
    constr_obj_opt = obj_functions[constr_obj](f"{case_study_dir}/{constr_obj}")
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
        es.print_param(f"TOTAL_{constr_obj.upper()}_OP", constr_obj_opt,
                       f"Optimal {constr_obj} of the system", estd_out_path)
        es.newline(estd_out_path)
        es.print_param(f"EPSILON", epsilon, "Epsilon value", estd_out_path)
        data_fns = [estd_out_path, td12_out_path]

        # Run the model
        mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/min_{min_obj}_epsilon_{constr_obj}.mod"]
        cs = f"{case_study_dir}/{constr_obj}_epsilon_{epsilon}/"
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                         dump_res_only=True)
