# -*- coding: utf-8 -*-
"""
Created on Dec 16 2021

Contains functions to perform step1 of EnergyScope

@author: Antoine Dubois (inspired from work from Paolo Thiran)
"""

import os
from sys import platform
from pathlib import Path
import csv
import logging

import numpy as np
import pandas as pd

import amplpy

from energyscope.amplpy_aux import get_results
import energyscope as es


def print_step1_data(nbr_td: int, input_fn: str, output_fn: str) -> None:
    """
    Convert time-series in CSV format to ampl-friendly format

    Parameters
    ----------
    nbr_td : int
        Number of selected time steps
    input_fn: str
        Input file name
    output_fn: str
        Output file name
    """

    data = pd.read_csv(input_fn, index_col=0)
    data_header = data.loc[["Type", "Weights", "Norm"]]
    data = data.loc[[str(i) for i in range(1, 366)]].astype(float)

    # Add header
    header_fn = os.path.join(Path(__file__).parents[0], 'headers/step1_header.txt')
    with open(output_fn, mode='w', newline='') as file, open(header_fn, 'r') as header:
        for line in header:
            file.write(line)
    es.newline(output_fn)

    # Specify number of TDs
    es.print_param('Nbr_TD', nbr_td, '', output_fn)
    es.newline(output_fn)

    # Print comments
    data_header.index = [f"# {idx}" for idx in data_header.index]
    data_header.to_csv(output_fn, sep='\t', mode='a', header=False, index=True, quoting=csv.QUOTE_NONE)

    # Print data
    es.print_df("param Ndata :", es.ampl_syntax(data.round(9), ''), output_fn)


def print_step1_out(ampl_trans: amplpy.AMPL, step1_out_fn: str) -> None:
    """
    Print results of Step 1 of EnergyScope TD

    Parameters
    ----------
    ampl_trans : amplpy.AMPL
        AMPL translator containing the results of the aggregation
    step1_out_fn: str
        Output file name

    """
    # Get results
    results_step1 = get_results(ampl_trans)

    # Do some manipulation on the cluster matrix
    cm = results_step1['Cluster_matrix'].pivot(index='index0', columns='index1', values='Cluster_matrix.val')
    cm.index.name = None
    out = pd.DataFrame(cm.mul(np.arange(1, 366), axis=0).sum(axis=0)).astype(int)
    out.to_csv(step1_out_fn, header=False, index=False, sep='\t')


def run_step1(nbr_td: int, data_path: str, ampl_path: str, solver_path: str) -> None:
    """
    Run Step 1 of EnergyScope TD (i.e. time series aggregation) with a given number of time steps

    Parameters
    ----------
    nbr_td : int
        Number of selected time-steps
    data_path: str
        Path to Data directory
    ampl_path: str
        Path to AMPL
    solver_path: str
        Path to solver

    """
    # running ES
    logging.info('Running STEP1')

    # Create AMPL environment
    ampl_trans = amplpy.AMPL(environment=amplpy.Environment(ampl_path))

    # Set solver
    ampl_trans.setOption('solver', solver_path)

    # Read model
    model_fn = os.path.join(Path(__file__).parents[0], 'models/step1.mod')
    ampl_trans.read(model_fn)

    # Convert data in appropriate format and add them to the environment
    input_fn = os.path.join(data_path, "step1_input.csv")
    data_fn = os.path.join(Path(__file__).parents[0], f'step1_io/data_td_{nbr_td}.dat')
    print_step1_data(nbr_td, input_fn, data_fn)
    ampl_trans.readData(data_fn)

    # Solve
    ampl_trans.solve()

    # Print output
    output_fn = os.path.join(Path(__file__).parents[0], f'step1_io/TD_of_days_{nbr_td}.out')
    print_step1_out(ampl_trans, output_fn)


def config_path():
    """
    Define the user CPLEX and AMPL path.
    :return: CPLEX and AMPL path.
    """

    if platform == "linux":
        cplex_path_ = "/home/jdumas/PycharmProjects/ampl_linux-intel64/cplex"
        ampl_path_ = '/home/jdumas/PycharmProjects/ampl_linux-intel64'
    else:
        ampl_path_ = '/Users/dumas/PycharmProjects/ampl_macos64'
        cplex_path_ = "cplex"

    return ampl_path_, cplex_path_


if __name__ == '__main__':

    # WARNING: the user must adapt its CPLEX and AMPL paths into the function config_path()
    ampl_path_, cplex_path_ = config_path()
    nbr_td_ = 12
    data_path = os.path.join(Path(__file__).parents[1], "Data")
    run_step1(nbr_td_, data_path, ampl_path_, cplex_path_)
