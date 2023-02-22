# -*- coding: utf-8 -*-
"""
This script allows to compute necessary conditions in a 3-objective space

@author: Antoine Dubois
"""

import yaml

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
    main_path = f"{config['case_studies_dir']}/{config['case_study_name']}"
    all_data = load_data(config)

    res_to_minimize = yaml.load(open("resources.yaml", 'r'), Loader=yaml.FullLoader)

    # Pairs (dev cost, dev einv)
    obj1 = 'cost'
    obj2 = 'einv'
    epsilon_tuples = [(0.01, 0.02), (0.02, 0.01), (0.01, 0.05), (0.05, 0.01), (0.02, 0.05), (0.05, 0.02)]
    obj1_epsilons_on_pareto = [0.0025, 0.005, 0.01, 0.025, 0.05, 0.075]
    # obj1_epsilons_on_pareto = [0.0025, 0.005, 0.01, 0.025, 0.05, 0.07]
    # obj1_epsilons_on_pareto = [0.075]

    for run_name in ['gas', 'elec-import']:

        print(f"Looking at {run_name}")

        for obj1_epsilon_on_pareto in obj1_epsilons_on_pareto:

            print(f"Doing {obj1_epsilon_on_pareto} of Pareto")
            solution_path = f"{main_path}/min_{obj2}_{obj1}_epsilon_{obj1_epsilon_on_pareto}"
            # Get obj1 of solution
            pareto_obj1 = obj_functions[obj1](solution_path)
            # Get obj2 of solution
            pareto_obj2 = obj_functions[obj2](solution_path)

            print(f"Run for solution with {obj1} {pareto_obj1} and {obj2} {pareto_obj2}")
            empty_temp(config['temp_dir'])

            for epsilon1, epsilon2 in epsilon_tuples:

                print(f"Doing {epsilon1} and {epsilon2} in tuples")

                # Printing the .dat files for the optimisation problem
                td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
                es.print_12td(td12_out_path, all_data['Time_series'], config["step1_output"])
                estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
                es.print_estd(estd_out_path, all_data, config["system_limits"])

                # Add specific elements
                es.newline(estd_out_path)
                es.print_param(f"PARETO_SOLUTION_{obj1.upper()}", pareto_obj1,
                               f"{obj1.title()} at the Pareto solution", estd_out_path)
                es.newline(estd_out_path)
                es.print_param(f"EPSILON_{obj1.upper()}", epsilon1, f"Epsilon value for {obj1}", estd_out_path)
                es.newline(estd_out_path)
                es.print_param(f"PARETO_SOLUTION_{obj2.upper()}", pareto_obj2,
                               f"{obj2.title()} at the Pareto solution the system", estd_out_path)
                es.newline(estd_out_path)
                es.print_param(f"EPSILON_{obj2.upper()}", epsilon2, f"Epsilon value for {obj2}", estd_out_path)

                es.newline(estd_out_path)
                es.print_set(res_to_minimize[run_name], "RESOURCES_TO_MINIMIZE", estd_out_path)
                data_fns = [estd_out_path, td12_out_path]

                # Run the model
                mod_fns = [f"{config['model_path']}/main.mod", f"{config['model_path']}/resources_{obj1}_{obj2}.mod"]
                cs = f"{main_path}/{run_name}_{obj1}_{obj2}_{epsilon1}_{epsilon2}_{obj1_epsilon_on_pareto}/"
                es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, data_fns, config['temp_dir'],
                                 dump_res_only=False)
