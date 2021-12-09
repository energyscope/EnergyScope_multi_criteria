# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 22:26:29 2020

Contains functions to read data in csv files and print it with AMPL syntax in ESTD_data.dat
Also contains functions to analyse input data

@author: Paolo Thiran, Antoine Dubois
"""
import logging
import shutil
from subprocess import CalledProcessError, run

from energyscope.misc.utils import make_dir


# TODO comment
# Function to run ES from python
def run_energyscope(case_study_dir:str, run_file_name:str, ampl_path:str, temp_dir:str):
    """
    Run ES using Python.
    :param case_study_dir: path to the case study directory.
    :param run_file_name: path and name of the .run file.
    :param ampl_path: ampl path to execute the .run file.
    :param temp_dir: directory to copy the results.
    """

    make_dir(f"{temp_dir}/output")
    make_dir(f"{temp_dir}/output/hourly_data")
    make_dir(f"{temp_dir}/output/sankey")

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
