# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 22:26:29 2020

Contains functions to read data in csv files and print it with AMPL syntax in ESTD_data.dat
Also contains functions to analyse input data

@author: Paolo Thiran, Antoine Dubois
"""
import logging
import shutil
import pickle
from subprocess import CalledProcessError, run
from typing import Dict, List

import amplpy

from energyscope.step2_output_generator import save_results
from energyscope.amplpy_aux import get_sets, get_parameters, get_results

from energyscope.utils import make_dir
from energyscope.sankey_input import generate_sankey_file


def run_step2(case_study_dir: str, run_file_name: str, ampl_path: str, temp_dir: str):
    """
    Run ESTD STEP 2 using Python.

    :param case_study_dir: path to the case study directory.
    :param run_file_name: path and name of the .run file.
    :param ampl_path: ampl path to execute the .run file.
    :param temp_dir: directory to copy the results.
    """

    make_dir(f"{temp_dir}/output")
    make_dir(f"{temp_dir}/output/hourly_data")
    make_dir(f"{temp_dir}/output/sankey")
    make_dir(f"{temp_dir}/output/sets")
    make_dir(f"{temp_dir}/output/parameters")
    make_dir(f"{temp_dir}/output/results")

    # running ES
    logging.info('Running EnergyScope')
    try:
        run(f"{ampl_path} {run_file_name}", shell=True, check=True)
    except CalledProcessError as e:
        print("The run didn't end normally.")
        print(e)
        exit()

    # Copy temporary results to case studies directory
    shutil.copytree(temp_dir, case_study_dir)

    logging.info('End of run')
    return


def run_step2_new(case_study_dir: str, ampl_path: str, solver_options: Dict,
                  model_fns: List[str], data_fns: List[str], temp_dir: str,
                  dump_res_only: bool = False) -> None:
    """
    Run ESTD STEP 2 using Python and amplpy.

    :param case_study_dir: path to the case study directory.
    :param ampl_path: ampl path to execute the .run file.
    :param solver_options: solver name and solver options
    :param model_fns: list of paths to the model files
    :param data_fns: list of paths to the data files
    :param temp_dir: directory to copy the results.
    :param dump_res_only: save raw results only
    """

    make_dir(f"{temp_dir}/output")
    make_dir(f"{temp_dir}/output/hourly_data")
    make_dir(f"{temp_dir}/output/sankey")
    # make_dir(f"{temp_dir}/output/sets")
    # make_dir(f"{temp_dir}/output/parameters")
    # make_dir(f"{temp_dir}/output/results")

    # running ES
    logging.info('Running EnergyScope')

    # Create AMPL environment
    ampl_trans = amplpy.AMPL(environment=amplpy.Environment(ampl_path))

    # Set solver and solver options
    for option_name in solver_options.keys():
        option_value = solver_options[option_name]
        ampl_trans.setOption(option_name, option_value)

    # Read models
    for model_fn in model_fns:
        ampl_trans.read(model_fn)

    # Read data files
    for data_fn in data_fns:
        ampl_trans.readData(data_fn)

    # Solve
    ampl_trans.solve()

    # Save output
    results = get_results(ampl_trans)
    # for ix, (key, val) in enumerate(results.items()):
    #     val.to_csv(f"{temp_dir}/output/results/{key}.csv")

    parameters = get_parameters(ampl_trans)
    # for ix, (key, val) in enumerate(parameters.items()):
    #     val.to_csv(f"{temp_dir}/output/parameters/{key}.csv")

    sets = get_sets(ampl_trans)
    # import json
    # with open(f"{temp_dir}/output/sets/sets.json", "w") as outfile:
    #     json.dump(sets, outfile, indent=2)

    # Dump results into a pickle file
    if dump_res_only:
        logging.info("Only dump results")
        with open(f"{temp_dir}/output/results.pickle", 'wb') as handle:
            pickle.dump(results, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(f"{temp_dir}/output/parameters.pickle", 'wb') as handle:
            pickle.dump(parameters, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(f"{temp_dir}/output/sets.pickle", 'wb') as handle:
            pickle.dump(sets, handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        logging.info("Saving results")
        save_results(results, parameters, sets, f"{temp_dir}/output/")

        logging.info("Creating Sankey diagram input file")
        generate_sankey_file(results, parameters, sets, f"{temp_dir}/output/sankey/")

    # Copy temporary results to case studies directory
    shutil.copytree(temp_dir, case_study_dir)

    logging.info('End of run')
