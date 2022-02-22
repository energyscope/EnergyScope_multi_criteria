# -*- coding: utf-8 -*-
"""
Created on Jan 18 2022

Contains functions to generate sankey file from an ESTD STEP 2 run in python

@author: Antoine Dubois
"""
from typing import Dict

import pandas as pd

from energyscope.step2_output_generator import simplify_df, time_to_pandas


def add_ft_single(sankey_df: pd.DataFrame, index: int, times: pd.Series,
                  f_t: pd.Series, layers_in_out: pd.Series) -> [pd.DataFrame, int]:

    # TODO: even better would be to save it to a file
    sankey_dict = {
        "AMMONIA": [["Imp. Ammonia", "Ammonia", 1, "AMMONIA", "Ammonia", "#000ECD", "TWh"]],
        "AMMONIA_RE": [["Imp. RE Ammonia", "Ammonia", 1, "AMMONIA", "Ammonia", "#000ECD", "TWh"]],
        "HABER_BOSCH": [
            ["H2", "Haber-Bosch", -1, "H2", "H2", "#FF00FF", "TWh"],
            ["Elec", "Haber-Bosch", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            ["Haber-Bosch", "DHN", 1, "HEAT_LOW_T_DHN", "DHN", "#FA8072", "TWh"],
            ["Haber-Bosch", "Ammonia", 1, "AMMONIA", "Ammonia", "#000ECD", "TWh"]],
        "CCGT_AMMONIA": [["Ammonia", "Elec", -1, "AMMONIA", "Ammonia", "#000ECD", "TWh"]],
        "AMMONIA_TO_H2": [["Ammonia", "Elec", -1, "AMMONIA", "H2", "#FF00FF", "TWh"]],
        "METHANOL": [["Imp. Methanol", "Methanol", 1, "METHANOL", "Methanol", "#CC0066", "TWh"]],
        "METHANOL_RE": [["Imp. RE Methanol", "Methanol", 1, "METHANOL", "Methanol", "#CC0066", "TWh"]],
        "METHANE_TO_METHANOL": [
            ["Gas", "Methane-to-Methanol", -1, "GAS", "Gas", "#FFD700", "TWh"],
            ["Methane-to-Methanol", "Methanol", 1, "METHANOL", "Methanol", "#CC0066", "TWh"]],
        "BIOMASS_TO_METHANOL": [
            ["Wood", "Gasifi. to Methanol", -1, "WOOD", "Wood", "#CD853F", "TWh"],
            ["Gasifi. to Methanol", "Elec", 1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            ["Gasifi. to Methanol", "DHN", 1, "HEAT_LOW_T_DHN", "DHN", "#FA8072", "TWh"],
            ["Gasifi. to Methanol", "Methanol", 1, "METHANOL", "Methanol", "#CC0066", "TWh"]],
        # FIXME: error ? wood and h2 ?
        "SYN_METHANOLATION": [
            ["H2", "Methanolation", -1, "WOOD", "H2", "#FF00FF", "TWh"],
            ["Elec", "Methanolation", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            ["Methanolation", "DHN", 1, "HEAT_LOW_T_DHN", "DHN", "#FA8072", "TWh"],
            ["Methanolation", "Methanol", 1, "METHANOL", "Methanol", "#CC0066", "TWh"],
            ["H2", "Biofuels Prod", -1, "H2", "H2", "#FF00FF", "TWh"]],
        "CAR_METHANOL": [["Methanol", "Mob priv", -1, "METHANOL", "Methanol", "#CC0066", "TWh"]],
        # FIXME: will generate two lines with exactly the same entries except value
        "BOAT_FREIGHT_METHANOL": [["Methanol", "Freight", -1, "METHANOL", "Methanol", "#CC0066", "TWh"]],
        "TRUCK_METHANOL": [["Methanol", "Freight", -1, "METHANOL", "Methanol", "#CC0066", "TWh"]],
        "OIL_TO_HVC": [
            ["Oil", "NSC", -1, "LFO", "Naphtha", "#8B008B", "TWh"],
            ["Elec", "NSC", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            ["HT ?", "NSC", -1, "HEAT_HIGH_T", "Heat HT", "#DC143C", "TWh"],
            ["NSC", "HVC", 1, "HVC", "HVC", "#00FFFF", "TWh"]],
        "GAS_TO_HVC": [
            ["Gas", "OCM", -1, "GAS", "Gas", "#FFD700", "TWh"],
            ["Elec", "OCM", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            ["OCM", "HVC", 1, "HVC", "HVC", "#00FFFF", "TWh"]],
        "BIOMASS_TO_HVC": [
            ["Wood", "Gasifi. to HVC", -1, "WOOD", "Wood", "#CD853F", "TWh"],
            ["Elec", "Gasifi. to HVC", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            ["HT ?", "Gasifi. to HVC", -1, "HEAT_HIGH_T", "Heat HT", "#DC143C", "TWh"],
            ["Gasifi. to HVC", "HVC", 1, "HVC", "HVC", "#00FFFF", "TWh"]],
        "METHANOL_TO_HVC": [
            ["Methanol", "MTO", -1, "METHANOL", "Methanol", "#CC0066", "TWh"],
            ["HT ?", "MTO", -1, "HEAT_HIGH_T", "Heat HT", "#DC143C", "TWh"],
            ["MTO", "HVC", 1, "HVC", "HVC", "#00FFFF", "TWh"]],
        "GASOLINE": [["Imp. Gasoline", "Gasoline", 1, "GASOLINE", "Gasoline", "#808080", "TWh"]],
        "BIOETHANOL": [["Imp. Bio-ethanol", "Gasoline", 1, "GASOLINE", "Gasoline", "#808080", "TWh"]],
        "DIESEL": [["Imp. Diesel", "Diesel", 1, "DIESEL", "Diesel", "#D3D3D3", "TWh"]],
        "BIODIESEL": [["Imp. Bio-diesel", "Diesel", 1, "DIESEL", "Diesel", "#D3D3D3", "TWh"]],
        "CAR_DIESEL": [["Diesel", "Mob priv", -1, "DIESEL", "Diesel", "#D3D3D3", "TWh"]],
        "CAR_NG": [["Gas", "Mob priv", -1, "GAS", "GAS", "#FFD700", "TWh"]],
        "BUS_COACH_CNG_STOICH": [["Gas", "Mob public", -1, "GAS", "GAS", "#FFD700", "TWh"]],
        "SMR": [["Gas", "H2 prod", -1, "GAS", "GAS", "#FFD700", "TWh"]],
        "CCGT": [["Gas", "Elec", -1, "GAS", "GAS", "#FFD700", "TWh"]],
        "DEC_THHP_GAS": [["Gas", "HPs", -1, "GAS", "GAS", "#FFD700", "TWh"]],
        "ELECTRICITY": [["Electricity", "Elec", 1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"]],
        "NUCLEAR": [["Uranium", "Elec", -1, "URANIUM", "Nuclear", "#FFC0CB", "TWh"]],
        "HYDRO_RIVER": [["Hydro River", "Elec", 1, "ELECTRICITY", "Hydro River", "#0000FF", "TWh"]],
        "IND_BOILER_COAL": [["Coal", "Boilers", -1, "COAL", "Coal", "#A0522D", "TWh"]],
        "GEOTHERMAL": [["Geothermal", "Elec", 1, "ELECTRICITY", "Geothermal", "#FF0000", "TWh"]],
        "DHN_DEEP_GEO": [["Geothermal", "DHN", 1, "HEAT_LOW_T_DHN", "Geothermal", "#FF0000", "TWh"]],
        "IND_BOILER_WASTE": [["Waste", "Boilers", -1, "WASTE", "Waste", "#808000", "TWh"]],
        "LFO": [["Imp. Oil", "Oil", 1, "LFO", "Oil", "#8B008B", "TWh"]],
        "DEC_COGEN_OIL": [["Oil", "CHP", -1, "LFO", "Oil", "#8B008B", "TWh"]],
        "H2_BIOMASS": [["Wood", "H2 prod", -1, "WOOD", "Wood", "#CD853F", "TWh"]],
        "GASIFICATION_SNG": [
            ["Wood", "Gasifi.", -1, "WOOD", "Wood", "#CD853F", "TWh"],
            ["Gasifi.", "Gas Prod", 1, "GAS", "GAS", "#FFD700", "TWh"],
            ["Gasifi.", "DHN", 1, "HEAT_LOW_T_DHN", "Heat LT", "#FA8072", "TWh"],
            ["Gasifi.", "Elec", 1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"]],
        "BIO_HYDROLYSIS": [["Biomethanation", "Elec", 1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"]],
        "ELEC_EXPORT": [["Elec", "Curt.", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"]],
        "H2_ELECTROLYSIS": [
            ["Elec", "Electrolyser", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            ["HT ?", "Electrolyser", -1, "HEAT_HIGH_T", "Heat HT", "#DC143C", "TWh"],
            ["Electrolyser", "H2 prod", 1, "H2", "Electricity", "#00BFFF", "TWh"],
            ["Electrolyser", "DHN", 1, "HEAT_LOW_T_DHN", "Heat LT", "#FA8072", "TWh"]],
        "DEC_ADVCOGEN_H2": [["H2", "CHP", -1, "H2", "H2", "#FF00FF", "TWh"]],
        "CAR_FUEL_CELL": [["H2", "Mob priv", -1, "H2", "H2", "#FF00FF", "TWh"]],
        "BUS_COACH_FC_HYBRIDH2": [["H2", "Mob public", -1, "H2", "H2", "#FF00FF", "TWh"]],
        "TRUCK_FUEL_CELL": [["H2", "Freight", -1, "H2", "H2", "#FF00FF", "TWh"]],
        "SYN_METHANATION": [["H2", "Gas Prod", -1, "H2", "H2", "#FF00FF", "TWh"]],
        "DHN_HP_ELEC": [["HPs", "DHN", 1, "HEAT_LOW_T_DHN", "Heat LT", "#FA8072", "TWh"]],
        "PYROLYSIS_TO_LFO": [
            ["Wood", "Pyrolysis", -1, "WOOD", "Wood", "#CD853F", "TWh"],
            ["Pyrolysis", "Elec", 1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            # FIXME: Was in sankey.run but entry ('PYROLYSIS_TO_LFO', 'OIL') does not exist in layers_in_out
            # ["Pyrolysis", "Oil", 1, "OIL", "Oil", "#8B008B", "TWh"]
            ],
        "PYROLYSIS_TO_FUELS": [
            ["Wood", "Pyrolysis", -1, "WOOD", "Wood", "#CD853F", "TWh"],
            ["Pyrolysis", "Elec", 1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
            ["Pyrolysis", "Elec", 1, "DIESEL", "Diesel", "#D3D3D3", "TWh"],
            ["Pyrolysis", "Oil", 1, "GASOLINE", "Diesel", "#808080", "TWh"]],
    }

    for main_key, items in sankey_dict.items():
        if f_t[main_key][times].sum() > 10:
            for sub_items in items:
                source, target, sign, key1, layer_id, layer_color, layer_unit = sub_items
                real_value = (sign * layers_in_out[main_key, key1] * f_t[main_key][times]).sum() / 1000.0
                sankey_df.loc[index] = [source, target, round(real_value, 2), layer_id, layer_color, layer_unit]
                index += 1

    return sankey_df, index


def add_ft_multi(sankey_df: pd.DataFrame, index: int, times: pd.Series,
                 f_t: pd.Series, layers_in_out: pd.Series) -> [pd.DataFrame, int]:

    sankey_dict = {
        0: [["BUS_COACH_DIESEL", "BUS_COACH_HYDIESEL"], "Diesel", "Mob public", -1, "DIESEL", "Diesel", "#D3D3D3", "TWh"],
        1: [["TRUCK_DIESEL", "BOAT_FREIGHT_DIESEL"], "Diesel", "Freight", -1, "DIESEL", "Diesel", "#D3D3D3", "TWh"],
        2: [["IND_COGEN_GAS", "DHN_COGEN_GAS", "DEC_COGEN_GAS", "DEC_ADVCOGEN_GAS"], "Gas", "CHP", -1, "GAS", "GAS", "#FFD700", "TWh"],
        3: [["IND_BOILER_GAS", "DHN_BOILER_GAS", "DEC_BOILER_GAS"], "Gas", "Boilers", -1, "GAS", "GAS", "#FFD700", "TWh"],
        4: [["WIND_ONSHORE", "WIND_OFFSHORE"], "Wind", "Elec", 1, "ELECTRICITY", "Wind", "#27AE34", "TWh"],
        5: [["COAL_US", "COAL_IGCC"], "Coal", "Elec", -1, "COAL", "Coal", "#A0522D", "TWh"],
        6: [["IND_COGEN_WASTE", "DHN_COGEN_WASTE"], "Waste", "CHP", -1, "WASTE", "Waste", "#808000", "TWh"],
        7: [["IND_BOILER_OIL", "DHN_BOILER_OIL", "DEC_BOILER_OIL"], "Oil", "Boilers", -1, "LFO", "Oil", "#8B008B", "TWh"],
        8: [["IND_COGEN_WOOD", "DHN_COGEN_WOOD"], "Wood", "CHP", -1, "WOOD", "Wood", "#CD853F", "TWh"],
        9: [["IND_BOILER_WOOD", "DHN_BOILER_WOOD", "DEC_BOILER_WOOD"], "Wood", "Boilers", -1, "WOOD", "Wood", "#CD853F", "TWh"],
        10: [["DHN_COGEN_WET_BIOMASS", "DHN_COGEN_BIO_HYDROLYSIS"], "Wet biomass", "CHP", -1, "WET_BIOMASS", "Wood", "#CD853F", "TWh"],
        11: [["BIOMETHANATION", "BIO_HYDROLYSIS"], "Wet biomass", "Biomethanation", -1, "WET_BIOMASS", "Wood", "#CD853F", "TWh"],
        12: [["BIOMETHANATION", "BIO_HYDROLYSIS"], "Biomethanation", "Gas Prod", 1, "GAS", "GAS", "#FFD700", "TWh"],
        13: [["CAR_PHEV", "CAR_BEV"], "Elec", "Mob priv", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
        14: [["TRAIN_PUB", "TRAMWAY_TROLLEY"], "Elec", "Mob public", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
        15: [["TRAIN_FREIGHT", "TRUCK_ELEC"], "Elec", "Freight", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
        16: [["DHN_HP_ELEC", "DEC_HP_ELEC"], "Elec", "HPs", -1, "ELECTRICITY", "Electricity", "#00BFFF", "TWh"],
        17: [["BOAT_FREIGHT_NG", "TRUCK_NG"], "Gas", "Freight", -1, "GAS", "GAS", "#FFD700", "TWh"]
    }

    for _, items in sankey_dict.items():
        main_keys, source, target, sign, key2, layer_id, layer_color, layer_unit = items
        if sum([f_t[main_key][times].sum() for main_key in main_keys]) > 10:
            real_value = sum([(sign * layers_in_out[key1, key2] * f_t[key1][times]).sum() / 1000.0
                              for key1 in main_keys])
            sankey_df.loc[index] = [source, target, round(real_value, 2), layer_id, layer_color, layer_unit]
            index += 1

    return sankey_df, index


def add_end_uses(sankey_df: pd.DataFrame, index: int, times: pd.Series, end_uses: pd.Series) -> [pd.DataFrame, int]:

    sankey_dict = {
        0: ["AMMONIA", "Ammonia", "Non-energy demand", "Ammonia", "#000ECD", "TWh"],
        1: ["METHANOL", "Methanol", "Non-energy demand", "Methanol", "#CC0066", "TWh"],
        2: ["HVC", "HVC", "Non-energy demand", "HVC", "#00FFFF", "TWh"],
    }
    for _, items in sankey_dict.items():
        key, source, target, layer_id, layer_color, layer_unit = items
        if end_uses[key][times].sum() > 10:
            real_value = end_uses[key][times].sum() / 1000.0
            sankey_df.loc[index] = [source, target, round(real_value, 2), layer_id, layer_color, layer_unit]
            index += 1

    return sankey_df, index


def add_network_losses(sankey_df: pd.DataFrame, index: int, times: pd.Series,
                       network_losses: pd.Series) -> [pd.DataFrame, int]:

    sankey_dict = {
        0: ["ELECTRICITY", "Elec", "Exp & Loss", "Electricity", "#00BFFF", "TWh"],
        1: ["HEAT_LOW_T_DHN", "DHN", "Loss DHN", "Heat LT", "#FA8072", "TWh"],
    }
    for _, items in sankey_dict.items():
        key, source, target, layer_id, layer_color, layer_unit = items
        if network_losses[key][times].sum() > 10:
            real_value = network_losses[key][times].sum() / 1000.0
            sankey_df.loc[index] = [source, target, round(real_value, 2), layer_id, layer_color, layer_unit]
            index += 1

    return sankey_df, index


def add_ft_top(sankey_df: pd.DataFrame, index: int, times: pd.Series,
               f_t: pd.Series, t_op: pd.Series,) -> [pd.DataFrame, int]:

    sankey_dict = {
        0: ["GAS", "Imp. NG", "Gas", "Gas", "#FFD700", "TWh"],
        1: ["GAS_RE", "Imp. SNG", "Gas", "Gas", "#FFD700", "TWh"],
        2: ["H2", "Imp. H2", "H2", "H2", "#FF00FF", "TWh"],
        3: ["H2_RE", "Imp. H2_RE", "H2_RE", "H2", "#FF00FF", "TWh"],
    }
    for _, items in sankey_dict.items():
        key, source, target, layer_id, layer_color, layer_unit = items
        real_value = (t_op[times] * f_t[key][times]).sum()
        if real_value > 10:
            sankey_df.loc[index] = [source, target, round(real_value/1000.0, 2), layer_id, layer_color, layer_unit]
            index += 1

    return sankey_df, index


def add_f(sankey_df: pd.DataFrame, index: int, times: pd.Series, f: pd.Series, f_t: pd.Series,
          layers_in_out: pd.Series, storage_in: pd.Series, storage_out: pd.Series,
          storage_eff_out: pd.Series,) -> [pd.DataFrame, int]:

    # GAS
    layer_id = "GAS"
    layer_color = '#FFD700'
    layer_unit = 'TWh'
    key1, key2 = 'GAS_STORAGE', 'GAS'
    keys = ["GASIFICATION_SNG", "BIOMETHANATION", "BIO_HYDROLYSIS", "SYN_METHANATION"]
    if f['GAS_STORAGE'] > 0.001:
        real_value = storage_in[key1, key2][times].sum()/1000.0
        sankey_df.loc[index] = ['Gas Prod', 'SNG sto.', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1
        real_value = (storage_out[key1, key2][times]*storage_eff_out[key1, key2]).sum()/1000.0
        sankey_df.loc[index] = ['SNG sto.', 'Gas', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1
    # Done in both cases (> and <= 0.001)
    real_value = sum([layers_in_out[key, key2]*f_t[key][times] for key in keys])
    real_value = (real_value - storage_in[key1, key2][times]).sum()/1000.0
    sankey_df.loc[index] = ['Gas Prod', 'Gas', round(real_value, 2), layer_id, layer_color, layer_unit]
    index += 1

    # H2
    layer_id = "H2"
    layer_color = '#FFD700'
    layer_unit = 'TWh'
    key1, key2 = 'H2_STORAGE', 'H2'
    keys = ["SMR", "H2_BIOMASS", "H2_ELECTROLYSIS"]
    if f['H2_STORAGE'] > 0.001:
        real_value = storage_in[key1, key2][times].sum()/1000.0
        sankey_df.loc[index] = ['H2 prod', 'H2 sto.', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1
        real_value = (storage_out[key1, key2][times]*storage_eff_out[key1, key2]).sum()/1000.0
        sankey_df.loc[index] = ['H2 sto.', 'H2', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1
        real_value = sum([layers_in_out[key, key2]*f_t[key][times] for key in keys])
        real_value = (real_value - storage_in[key1, key2][times]).sum()/1000.0
        sankey_df.loc[index] = ['H2 Prod', 'H2', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1
    elif sum([f_t[key][times].sum() for key in keys]) > 10:
        real_value = sum([(layers_in_out[key, key2] * f_t[key][times]).sum() for key in keys]) / 1000.0
        sankey_df.loc[index] = ['H2 Prod', 'H2', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    return sankey_df, index


def add_solar(sankey_df: pd.DataFrame, index: int, times: pd.Series, sets: Dict,
              c_p_t: pd.Series, f: pd.Series, f_t: pd.Series, f_t_solar: pd.Series,
              layers_in_out: pd.Series, storage_in: pd.Series, storage_out: pd.Series) -> [pd.DataFrame, int]:

    layer_id, layer_color, layer_unit = "Solar", "#FFFF00", "TWh"
    if f_t['PV'][times].sum() > 10:
        real_value = (layers_in_out["PV", "ELECTRICITY"] * f["PV"] * c_p_t["PV"][times]).sum()/1000.0
        sankey_df.loc[index] = ['Solar', 'Elec', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    if f_t['DEC_SOLAR'][times].sum() > 10:
        real_value_1 = 0
        real_value_2 = 0
        for tech in set(sets["TECHNOLOGIES_OF_END_USES_TYPE"]["HEAT_LOW_T_DECEN"]) - {'DEC_SOLAR'}:
            for ts in sets["TS_OF_DEC_TECH"][tech]:
                term1 = layers_in_out[tech, "HEAT_LOW_T_DECEN"] * f_t_solar[tech][times]
                term2 = (layers_in_out[tech, "HEAT_LOW_T_DECEN"] * (f_t[tech][times] + f_t_solar[tech][times]))\
                    .apply(lambda x: max(x, 1e-4))
                term3 = (storage_in[ts, "HEAT_LOW_T_DECEN"][times] - storage_out[ts, "HEAT_LOW_T_DECEN"][times])\
                    .apply(lambda x: max(x, 0))
                real_value_1 += (term1/term2 * term3).sum()
                real_value_1 += (term1 - (term1/term2 * term3)).sum()
        sankey_df.loc[index] = ['Solar', 'Dec. sto', round(real_value_1/1000., 2), layer_id, layer_color, layer_unit]
        index += 1
        sankey_df.loc[index] = ['Solar', 'Heat LT Dec', round(real_value_2/1000., 2), layer_id, layer_color, layer_unit]
        index += 1

    if f_t['DHN_SOLAR'][times].sum() > 10:
        real_value = (layers_in_out["DHN_SOLAR", "HEAT_LOW_T_DHN"] * f["DHN_SOLAR"] *
                      c_p_t["DHN_SOLAR"][times]).sum()/1000.0
        sankey_df.loc[index] = ['Solar', 'DHN', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    return sankey_df, index


def add_elec_uses(sankey_df: pd.DataFrame, index: int, times: pd.Series, sets: Dict,
                  c_p_t: pd.Series, f: pd.Series, f_t: pd.Series,
                  end_uses: pd.Series, network_losses: pd.Series,
                  storage_in: pd.Series, storage_out: pd.Series) -> [pd.DataFrame, int]:

    layer_id, layer_color, layer_unit = "Electricity", "#00BFFF", "TWh"
    if end_uses["ELECTRICITY"][times].sum() > 10:
        real_value = end_uses["ELECTRICITY"][times] - network_losses["ELECTRICITY"][times]
        real_value += sum([(storage_out[i, "ELECTRICITY"][times] - storage_in[i, "ELECTRICITY"][times]).apply(lambda x: max(x, 0))
                           for i in sets["STORAGE_OF_END_USES_TYPES"]["ELECTRICITY"]])
        sankey_df.loc[index] = ['Elec', 'Elec demand', round(real_value.sum()/1000., 2),
                                layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Solar", "#FFFF00", "TWh"
    real_value = (f["PV"]*c_p_t["PV"][times] - f_t["PV"][times]).sum()
    if real_value > 10:
        sankey_df.loc[index] = ['Solar', 'Curt.', round(real_value/1000., 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Wind", "#27AE34", "TWh"
    real_value = (f["WIND_ONSHORE"]*c_p_t["WIND_ONSHORE"][times] - f_t["WIND_ONSHORE"][times]
                  + f["WIND_OFFSHORE"]*c_p_t["WIND_OFFSHORE"][times] - f_t["WIND_OFFSHORE"][times]).sum()
    if real_value > 10:
        sankey_df.loc[index] = ['Wind', 'Curt.', round(real_value/1000., 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Electricity", "#00BFFF", "TWh"
    if sum([storage_in[sto, "ELECTRICITY"][times].sum() for sto in sets["STORAGE_OF_END_USES_TYPES"]["ELECTRICITY"]]) > 10:
        real_value = sum([(-storage_out[sto, "ELECTRICITY"][times]
                           + storage_in[sto, "ELECTRICITY"][times]).apply(lambda x: max(x, 0)).sum()
                          for sto in sets["STORAGE_OF_END_USES_TYPES"]["ELECTRICITY"]])/1000.
        sankey_df.loc[index] = ['Elec', 'Storage', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1
        real_value = sum([(storage_out[sto, "ELECTRICITY"][times]
                           - storage_in[sto, "ELECTRICITY"][times]).apply(lambda x: max(x, 0)).sum()
                          for sto in sets["STORAGE_OF_END_USES_TYPES"]["ELECTRICITY"]])/1000.
        sankey_df.loc[index] = ['Storage', 'Elec demand', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    return sankey_df, index


def add_elec_heat(sankey_df: pd.DataFrame, index: int, times: pd.Series,
                  f_t: pd.Series, f_t_solar: pd.Series, layers_in_out: pd.Series,
                  storage_in: pd.Series, storage_out: pd.Series,
                  storage_eff_in: pd.Series, storage_eff_out: pd.Series) -> [pd.DataFrame, int]:

    layer_id, layer_color, layer_unit = "Electricity", "#00BFFF", "TWh"
    if f_t["DEC_DIRECT_ELEC"][times].sum() > 10:
        cond2 = (storage_in["TS_DEC_DIRECT_ELEC", "HEAT_LOW_T_DECEN"][times] -
                 storage_out["TS_DEC_DIRECT_ELEC" , "HEAT_LOW_T_DECEN"][times]).apply(lambda x: max(x, 0)).sum()
        if cond2 > 10:
            term1 = layers_in_out["DEC_DIRECT_ELEC", "HEAT_LOW_T_DECEN"] * f_t["DEC_DIRECT_ELEC"][times]
            term2 = (layers_in_out["DEC_DIRECT_ELEC", "HEAT_LOW_T_DECEN"] * f_t["DEC_DIRECT_ELEC"][times]
                     + layers_in_out["DEC_DIRECT_ELEC", "HEAT_LOW_T_DECEN"] * f_t_solar["DEC_DIRECT_ELEC"][times]).apply(lambda x: max(x, 1e-4))
            term3 = (storage_in["TS_DEC_DIRECT_ELEC", "HEAT_LOW_T_DECEN"][times]
                     - storage_out["TS_DEC_DIRECT_ELEC", "HEAT_LOW_T_DECEN"][times]).apply(lambda x: max(x, 0))
            real_value_1 = (term1/term2*term3).sum()/1000.
            sankey_df.loc[index] = ['Elec', 'Dec. sto', round(real_value_1, 2), layer_id, layer_color, layer_unit]
            index += 1
            real_value_2 = (term1 - (term1/term2*term3)).sum()/1000.
            sankey_df.loc[index] = ['Elec', 'Heat LT Dec', round(real_value_2, 2), layer_id, layer_color, layer_unit]
            index += 1

    if f_t["IND_DIRECT_ELEC"][times].sum() > 10:

        real_value = f_t["IND_DIRECT_ELEC"][times]
        real_value -= (storage_eff_in["TS_HIGH_TEMP", "HEAT_HIGH_T"] * storage_in["TS_HIGH_TEMP", "HEAT_HIGH_T"][times]
                      - storage_out["TS_HIGH_TEMP", "HEAT_HIGH_T"][times]).apply(lambda x: max(x, 0))
        layer_id, layer_color, layer_unit = "Electricity", "#00BFFF", "TWh"
        sankey_df.loc[index] = ['Elec', 'Heat HT', round(real_value.sum() / 1000., 2), layer_id, layer_color, layer_unit]
        index += 1

        cond2 = (storage_in["TS_HIGH_TEMP", "HEAT_HIGH_T"][times] -
                 storage_out["TS_HIGH_TEMP", "HEAT_HIGH_T"][times]).apply(lambda x: max(x, 0)).sum()
        if cond2 > 10:
            real_value = (storage_eff_in["TS_HIGH_TEMP", "HEAT_HIGH_T"] * storage_in["TS_HIGH_TEMP", "HEAT_HIGH_T"][times]
                          - storage_out["TS_HIGH_TEMP", "HEAT_HIGH_T"][times]).apply(lambda x: max(x, 0)).sum()/1000.
            layer_id, layer_color, layer_unit = "Electricity", "#00BFFF", "TWh"
            sankey_df.loc[index] = ['Elec', 'HT sto', round(real_value, 2), layer_id, layer_color, layer_unit]
            index += 1
            real_value = (storage_eff_out["TS_HIGH_TEMP", "HEAT_HIGH_T"] * storage_out["TS_HIGH_TEMP", "HEAT_HIGH_T"][times]
                          - storage_in["TS_HIGH_TEMP", "HEAT_HIGH_T"][times]).apply(lambda x: max(x, 0)).sum()/1000.
            layer_id, layer_color, layer_unit = "Heat HT", "#DC143C", "TWh"
            sankey_df.loc[index] = ["HT sto", "Heat HT", round(real_value, 2), layer_id, layer_color, layer_unit]
            index += 1

    return sankey_df, index


def add_chp(sankey_df: pd.DataFrame, index: int, times: pd.Series, sets: Dict,
            f_t: pd.Series, f_t_solar: pd.Series, layers_in_out: pd.Series,
            storage_in: pd.Series, storage_out: pd.Series) -> [pd.DataFrame, int]:

    layer_id, layer_color, layer_unit = "Electricity", "#00BFFF", "TWh"
    if sum([f_t[tech][times].sum() for tech in sets['COGEN']]) > 10:
        real_value = sum([(layers_in_out[tech, "ELECTRICITY"] * f_t[tech][times]).sum() for tech in sets['COGEN']]) / 1000.
        sankey_df.loc[index] = ['CHP', 'Elec', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Heat LT", "#FA8072", "TWh"
    keys = ["DEC_COGEN_GAS", "DEC_COGEN_OIL", "DEC_ADVCOGEN_GAS", "DEC_ADVCOGEN_H2"]
    if sum([f_t[tech][times].sum() for tech in keys]) > 10:
        real_value_1 = 0
        real_value_2 = 0
        for tech in keys:
            for ts in sets['TS_OF_DEC_TECH'][tech]:
                term1 = layers_in_out[tech, "HEAT_LOW_T_DECEN"] * f_t[tech][times]
                term2 = (layers_in_out[tech, "HEAT_LOW_T_DECEN"] * f_t[tech][times]
                         + layers_in_out[tech, "HEAT_LOW_T_DECEN"] * f_t_solar[tech][times]).apply(lambda x: max(x, 1e-4))
                term3 = (storage_in[ts, "HEAT_LOW_T_DECEN"][times]
                         - storage_out[ts, "HEAT_LOW_T_DECEN"][times]).apply(lambda x: max(x, 0))
                real_value_1 += (term1 / term2 * term3).sum()/1000.
                real_value_2 += (term1 - (term1 / term2 * term3)).sum()/1000.
        sankey_df.loc[index] = ['CHP', 'Dec. sto', round(real_value_1, 2), layer_id, layer_color, layer_unit]
        index += 1
        sankey_df.loc[index] = ['CHP', 'Heat LT Dec', round(real_value_2, 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Heat LT", "#FA8072", "TWh"
    keys = ["DHN_COGEN_GAS", "DHN_COGEN_WOOD", "DHN_COGEN_WASTE", "DHN_COGEN_WET_BIOMASS", "DHN_COGEN_BIO_HYDROLYSIS"]
    if sum([f_t[tech][times].sum() for tech in keys]) > 10:
        real_value = sum([(layers_in_out[tech, "HEAT_LOW_T_DHN"] * f_t[tech][times]).sum() for tech in sets['COGEN']]) / 1000.
        sankey_df.loc[index] = ['CHP', 'DHN', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Heat HT", "#DC143C", "TWh"
    keys = ["IND_COGEN_GAS", "IND_COGEN_WOOD", "IND_COGEN_WASTE"]
    if sum([f_t[tech][times].sum() for tech in keys]) > 10:
        real_value = sum([(layers_in_out[tech, "HEAT_HIGH_T"] * f_t[tech][times]).sum() for tech in sets['COGEN']]) / 1000.
        sankey_df.loc[index] = ['CHP', 'Heat HT', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    return sankey_df, index


def add_hp(sankey_df: pd.DataFrame, index: int, times: pd.Series, sets: Dict,
           f_t: pd.Series, f_t_solar: pd.Series, layers_in_out: pd.Series,
           storage_in: pd.Series, storage_out: pd.Series) -> [pd.DataFrame, int]:

    layer_id, layer_color, layer_unit = "Heat LT", "#FA8072", "TWh"
    keys = ["DEC_HP_ELEC", "DEC_THHP_GAS"]
    if sum([f_t[tech][times].sum() for tech in keys]) > 10:

        real_value_1 = 0
        real_value_2 = 0

        cond2 = sum([(storage_in[ts, "HEAT_LOW_T_DECEN"][times] -
                     storage_out[ts, "HEAT_LOW_T_DECEN"][times]).apply(lambda x: max(x, 0)).sum()
                     for tech in keys for ts in sets['TS_OF_DEC_TECH'][tech]])

        for tech in keys:
            for ts in sets['TS_OF_DEC_TECH'][tech]:
                term1 = layers_in_out[tech, "HEAT_LOW_T_DECEN"] * f_t[tech][times]
                term2 = (layers_in_out[tech, "HEAT_LOW_T_DECEN"] * f_t[tech][times]
                         + layers_in_out[tech, "HEAT_LOW_T_DECEN"] * f_t_solar[tech][times]).apply(
                    lambda x: max(x, 1e-4))
                term3 = (storage_in[ts, "HEAT_LOW_T_DECEN"][times]
                         - storage_out[ts, "HEAT_LOW_T_DECEN"][times]).apply(lambda x: max(x, 0))
                real_value_1 += (term1 / term2 * term3).sum() / 1000.
                real_value_2 += (term1 - (term1 / term2 * term3)).sum() / 1000.
        if cond2 > 10:
            sankey_df.loc[index] = ['HPs', 'Dec. sto', round(real_value_1, 2), layer_id, layer_color, layer_unit]
            index += 1
        sankey_df.loc[index] = ['HPs', 'Heat LT Dec', round(real_value_2, 2), layer_id, layer_color, layer_unit]
        index += 1

    return sankey_df, index


def add_boiler(sankey_df: pd.DataFrame, index: int, times: pd.Series, sets: Dict,
               f_t: pd.Series, layers_in_out: pd.Series, storage_in: pd.Series, storage_out: pd.Series) -> [pd.DataFrame, int]:

    layer_id, layer_color, layer_unit = "Heat LT", "#FA8072", "TWh"
    keys = ["DEC_BOILER_GAS", "DEC_BOILER_WOOD", "DEC_BOILER_OIL"]
    if sum([f_t[tech][times].sum() for tech in keys]) > 10:
        real_value_1 = 0
        real_value_2 = 0
        for tech in keys:
            for ts in sets['TS_OF_DEC_TECH'][tech]:
                term2 = layers_in_out[tech, "HEAT_LOW_T_DECEN"] * f_t[tech][times]
                term1 = (storage_in[ts, "HEAT_LOW_T_DECEN"][times]
                         - storage_out[ts, "HEAT_LOW_T_DECEN"][times]).apply(lambda x: max(x, 0))
                real_value_1 += term1.sum()/1000.
                real_value_2 += (term2 - term1).sum()/1000.
        sankey_df.loc[index] = ['Boilers', 'Dec. sto', round(real_value_1, 2), layer_id, layer_color, layer_unit]
        index += 1
        sankey_df.loc[index] = ['Boilers', 'Heat LT Dec', round(real_value_2, 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Heat LT", "#FA8072", "TWh"
    keys = sets["STORAGE_OF_END_USES_TYPES"]["HEAT_LOW_T_DECEN"]
    real_value = sum([(storage_out[tech, "HEAT_LOW_T_DECEN"][times] - storage_in[tech, "HEAT_LOW_T_DECEN"][times])
                     .apply(lambda x: max(x, 0)).sum() for tech in keys])
    if real_value > 10:
        sankey_df.loc[index] = ['Dec. sto', 'Heat LT Dec', round(real_value/1000., 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Heat LT", "#FA8072", "TWh"
    keys = ["DHN_BOILER_GAS", "DHN_BOILER_WOOD", "DHN_BOILER_OIL"]
    if sum([f_t[tech][times].sum() for tech in keys]) > 10:
        real_value = sum([(layers_in_out[tech, "HEAT_LOW_T_DHN"] * f_t[tech][times]).sum() for tech in sets["BOILERS"]])/1000.
        sankey_df.loc[index] = ['Boilers', 'DHN', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Heat HT", "#DC143C", "TWh"
    keys = ["IND_BOILER_GAS", "IND_BOILER_WOOD", "IND_BOILER_OIL", "IND_BOILER_COAL", "IND_BOILER_WASTE"]
    if sum([f_t[tech][times].sum() for tech in keys]) > 10:
        real_value = sum([(layers_in_out[tech, "HEAT_HIGH_T"] * f_t[tech][times]).sum() for tech in sets["BOILERS"]])/1000.
        sankey_df.loc[index] = ['Boilers', 'Heat HT', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    return sankey_df, index


def add_dhn(sankey_df: pd.DataFrame, index: int, times: pd.Series, sets: Dict,
            f_t: pd.Series, layers_in_out: pd.Series, end_uses: pd.Series, network_losses: pd.Series,
            storage_in: pd.Series, storage_out: pd.Series) -> [pd.DataFrame, int]:

    layer_id, layer_color, layer_unit = "Heat LT", "#FA8072", "TWh"
    if end_uses["HEAT_LOW_T_DHN"][times].sum() > 10:
        term1 = sum([layers_in_out[tech, "HEAT_LOW_T_DHN"] * f_t[tech][times]
                     for tech in set(sets["TECHNOLOGIES"]) - set(sets["STORAGE_TECH"])])
        term2 = network_losses["HEAT_LOW_T_DHN"][times]
        term3 = sum([(storage_in[sto, "HEAT_LOW_T_DHN"][times]
                      - storage_out[sto, "HEAT_LOW_T_DHN"][times]).apply(lambda x: max(x, 0))
                     for sto in sets["STORAGE_OF_END_USES_TYPES"]["HEAT_LOW_T_DHN"]])
        real_value = (term1-term2-term3).sum()/1000.
        sankey_df.loc[index] = ['DHN', 'Heat LT DHN', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    layer_id, layer_color, layer_unit = "Heat LT", "#FA8072", "TWh"
    stos = sets["STORAGE_OF_END_USES_TYPES"]["HEAT_LOW_T_DHN"]
    real_value_1 = sum([(storage_in[sto, "HEAT_LOW_T_DHN"][times] - storage_out[sto, "HEAT_LOW_T_DHN"][times])
                        .apply(lambda x: max(x, 0)).sum() for sto in stos])
    if real_value_1 > 10:
        sankey_df.loc[index] = ['DHN', 'DHN Sto', round(real_value_1/1000., 2), layer_id, layer_color, layer_unit]
        index += 1
        real_value_2 = sum([(storage_out[sto, "HEAT_LOW_T_DHN"][times] - storage_in[sto, "HEAT_LOW_T_DHN"][times])
                            .apply(lambda x: max(x, 0)).sum() for sto in stos])
        sankey_df.loc[index] = ['DHN Sto', 'Heat LT DHN', round(real_value_2/1000., 2), layer_id, layer_color, layer_unit]
        index += 1

    return sankey_df, index


def add_gasoline(sankey_df: pd.DataFrame, index: int, times: pd.Series,
                 f_t: pd.Series, layers_in_out: pd.Series) -> [pd.DataFrame, int]:

    layer_id, layer_color, layer_unit = "Gasoline", "#808080", "TWh"
    techs = ["CAR_GASOLINE", "CAR_HEV", "CAR_PHEV"]
    if f_t["GASOLINE"][times].sum() > 10:
        real_value = sum([(layers_in_out[tech, "GASOLINE"] * f_t[tech][times]).sum() for tech in techs])
        sankey_df.loc[index] = ['Gasoline', 'Mob priv', round(real_value, 2), layer_id, layer_color, layer_unit]
        index += 1

    return sankey_df, index


def generate_sankey_file(results: Dict[str, pd.DataFrame], parameters: Dict[str, pd.DataFrame],
                         sets: Dict, output_dir: str) -> None:
    # Sets
    times = time_to_pandas(sets)

    # Parameters
    layers_in_out = parameters['layers_in_out'].set_index(['index0', 'index1']).squeeze()
    t_op = parameters['t_op'].set_index(['index0', 'index1']).squeeze()
    storage_eff_in = parameters['storage_eff_in'].set_index(['index0', 'index1']).squeeze()
    storage_eff_out = parameters['storage_eff_out'].set_index(['index0', 'index1']).squeeze()
    c_p_t = parameters['c_p_t'].set_index(['index0', 'index1', 'index2']).squeeze()

    # Results
    f = simplify_df(results["F"]).squeeze()
    f_t = results['F_t'].set_index(['index0', 'index1', 'index2']).squeeze()
    f_t_solar = results['F_t_solar'].set_index(['index0', 'index1', 'index2']).squeeze()
    end_uses = results['End_uses'].set_index(['index0', 'index1', 'index2']).squeeze()
    network_losses = results['Network_losses'].set_index(['index0', 'index1', 'index2']).squeeze()
    storage_in = results['Storage_in'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()
    storage_out = results['Storage_out'].set_index(['index0', 'index1', 'index2', 'index3']).squeeze()

    # Filling the dataframe
    sankey_df = pd.DataFrame(columns=["source", "target", "realValue", "layerID", "layerColor", "layerUnit"])
    index = 0

    sankey_df, index = add_ft_single(sankey_df, index, times, f_t, layers_in_out)
    sankey_df, index = add_ft_multi(sankey_df, index, times, f_t, layers_in_out)
    sankey_df, index = add_end_uses(sankey_df, index, times, end_uses)
    sankey_df, index = add_network_losses(sankey_df, index, times, network_losses)
    sankey_df, index = add_ft_top(sankey_df, index, times, f_t, t_op)
    sankey_df, index = add_f(sankey_df, index, times, f, f_t, layers_in_out,
                             storage_in, storage_out, storage_eff_out)
    sankey_df, index = add_gasoline(sankey_df, index, times, f_t, layers_in_out)
    sankey_df, index = add_solar(sankey_df, index, times, sets, c_p_t, f, f_t, f_t_solar,
                                 layers_in_out, storage_in, storage_out)
    sankey_df, index = add_elec_uses(sankey_df, index, times, sets, c_p_t, f, f_t,
                                     end_uses, network_losses, storage_in, storage_out)
    sankey_df, index = add_elec_heat(sankey_df, index, times, f_t, f_t_solar, layers_in_out,
                                     storage_in, storage_out, storage_eff_in, storage_eff_out)
    sankey_df, index = add_chp(sankey_df, index, times, sets, f_t, f_t_solar, layers_in_out,
                               storage_in, storage_out)
    sankey_df, index = add_hp(sankey_df, index, times, sets, f_t, f_t_solar, layers_in_out,
                              storage_in, storage_out)
    sankey_df, index = add_boiler(sankey_df, index, times, sets, f_t, layers_in_out, storage_in, storage_out)
    sankey_df, index = add_dhn(sankey_df, index, times, sets, f_t, layers_in_out, end_uses, network_losses,
                               storage_in, storage_out)

    sankey_df.set_index(['source', 'target']).sort_index().to_csv(f"{output_dir}input2sankey.csv")


# TODO: remove
if __name__ == '__main__':
    import json

    output_dir_ = "/home/duboisa1/Global_Grid/code/EnergyScope_multi_criteria/temp/output2/"

    sets_ = json.load(open(f"{output_dir_}sets/sets.json", "r"))

    parameters_names = ['layers_in_out', 't_op', 'storage_eff_out', 'storage_eff_in', 'c_p_t']
    parameters_ = {name: pd.read_csv(f"{output_dir_}parameters/{name}.csv", index_col=0) for name in parameters_names}

    results_name = ['F_t', 'End_uses', 'Network_losses', 'F', 'Storage_in', 'Storage_out', 'F_t_solar']
    results_ = {name: pd.read_csv(f"{output_dir_}results/{name}.csv", index_col=0) for name in results_name}

    generate_sankey_file(results_, parameters_, sets_, f"{output_dir_}sankey/")
