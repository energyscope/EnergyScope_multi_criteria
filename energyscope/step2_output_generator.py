# -*- coding: utf-8 -*-
"""
Created on Jan 17 2022

Contains functions to generate appropriate output files from an ESTD STEP 2 run

@author: Antoine Dubois
"""
import itertools
import logging
from typing import Dict

import pandas as pd
from functools import reduce
from itertools import product
import pickle

from energyscope.amplpy_aux import simplify_df, time_to_pandas
from energyscope.sankey_input import generate_sankey_file


def save_breakdowns(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                    sets: Dict, output_dir: str) -> None:
    """See save_results"""

    # Cost Breakdown
    c_inv = simplify_df(results["C_inv"])
    c_maint = simplify_df(results["C_maint"])
    c_op = simplify_df(results["C_op"])

    tau = simplify_df(parameters["tau"])
    c_inv["C_inv"] = c_inv["C_inv"] * tau["tau"]

    cost_breakdown = reduce(lambda left, right: pd.merge(left, right, on='Name', how='outer'),
                            [c_inv, c_maint, c_op])
    cost_breakdown = cost_breakdown.fillna(0).round(6).sort_index()
    cost_breakdown.to_csv(f"{output_dir}cost_breakdown.csv")

    # GWP breakdown
    gwp_constr = simplify_df(results["GWP_constr"])
    gwp_op = simplify_df(results["GWP_op"])

    lifetime = simplify_df(parameters["lifetime"])
    gwp_constr["GWP_constr"] = gwp_constr["GWP_constr"] / lifetime["lifetime"]

    gwp_breakdown = reduce(lambda left, right: pd.merge(left, right, on='Name', how='outer'), [gwp_constr, gwp_op])
    gwp_breakdown = gwp_breakdown.fillna(0).round(6).sort_index()
    gwp_breakdown.to_csv(f"{output_dir}gwp_breakdown.csv")

    # Einv breakdown
    einv_constr = simplify_df(results["Einv_constr"])
    einv_op = simplify_df(results["Einv_op"])

    lifetime = simplify_df(parameters["lifetime"])
    einv_constr["Einv_constr"] = einv_constr["Einv_constr"] / lifetime["lifetime"]

    einv_breakdown = reduce(lambda left, right: pd.merge(left, right, on='Name', how='outer'), [einv_constr, einv_op])
    einv_breakdown = einv_breakdown.fillna(0).round(6).sort_index()
    einv_breakdown.to_csv(f"{output_dir}einv_breakdown.csv")

    # Resources breakdown
    avail = simplify_df(parameters["avail"]).squeeze()
    f_t = results['F_t'].set_index(['index0', 'index1', 'index2']).squeeze()
    t_op = parameters['t_op'].set_index(['index0', 'index1']).squeeze()
    times = time_to_pandas(sets)
    resources = sorted(sets['RESOURCES'])

    resources_breakdown = pd.DataFrame(0., index=resources, columns=['Used', 'Potential'])
    resources_breakdown.index.name = 'Name'
    for res in resources:
        resources_breakdown.loc[res, 'Used'] = (f_t.loc[res].loc[times] * t_op.loc[times]).sum()
        resources_breakdown.loc[res, 'Potential'] = avail[res]
    resources_breakdown.round(6).to_csv(f"{output_dir}resources_breakdown.csv")


