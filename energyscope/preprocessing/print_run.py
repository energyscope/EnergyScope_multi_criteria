# -*- coding: utf-8 -*-
"""
This script allows to print the .run files.

@author: Jonathan Dumas, Antoine Dubois
"""
import os
from typing import List
from pathlib import Path


def print_mod(run_fn: str, mod_fns: List[str]) -> None:
    """
    Add .mod imports to run file

    :param run_fn: Path to .run file
    :param mod_fns: Paths to .mod files
    """
    with open(run_fn, mode='a', newline='') as file:
        file.write("\n# Load model\n")
        for mod_fn in mod_fns:
            file.write(f"model {mod_fn};\n")


def print_dat(run_fn: str, dat_fns: List[str]) -> None:
    """
    Add .mod imports to run file
    :param run_fn: Path to .run file
    :param dat_fns: Paths to .dat files
    """
    with open(run_fn, mode='a', newline='') as file:
        file.write("\n# Load data\n")
        for dat_fn in dat_fns:
            file.write(f"data {dat_fn};\n")


def print_options(run_fn: str, options: dict) -> None:
    """
    Add options to run file
    :param run_fn: Path to .run file
    :param options: Dictionary whose keys are AMPL options (e.g. 'show_stats', 'cplex_options') and values are the
    values to be attributed to those options
    """
    with open(run_fn, mode='a', newline='') as file:
        file.write("\n# Run options\n")
        for option_name in options.keys():
            option_value = options[option_name]
            if isinstance(option_value, list):
                for value in option_value:
                    file.write(f'option {option_name} "{value}";\n')
            else:
                file.write(f'option {option_name} "{option_value}";\n')


def print_solve(run_fn: str) -> None:
    """
    Add AMPL solving script to run file
    :param run_fn: Path to .run file
    """

    solve_fn = os.path.join(Path(__file__).parents[0], 'run_solve.txt')
    with open(run_fn, mode='a', newline='') as file, open(solve_fn, 'r') as header:
        for line in header:
            file.write(line)


def print_save(run_fn: str, output_dir: str) -> None:
    """
    Add the AMPL scripts used to save results to the run file
    :param run_fn: Path to .run file
    :param output_dir: Path to the directory where the output of the model is to be generated (e.g. used as PathName in
    AMPL_utils/print.run and AMPL_utils/sankey.run)
    """

    with open(run_fn, mode='a', newline='') as file:
        file.write("\n# Saving sets and parameters to output file\n")
        file.write(f'param PathName symbolic := "{output_dir}";\n')

        solve_fn = os.path.join(Path(__file__).parents[0], 'run_save.txt')
        with open(solve_fn, 'r') as header:
            for line in header:
                file.write(line)

        ampl_utils_dir = os.path.join(Path(__file__).parents[2], "AMPL_utils")
        file.write(f'\t\t\tinclude {ampl_utils_dir}/print.run;\n')
        file.write(f'\t\t\tinclude {ampl_utils_dir}/sankey.run;\n')
        file.write("\t\t\texit 0;\n\t\t}\n\t}\n}")


def print_run(run_fn: str, mod_fns: List[str], dat_fns: List[str], options: dict, output_dir: str) -> None:
    """
    Print the .run file.

    :param run_fn: Path where the .run file needs to be generated
    :param mod_fns: Paths to .mod files
    :param dat_fns: Paths to .dat files
    :param options: Dictionary whose keys are AMPL options (e.g. 'show_stats', 'cplex_options') and values are the
    values to be attributed to those options
    :param output_dir: Path to the directory where the output of the model is to be generated (e.g. used as PathName in
    AMPL_utils/print.run and AMPL_utils/sankey.run)
    """

    # Add header
    header_fn = os.path.join(Path(__file__).parents[0], 'run_header.txt')
    with open(run_fn, mode='w', newline='') as file, open(header_fn, 'r') as header:
        for line in header:
            file.write(line)

    # Add .mod imports
    print_mod(run_fn, mod_fns)
    # Add .dat import
    print_dat(run_fn, dat_fns)
    # Add run options
    print_options(run_fn, options)
    # Add solving
    print_solve(run_fn)
    # Add saving
    print_save(run_fn, output_dir)
