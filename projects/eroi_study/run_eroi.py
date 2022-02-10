# -*- coding: utf-8 -*-
"""
This script modifies the input data and runs the EnergyScope model.

@author: Paolo Thiran, Matija Pavičević, Antoine Dubois, Jonathan Dumas
"""

import yaml
import os

import pandas as pd
import energyscope as es
import numpy as np

from sys import platform

from energyscope.utils import make_dir, load_config, get_FEC_from_sankey
from energyscope.postprocessing import get_total_einv
from projects.eroi_study.res_RE_domestic_share import compute_fec
from projects.eroi_study.utils_res import get_gwp, get_cost

def loop_eroi_computation(range_val, dir_name: str, GWP_op_ini: float, config: dict, GWP_tot:bool=True):
    """
    Minimize the Einv for several GWP <= p*GWP_op_ini with p a percentage, with GWP being either GWP_tot or GWP_op.
    :param range_val: range of p.
    :param dir_name: directory name.
    :param GWP_op_ini: GWP_op initial value.
    :param GWP_tot: to select to constrain GWP_tot or GWP_op
    :param config: configuration file.
    """
    for gwp_tot_max, cs_name in zip(np.asarray([i for i in range_val]) * GWP_op_ini / 100, ['run_' + str(i) for i in range_val]):
        print('Case in progress %s' % cs_name)
        cs = f"{config['case_studies_dir']}/{dir_name + '/' + cs_name}"
        # Update the GWP limit
        config["system_limits"]['GWP_limit'] = gwp_tot_max
        # Saving data to .dat files into the config['temp_dir'] directory
        estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
        es.print_estd(out_path=estd_out_path, data=all_data, system_limits=config["system_limits"])
        td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
        es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

        # Running EnergyScope
        if GWP_tot:
            # INCLUDING GREY EMISSIONS
            # TotalGWP = sum {j in TECHNOLOGIES} (GWP_constr [j] / lifetime [j]) + sum {i in RESOURCES} GWP_op [i]
            mod_fns = [f"{config['ES_path']}/ESTD_model.mod"]
        else:
            # JUST RESOURCES
            # TotalGWP = sum {i in RESOURCES} GWP_op [i]
            mod_fns = [f"{config['ES_path']}/ESTD_model_GWP_op.mod"]
        es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, [estd_out_path, td12_out_path], config['temp_dir'])
        es.draw_sankey(sankey_dir=f"{cs}/output/sankey")


DOMESTIC_RE_SHARE = 0.3 # (%) Domestic RE share in the primary energy mix (by default is set to 0 in the config file)

if __name__ == '__main__':

    # Get the current working directory
    cwd = os.getcwd()
    # Print the current working directory
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config.yaml')
    config['system_limits']['re_be_share_primary'] = DOMESTIC_RE_SHARE

    # Create the temp_dir if it does not exist
    make_dir(config['temp_dir'])

    # Loading data
    all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # Saving data to .dat files into the config['temp_dir'] directory
    estd_out_path = f"{config['temp_dir']}/ESTD_data.dat"
    es.print_estd(out_path=estd_out_path, data=all_data, system_limits=config["system_limits"])
    td12_out_path = f"{config['temp_dir']}/ESTD_12TD.dat"
    # WARNING: check if STEP1 is done
    if not os.path.isfile(config["step1_output"]):
        print('WARNING: the STEP1 that consists of generating the 12 typical days must be conducted'
              ' before to compute the TD_of_days.out file located in %s' % (config["step1_output"]))
    es.print_12td(out_path=td12_out_path, time_series=all_data['Time_series'], step1_output_path=config["step1_output"])

    # --------------------------------------------------
    # Min Einv
    # GWP_tot is not constrained
    # -> allows to compute GWP_op^i
    # -------------------------------------------------

    GWP_tot = True
    if GWP_tot:
        dir_name = 'einv_GWP_tot_'+str(int(100 * DOMESTIC_RE_SHARE))
    else:
        dir_name = 'einv_GWP_op_'+str(int(100 * DOMESTIC_RE_SHARE))

    # Running EnergyScope
    mod_fns = [f"{config['ES_path']}/ESTD_model.mod"]
    cs = f"{config['case_studies_dir']}/{dir_name+'/'+config['case_study_name']}"
    es.run_step2_new(cs, config['AMPL_path'], config['options'], mod_fns, [estd_out_path, td12_out_path], config['temp_dir'])
    es.draw_sankey(sankey_dir=f"{cs}/output/sankey")

    ################################################
    # Compute the EROI "final":
    # -> compute the FEC from the year_balance.csv
    # -> get the Einv
    # -> EROI "final" = Eout/Einv, with Eout = FEC
    # Note: Eout could be also defined as: Eout = EUD * conversion_factor
    ################################################

    # Compute the FEC from the year_balance.csv
    GWP_val = get_gwp(cs=cs)
    cost_val = get_cost(cs=cs) /1000 # bEUR/y
    df_year_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0)
    fec_details, fec_tot = compute_fec(data=df_year_balance, user_data=config['user_data'])
    fec_tot_val = sum(fec_tot.values()) / 1000  # TWh
    # Compute the FEC from SANKEY
    ef = get_FEC_from_sankey(case_study_dir=cs, col=config['case_study_name'])
    fec_sankey = ef.sum()
    einv = get_total_einv(cs) / 1000  # TWh
    print('FEC SANKEY %.2f vs year_balance %.2f [TWh/y]' % (fec_sankey, fec_tot_val))
    print('EROI SANKEY %.2f vs year_balance %.2f' % (fec_sankey / einv, fec_tot_val / einv))
    print('GWP_constr %.1f GWP_op %.1f [MtC02/y]' %(GWP_val['GWP_constr'], GWP_val['GWP_op']))
    print('C_inv %.1f C_maint %.1f C_op %.1f [bEUR/y]' %(cost_val['C_inv'], cost_val['C_maint'], cost_val['C_op']))

    # -----------------------------------------------
    # Min Einv
    # s.t. GWP_tot <= p * GWP_op^i with p a percentage and GWP_op^i computed by Min Einv without contraint on GWP_tot
    # -----------------------------------------------
    # GWP_op_ini = get_gwp(cs=f"{config['case_studies_dir']}/{dir_name + '/run_100'}")['GWP_op']
    GWP_op_ini = get_gwp(cs=f"{config['case_studies_dir']}/{'einv_GWP_tot_0/run_100'}")['GWP_op']
    print('GWP_limit initial %.1f [MtC02/y]' %(GWP_op_ini/1000))
    range_val = range(100, 0, -5)
    loop_eroi_computation(range_val=range_val, dir_name=dir_name, GWP_op_ini=GWP_op_ini, config=config, GWP_tot=GWP_tot)