def save_tech_res_matrices(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                           sets: Dict, output_dir: str) -> None:
    """See save_results"""

    # Cost Op Tech and GWP tech
    # Results
    f_t = results['F_t'].set_index(['index0', 'index1', 'index2']).squeeze()
    storage_in = results['Storage_in'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()
    storage_out = results['Storage_out'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()

    # Parameters
    t_op = parameters['t_op'].set_index(['index0', 'index1']).squeeze()
    c_op = parameters['c_op'].set_index(['index0']).squeeze()
    gwp_op = parameters['gwp_op'].set_index(['index0']).squeeze()
    layers_in_out = parameters["layers_in_out"].pivot(index='index0', columns='index1', values='layers_in_out')

    # Sets
    techs_set = sorted(list(set(sets['TECHNOLOGIES']) - set(sets['STORAGE_TECH'])))
    resources_set = sorted(list(set(sets['RESOURCES']) - set(sets['BIOFUELS']) - set(sets['EXPORT'])))
    cost_op_tech = pd.DataFrame(0., index=techs_set, columns=resources_set, dtype=float)
    gwp_tech = pd.DataFrame(0., index=techs_set, columns=resources_set, dtype=float)
    times = time_to_pandas(sets)

    for res in resources_set:

        # The total share of technologies
        den = pd.Series(0., index=times)
        for tech in techs_set:
            den += (layers_in_out.loc[tech, res] * f_t.loc[tech]).loc[times]
        for tech in sets['STORAGE_TECH']:
            den += storage_out.loc[tech, res].loc[times] - storage_in.loc[tech, res].loc[times]
        den = den.apply(lambda x: min(-1e-6, x))

        for tech in techs_set:

            if layers_in_out.loc[tech, res] == 0:
                continue

            # The specific resources emissions/cost times the share of the technology
            num_cost = (c_op.loc[res] * f_t.loc[res].loc[times] * t_op.loc[times]) * \
                       (layers_in_out.loc[tech, res] * f_t.loc[tech].loc[times])
            num_gwp = (gwp_op.loc[res] * f_t.loc[res].loc[times] * t_op.loc[times]) * \
                      (layers_in_out.loc[tech, res] * f_t.loc[tech].loc[times])

            cost_op_tech.loc[tech, res] = (num_cost / den).sum()
            gwp_tech.loc[tech, res] = (num_gwp / den).sum()

    cost_op_tech.to_csv(f"{output_dir}cost_op_tech.csv")
    gwp_tech.to_csv(f"{output_dir}gwp_tech.csv")


def save_losses(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                sets: Dict, output_dir: str) -> None:
    """See save_results"""

    network_losses = results['Network_losses'].set_index(['index0', 'index1', 'index2']).squeeze()
    t_op = parameters['t_op'].set_index(['index0', 'index1']).squeeze()
    euts = sorted(sets['END_USES_TYPES'])
    times = time_to_pandas(sets)

    losses = pd.DataFrame(0., index=euts, columns=['Losses'])
    losses.index.name = 'End use'
    for eut in euts:
        losses.loc[eut] = (network_losses.loc[eut].loc[times] * t_op.loc[times]).sum()

    losses.round(3).to_csv(f"{output_dir}losses.csv")


def save_assets(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                sets: Dict, output_dir: str) -> None:
    """See save_results"""

    # Results
    c_inv = simplify_df(results["C_inv"]).squeeze()
    c_maint = simplify_df(results["C_maint"]).squeeze()
    gwp_constr = simplify_df(results["GWP_constr"]).squeeze()
    f = simplify_df(results["F"]).squeeze()

    f_t = results['F_t'].set_index(['index0', 'index1', 'index2']).squeeze()
    storage_in = results['Storage_in'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()
    storage_out = results['Storage_out'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()

    # Parameters
    lifetime = simplify_df(parameters["lifetime"]).squeeze()
    tau = simplify_df(parameters["tau"]).squeeze()
    c_p = simplify_df(parameters["c_p"]).squeeze()
    f_min = simplify_df(parameters["f_min"]).squeeze()
    f_max = simplify_df(parameters["f_max"]).squeeze()
    fmin_perc = simplify_df(parameters["fmin_perc"]).squeeze()
    fmax_perc = simplify_df(parameters["fmax_perc"]).squeeze()

    t_op = parameters['t_op'].set_index(['index0', 'index1']).squeeze()
    storage_eff_in = parameters['storage_eff_in'].set_index(['index0', 'index1']).squeeze()
    storage_eff_out = parameters['storage_eff_out'].set_index(['index0', 'index1']).squeeze()

    # Sets
    times = time_to_pandas(sets)
    techs_of_euts = list(itertools.chain.from_iterable([sets['TECHNOLOGIES_OF_END_USES_TYPE'][eut]
                                                        for eut in sets['END_USES_TYPES']]))
    storage_techs = sets['STORAGE_TECH']
    infra = sets['INFRASTRUCTURE']
    all_techs = sorted(techs_of_euts + storage_techs + infra)

    assets = pd.DataFrame(0., index=['UNITS'] + all_techs,
                          columns=['c_inv', 'c_maint', 'lifetime', 'f_min', 'f', 'f_max',
                                   'fmin_perc', 'f_perc', 'fmax_perc', 'c_p', 'c_p_max', 'tau', 'gwp_constr'],
                          dtype=float)
    assets.index.name = 'TECHNOLOGIES'
    assets.loc['UNITS'] = ['[MCHCapitalf]', '[MCHCapitalf/y]', '[y]', '[GW or GWh]', '[GW or GWh]', '[GW or GWh]',
                           '[0-1]', '[0-1]', '[0-1]', '[0-1]', '[0-1]', '[-]', '[ktCO2-eq.]']

    # End use type technologies
    for eut in sets['END_USES_TYPES']:

        den = 0
        for tech in sets['TECHNOLOGIES_OF_END_USES_TYPE'][eut]:
            den += f_t.loc[tech].loc[times].sum()
        den = max(1e-5, den)

        for tech in sets['TECHNOLOGIES_OF_END_USES_TYPE'][eut]:

            # TODO c_p and c_p_max inverted in original printer ?
            assets.loc[tech, ['c_inv', 'c_maint', 'lifetime', 'f_min', 'f', 'f_max', 'fmin_perc', 'fmax_perc',
                              'c_p_max', 'tau', 'gwp_constr']] = \
                [c_inv[tech], c_maint[tech], lifetime[tech], f_min[tech], f[tech],
                 f_max[tech], fmin_perc[tech], fmax_perc[tech], c_p[tech], tau[tech],
                 gwp_constr[tech]]
            # f_perc
            assets.loc[tech, 'f_perc'] = f_t.loc[tech].loc[times].sum() / den
            # c_p
            assets.loc[tech, 'c_p'] = (f_t.loc[tech].loc[times] * t_op.loc[times]).sum() / (8760 * max(f[tech], 1e-4))

    # Storage techs
    for tech in storage_techs:

        assets.loc[tech, ['c_inv', 'c_maint', 'lifetime', 'f_min', 'f', 'f_max', 'fmin_perc', 'f_perc', 'fmax_perc',
                          'c_p_max', 'tau', 'gwp_constr']] = \
            [c_inv[tech], c_maint[tech], lifetime[tech], f_min[tech], f[tech],
             f_max[tech], fmin_perc[tech], -1, fmax_perc[tech], c_p[tech], tau[tech],
             gwp_constr[tech]]
        # c_p
        for lay in sets['LAYERS']:
            if storage_eff_out[tech, lay] <= 0:
                continue
            term = storage_out.loc[tech, lay].loc[times] / storage_eff_out.loc[tech, lay] \
                - storage_in.loc[tech, lay].loc[times] * storage_eff_in.loc[tech, lay]
            term = term.apply(lambda x: -min(x, 0)).sum()
            assets.loc[tech, 'c_p'] += term.sum() / (8760.0 * max(f[tech], 1e-4))

    # Infrastructure
    for tech in infra:

        assets.loc[tech, ['c_inv', 'c_maint', 'lifetime', 'f_min', 'f', 'f_max', 'fmin_perc', 'f_perc', 'fmax_perc',
                          'c_p_max', 'tau', 'gwp_constr']] = \
            [c_inv[tech], c_maint[tech], lifetime[tech], f_min[tech], f[tech],
             f_max[tech], fmin_perc[tech], -1, fmax_perc[tech], c_p[tech], tau[tech],
             gwp_constr[tech]]
        # c_p
        assets.loc[tech, 'c_p'] = (f_t.loc[tech].loc[times] * t_op.loc[times]).sum() / (8760 * max(f[tech], 1e-4))

    assets.loc[all_techs] = assets.loc[all_techs].astype(float).round(6)
    assets.to_csv(f"{output_dir}assets.csv")


def save_year_balance(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                      sets: Dict, output_dir: str) -> None:
    """See save_results"""

    # Sets
    layers = sorted(sets["LAYERS"])
    res_and_techs = list(set(sets['RESOURCES']) | set(sets['TECHNOLOGIES']) - set(sets['STORAGE_TECH']))
    storage_techs = sets['STORAGE_TECH']
    all_techs = sorted(res_and_techs + storage_techs)
    times = time_to_pandas(sets)

    # Results
    f_t = results['F_t'].set_index(['index0', 'index1', 'index2']).squeeze()
    end_uses = results['End_uses'].set_index(['index0', 'index1', 'index2']).squeeze()
    storage_in = results['Storage_in'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()
    storage_out = results['Storage_out'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()

    # Parameters
    layers_in_out = parameters['layers_in_out'].set_index(['index0', 'index1']).squeeze()

    year_balance = pd.DataFrame(0., index=all_techs + ['END_USES_DEMAND'], columns=layers, dtype=float)
    for lay in layers:

        for rt in res_and_techs:
            year_balance.loc[rt, lay] = (layers_in_out.loc[rt, lay] * f_t.loc[rt].loc[times]).sum()

        for tech in storage_techs:
            year_balance.loc[tech, lay] = (storage_out.loc[tech, lay].loc[times]
                                           - storage_in.loc[tech, lay].loc[times]).sum()

        year_balance.loc['END_USES_DEMAND', lay] = end_uses.loc[lay].loc[times].sum()

    year_balance.round(6).to_csv(f"{output_dir}year_balance.csv")


def save_layers(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                sets: Dict, output_dir: str) -> None:
    """See save_results"""

    # Sets
    layers = sorted(sets["LAYERS"])
    storage_techs = sorted(sets['STORAGE_TECH'])
    storage_techs_mod = list(itertools.chain.from_iterable([[f"{tech}_Pin", f"{tech}_Pout"] for tech in storage_techs]))
    techs = sorted(list(set(sets['TECHNOLOGIES']) - set(storage_techs)))
    resources = sorted(sets['RESOURCES'])

    tds_hs = list(product(sets['TYPICAL_DAYS'], sets['HOURS']))
    hs_tds = [(h, td) for (td, h) in tds_hs]
    # Parameters
    layers_in_out = parameters['layers_in_out'].set_index(['index0', 'index1']).squeeze()
    storage_eff_in = parameters['storage_eff_in'].set_index(['index0', 'index1']).squeeze()

    # Results
    f = simplify_df(results["F"]).squeeze()
    f_t = results['F_t'].set_index(['index0', 'index1', 'index2']).squeeze()
    storage_in = results['Storage_in'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()
    storage_out = results['Storage_out'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()
    end_uses = results['End_uses'].set_index(['index0', 'index1', 'index2']).squeeze()

    # Save 1 file per layer
    for lay in layers:

        layers_df = pd.DataFrame(index=pd.MultiIndex.from_tuples(tds_hs, names=['Td', 'Time']),
                                 columns=resources + techs + storage_techs_mod + ["END_USE"],
                                 dtype=float)

        for res in resources:
            if layers_in_out[res, lay] == 0:
                continue  # incompatible
            layers_df.loc[tds_hs, res] = layers_in_out[res, lay] * f_t.loc[res].loc[hs_tds].values

        for tech in techs:
            # Incompatible or No technology installed
            if layers_in_out[tech, lay] == 0 or f[tech] == 0:
                continue  # incompatible
            layers_df.loc[tds_hs, tech] = layers_in_out[tech, lay] * f_t.loc[tech].loc[hs_tds].values

        for tech in storage_techs:
            # Incompatible or No storage installed
            if storage_eff_in[tech, lay] == 0 or f[tech] == 0:
                continue  # incompatible
            layers_df.loc[tds_hs, f"{tech}_Pin"] = -storage_in.loc[tech, lay].loc[hs_tds].values
            layers_df.loc[tds_hs, f"{tech}_Pout"] = storage_out.loc[tech, lay].loc[hs_tds].values

        layers_df.loc[tds_hs, 'END_USE'] = -end_uses.loc[lay].loc[hs_tds].values

        layers_df.round(6).to_csv(f"{output_dir}layer_{lay}.csv")


def save_energy_stored(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                       sets: Dict, output_dir: str) -> None:

    # TODO: also not the same result for TS_DEC_HP_ELEC and BEV_BATT but seems correct in the python version as it
    #  contains the same values as in Storage_level.csv (error in this file?)

    # Sets
    layers = sets['LAYERS']
    storage_techs = sorted(sets['STORAGE_TECH'])
    storage_techs_mod = list(itertools.chain.from_iterable([[f"{tech}_Pin", f"{tech}_Pout"] for tech in storage_techs]))
    times = time_to_pandas(sets)

    # Parameters
    storage_eff_in = parameters['storage_eff_in'].set_index(['index0', 'index1']).squeeze()
    storage_eff_out = parameters['storage_eff_out'].set_index(['index0', 'index1']).squeeze()

    # Results
    f = simplify_df(results["F"]).squeeze()
    storage_level = results['Storage_level'].set_index(['index0', 'index1']).squeeze()
    storage_in = results['Storage_in'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()
    storage_out = results['Storage_out'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()

    energy_stored = pd.DataFrame(index=times.index, columns=storage_techs+storage_techs_mod, dtype=float)
    for tech in storage_techs:

        if f[tech] == 0:
            continue
        energy_stored.loc[times.index, tech] = storage_level.loc[tech].loc[times.index]
        active_layers = [lay for lay in layers if storage_eff_in.loc[tech, lay] > 0]
        energy_stored.loc[times.index, f"{tech}_Pin"] = 0
        energy_stored.loc[times.index, f"{tech}_Pout"] = 0
        for lay in active_layers:
            energy_stored.loc[times.index, f"{tech}_Pin"] -= \
                (storage_in.loc[tech, lay].loc[times] * storage_eff_in.loc[tech, lay]).values
            energy_stored.loc[times.index, f"{tech}_Pout"] -= \
                (storage_out.loc[tech, lay].loc[times] / storage_eff_out.loc[tech, lay]).values

    energy_stored.round(6).to_csv(f"{output_dir}energy_stored.csv")


def save_results(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                 sets: Dict, output_dir: str) -> None:
    """
    Generate output files based on ESTD STEP 2 results and inputs

    Parameters
    ----------
    results: Dict[str, pd.DataFrame]
        Dictionary containing for each variable of the problem, the result of the optimization as a DataFrame
    parameters: Dict[str, pd.DataFrame]
        Dictionary containing for each parameter of the problem, the corresponding DataFrame
    sets: Dict
        Dictionary containing all the sets and subsets defined in the problem
    output_dir: str
        Path to the directory where output files ought to be saved
    """

    logging.info('Saving breakdowns')
    save_breakdowns(results, parameters, sets, output_dir)
    logging.info('Saving year balance')
    save_year_balance(results, parameters, sets, output_dir)
    # logging.info('Saving assets')
    # save_assets(results, parameters, sets, output_dir)
    if 0:

        logging.info('Saving technology-resource matrices')
        save_tech_res_matrices(results, parameters, sets, output_dir)
        logging.info('Saving losses')
        save_losses(results, parameters, sets, output_dir)
        logging.info('Saving layers')
        save_layers(results, parameters, sets, f"{output_dir}hourly_data/")
        logging.info('Saving energy stored')
        save_energy_stored(results, parameters, sets, f"{output_dir}hourly_data/")


def extract_results_step2(case_study_dir: str) -> None:
    """
    Extract results.

    :param case_study_dir: path to the case study directory.
    """

    # Load results
    with open(f"{case_study_dir}/output/results.pickle", 'rb') as handle:
        results = pickle.load(handle)

    with open(f"{case_study_dir}/output/parameters.pickle", 'rb') as handle:
        parameters = pickle.load(handle)

    with open(f"{case_study_dir}/output/sets.pickle", 'rb') as handle:
        sets = pickle.load(handle)

    logging.info("Saving results")
    save_results(results, parameters, sets, f"{case_study_dir}/output/")

    logging.info("Creating Sankey diagram input file")
    # generate_sankey_file(results, parameters, sets, f"{case_study_dir}/output/sankey/")

    logging.info('End of run')


if __name__ == '__main__':
    output_dir_ = "/home/duboisa1/Global_Grid/code/EnergyScope_multi_criteria/case_studies/gwp_constraint_35000/"
    run_name_ = "locals"
    print(output_dir_, run_name_)

    # extract_results_step2(f"{output_dir_}cost")
    # extract_results_step2(f"{output_dir_}einv")
    extract_results_step2(f"{output_dir_}gwp")

    epsilons = [0.05, 0.07]  # [0.0025, 0.005, 0.01, 0.025, 0.05, 0.075]
    for epsilon in epsilons:
        extract_results_step2(f"{output_dir_}cost_epsilon_{epsilon}")

    epsilon_tuples = [(0.01, 0.01), (0.02, 0.02)]
    epsilons = [0.0025, 0.005, 0.01, 0.025, 0.05, 0.075]
    for epsilon in epsilons:
        for epsilon_cost, epsilon_einv in epsilon_tuples:
            extract_results_step2(f"{output_dir_}{run_name_}_{epsilon_cost}_{epsilon_einv}_{epsilon}")
