# -*- coding: utf-8 -*-
"""
This script allows to print the .run files.

@author: Jonathan Dumas
"""
import yaml
import os
from sys import platform
import pandas as pd


def load_config(config_fn: str):
    """
    Load the configuration into a dict.
    :param config_fn: configuration file name.
    :return: a dict with the configuration.
    """

    # Load parameters
    cfg = yaml.load(open(config_fn, 'r'), Loader=yaml.FullLoader)

    # Extend path
    for param in ['case_studies_dir', 'user_data', 'developer_data', 'temp_dir', 'ES_path', 'step1_output']:
        cfg[param] = os.path.join(cfg['energyscope_dir'], cfg[param])

    return cfg

def print_master_run_file(config: dict):
    """
    Print the master.run file.
    :param config: configuration file with the path into a dict.
    """
    header = ['################################################################################',
              '##																			  ##',
              '##                     			MASTER RUN								      ##',
              '##																			  ##',
              '################################################################################',
              '## WARNING: when executed from a working directory, it is required to specify  #',
              '## the path of the .mod, .dat, and .run files from the working directory.      #',
              '################################################################################',
              '#',
              '# 1. Load standard model',
              'model ' + config['ES_path'] + '/ESTD_model.mod;',
              # '#',
              # '# 2. specify the path of the temp folder',
              # 'param PathName symbolic default "' + config['temp_dir'] + '/output/";',
              # 'print PathName;',
              '#',
              '# 2. Load standard data',
              'data ' + config['temp_dir'] + '/ESTD_data.dat;  # not TDs depending data',
              'data ' + config['temp_dir'] + '/ESTD_12TD.dat;  # TDs depending data',
              '#',
              '# 3. Load main run',
              'include ' + config['ES_path'] + '/ESTD_main.run;']
    out_path_master_run = 'ampl_model/master.run'
    with open(out_path_master_run, mode='w', newline='') as f:
        for line in header:
            f.write(line)
            f.write('\n')
    f.close()

def print_main_run_file(config: dict):
    """
    Print the master.run file.
    :param config: configuration file with the path into a dict.
    """
    cplex_path_linux = '"/home/jdumas/PycharmProjects/ampl_linux-intel64/cplex"' # on linux -> need to specify the path to cplex
    cplex_path_mac = 'cplex' # no need on mac to specify the cplex path
    if platform == "linux":
        cplex_path = cplex_path_linux
    else:
        cplex_path = cplex_path_mac

    header = ['################################################################################',
              '##																			  ##',
              '##                     			SOLVER OPTIONS								  ##',
              '##																			  ##',
              '################################################################################',
              '#',
              'option solver '+cplex_path+';',
              ' ',
              'option show_stats 1;  # show statistics',
              ' ',
              'option cplex_options "mipdisplay 5 mipinterval 1000";',
              ' ',
              'option log_file "log.txt";   #write the log in a .txt file. Create the file before running.',
              ' ',
              '# option cplex_options $cplex_options "startbasis ./output/solution.bas "; # to read previously existing path',
              'option cplex_options $cplex_options "endbasis ./output/solution.bas "; # to write how to solve',
              ' ',
              '# Saving and starting from last solution. Starting from last solution is not very efficient.',
              '# option cplex_options $cplex_options "startsol ./output/solution.sol "; # to read previously existing file',
              '# option cplex_options $cplex_options "endsol ./output/solution.sol "; # to write file',
              ' ',
              'option cplex_options $cplex_options "mipgap 0.01";',
              'option cplex_options $cplex_options "timelimit 3600";',
              ' ',
              '/*',
              '# Save pool of solutions',
              'option cplex_options "poolstub=PoolSol poolcapacity=10 populate=1 poolintensity=4 poolreplace=2";',
              '*/',
              ' ',
              '################################################################################',
              '##																			  ##',
              '##                     			RUN & SAVE PATH								  ##',
              '##																			  ##',
              '################################################################################',
              ' ',
              '# Specify the path of the temp folder',
              'param PathName symbolic default "' + config['temp_dir'] + '/output/";',
              'print PathName;',
              ' ',
              'let f_min["PV"] := 3.846;',
              'let f_min["WIND_ONSHORE"] := 1.177;',
              'let f_min["WIND_OFFSHORE"] := 0.692;',
              'let f_min["HYDRO_RIVER"] := 0.11;',
              'let re_share_primary := 0.0;',
              ' ',
              'let gwp_limit := Infinity;',
              'let cost_limit := Infinity;',
              'let einv_limit := Infinity;',
              ' ',
              'option times 1;  # show time',
              'option gentimes 1;  # show time',
              ' ',
              'solve;',
              ' ',
              'display solve_result_num;',
              'display _solve_elapsed_time;',
              ' ',
              '## Saving sets and parameters to output file',
              ' ',
              'option times 0; # show time',
              'option gentimes 0; # show time',
              ' ',
              'if solve_result = "limit" then { # To avoid post treatment error',
              '    print "TIME OUT";',
              '    exit 1;',
              '}',
              'else {',
              '    if solve_result = "infeasible" then {',
              '        print "INFEASIBLE";',
              '        exit 1',
              '    }',
              '    else {',
              '        if solve_result = "failure" then {',
              '        print "FAILURE";',
              '        exit 1',
              '        }',
              '        else {',
              '            include ampl_model/utils/print.run',
              '            include ampl_model/utils/sankey.run',
              '            exit 0',
              '        }',
              '    }',
              '}# END SAVING'
              ]
    out_path_master_run = 'ampl_model/ESTD_main.run'
    with open(out_path_master_run, mode='w', newline='') as f:
        for line in header:
            f.write(line)
            f.write('\n')
    f.close()

if __name__ == '__main__':

    # Get the current working directory
    cwd = os.getcwd()
    # Print the current working directory
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config.yaml')

    # Printing data #
    print_main_run_file(config=config)