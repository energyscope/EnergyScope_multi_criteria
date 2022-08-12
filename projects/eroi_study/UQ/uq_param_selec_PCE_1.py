# -*- coding: utf-8 -*-
"""
This script provides the parameters and their uncertainty intervals to be used in the RHEIA python library.

At this stage we only consider uncertainty on:
- EUD;
- resources availability;
- resources einv_op: by default 25%;
- technologies einv_const: by default 25%;
- technologies f_max capacities;
- "other" parameters such as i_rate, etc.

For the uncertainty ranges, see [2] Appendix D, Table D.1. The ranges were determined [3] see Table 2.1.

Extensions need to be conducted by including uncertainty on:
- cost: c_op, c_maint, and c_inv;
- gwp: gwp_op and gwp_const;
- efficiencies;
- einv_const: inlude storage technologies;
- einv_op and einv_const: determine relevant uncertainty intervals;
- technologies capacity factors.

Note: this script generates the design_space and stochastic_space files required
 by the RHEIA python library to generate samples.
These samples are then used to run ES-TD to compute the corresponding EROI values.
Then, the RHEIA python library is used to perform PCE using these samples to compute the Sobol indexes.
For more information about the uncertainty quantification in ES-TD see:
[1] Rixhon, Xavier, et al. "The Role of Electrofuels under Uncertainties for the Belgian Energy Transition."
 Energies 14.13 (2021): 4027.
[2] Limpens, Gauthier. Generating energy transition pathways: application to Belgium.
 Diss. UCL-Université Catholique de Louvain, 2021. -> chapter 6 and appendix D.
[3] Moret, Stefano, et al. "Characterization of input uncertainties in strategic energy planning models."
 Applied energy 202 (2017): 597-617.
[4] Coppitters, Diederik. Robust design optimization of hybrid renewable energy systems.
 Diss. University of Plymouth, 2021.

@author: Jonathan Dumas
"""

# import yaml
import os
import json

import pandas as pd
import energyscope as es
# import numpy as np
# import matplotlib.pyplot as plt

from projects.eroi_study.utils import load_config


def eff_mature_standard_tech(df: pd.DataFrame):
    eff_NUCLEAR = -1 / df.loc['NUCLEAR']['URANIUM']
    eff_CCGT = -1 / df.loc['CCGT']['GAS']
    eff_CCGT_AMMONIA = -1 / df.loc['CCGT_AMMONIA']['AMMONIA']
    eff_IND_BOILER_GAS = -1 / df.loc['IND_BOILER_GAS']['GAS']
    eff_IND_BOILER_WOOD = -1 / df.loc['IND_BOILER_WOOD']['WOOD']
    eff_IND_BOILER_WASTE = -1 / df.loc['IND_BOILER_WASTE']['WASTE']
    eff_DHN_BOILER_GAS = -1 / df.loc['DHN_BOILER_GAS']['GAS']
    eff_DHN_BOILER_WOOD = -1 / df.loc['DHN_BOILER_WOOD']['WOOD']
    eff_DEC_BOILER_GAS = -1 / df.loc['DEC_BOILER_GAS']['GAS']
    eff_DEC_BOILER_WOOD = -1 / df.loc['DEC_BOILER_WOOD']['WOOD']
    tech_list = ['NUCLEAR', 'CCGT', 'CCGT_AMMONIA', 'IND_BOILER_GAS', 'IND_BOILER_WOOD', 'IND_BOILER_WASTE',
                 'DHN_BOILER_GAS', 'DHN_BOILER_WOOD', 'DEC_BOILER_GAS', 'DEC_BOILER_WOOD']
    eff_tech_list = [eff_NUCLEAR, eff_CCGT, eff_CCGT_AMMONIA, eff_IND_BOILER_GAS, eff_IND_BOILER_WOOD,
                     eff_IND_BOILER_WASTE, eff_DHN_BOILER_GAS, eff_DHN_BOILER_WOOD, eff_DEC_BOILER_GAS,
                     eff_DEC_BOILER_WOOD]
    return eff_tech_list, tech_list

    # # mature customized U[-20.6%, 20.6%]
    # eff_CAR_GASOLINE = -1/all_data['Layers_in_out'].loc['CAR_GASOLINE']['GASOLINE']
    # eff_TRUCK_DIESEL = -1/all_data['Layers_in_out'].loc['TRUCK_DIESEL']['DIESEL']
    # eff_IND_COGEN_GAS_gas = -1/all_data['Layers_in_out'].loc['IND_COGEN_GAS']['GAS']
    # eff_IND_COGEN_GAS_elec = 1/all_data['Layers_in_out'].loc['IND_COGEN_GAS']['ELECTRICITY']
    # eff_IND_COGEN_WOOD_gas = -1/all_data['Layers_in_out'].loc['IND_COGEN_WOOD']['WOOD']
    # eff_IND_COGEN_WOOD_elec = 1/all_data['Layers_in_out'].loc['IND_COGEN_WOOD']['ELECTRICITY']
    # eff_IND_COGEN_WASTE_gas = -1/all_data['Layers_in_out'].loc['IND_COGEN_WASTE']['WASTE']
    # eff_IND_COGEN_WASTE_elec = 1/all_data['Layers_in_out'].loc['IND_COGEN_WASTE']['ELECTRICITY']
    # eff_DHN_COGEN_GAS_gas = -1/all_data['Layers_in_out'].loc['DHN_COGEN_GAS']['GAS']
    # eff_DHN_COGEN_GAS_elec = 1/all_data['Layers_in_out'].loc['DHN_COGEN_GAS']['ELECTRICITY']
    # eff_DHN_COGEN_WOOD_gas = -1/all_data['Layers_in_out'].loc['DHN_COGEN_WOOD']['WOOD']
    # eff_DHN_COGEN_WOOD_elec = 1/all_data['Layers_in_out'].loc['DHN_COGEN_WOOD']['ELECTRICITY']
    # eff_DHN_COGEN_WASTE_gas = -1/all_data['Layers_in_out'].loc['DHN_COGEN_WASTE']['WASTE']
    # eff_DHN_COGEN_WASTE_elec = 1/all_data['Layers_in_out'].loc['DHN_COGEN_WASTE']['ELECTRICITY']
    # eff_DHN_COGEN_BIO_HYDROLYSIS_biomass = -1/all_data['Layers_in_out'].loc['DHN_COGEN_BIO_HYDROLYSIS']['WET_BIOMASS']
    # eff_DHN_COGEN_BIO_HYDROLYSIS_elec = 1/all_data['Layers_in_out'].loc['DHN_COGEN_BIO_HYDROLYSIS']['ELECTRICITY']
    # eff_DHN_HP_ELEC = -1/all_data['Layers_in_out'].loc['DHN_HP_ELEC']['ELECTRICITY']
    # eff_DEC_HP_ELEC = -1/all_data['Layers_in_out'].loc['DEC_HP_ELEC']['ELECTRICITY']
    # eff_DEC_COGEN_GAS_gas = -1/all_data['Layers_in_out'].loc['DEC_COGEN_GAS']['GAS']
    # eff_DEC_COGEN_GAS_elec = 1/all_data['Layers_in_out'].loc['DEC_COGEN_GAS']['ELECTRICITY']
    # eff_DEC_ADVCOGEN_GAS_gas = -1/all_data['Layers_in_out'].loc['DEC_ADVCOGEN_GAS']['GAS']
    # eff_DEC_ADVCOGEN_GAS_elec = 1/all_data['Layers_in_out'].loc['DEC_ADVCOGEN_GAS']['ELECTRICITY']
    # eff_DEC_ADVCOGEN_H2_H2 = -1/all_data['Layers_in_out'].loc['DEC_ADVCOGEN_H2']['H2']
    # eff_DEC_ADVCOGEN_H2_elec = 1/all_data['Layers_in_out'].loc['DEC_ADVCOGEN_H2']['ELECTRICITY']
    # eff_DEC_COGEN_OIL_lfo = -1/all_data['Layers_in_out'].loc['DEC_COGEN_OIL']['LFO']
    # eff_DEC_COGEN_OIL_elec = 1/all_data['Layers_in_out'].loc['DEC_COGEN_OIL']['ELECTRICITY']
    #
    # # new customized U[-28.7%, 28.7%]
    # eff_CAR_NG = -1/all_data['Layers_in_out'].loc['CAR_NG']['GAS']
    # eff_CAR_METHANOL = -1/all_data['Layers_in_out'].loc['CAR_METHANOL']['METHANOL']
    # eff_CAR_FUEL_CELL = -1/all_data['Layers_in_out'].loc['CAR_FUEL_CELL']['H2']
    # eff_CAR_BEV = -1/all_data['Layers_in_out'].loc['CAR_BEV']['ELECTRICITY']
    # eff_CAR_HEV = -1/all_data['Layers_in_out'].loc['CAR_HEV']['GASOLINE']
    # eff_CAR_PHEV_gasoline = -1/all_data['Layers_in_out'].loc['CAR_PHEV']['GASOLINE']
    # eff_CAR_PHEV_elec = -1/all_data['Layers_in_out'].loc['CAR_PHEV']['ELECTRICITY']
    # eff_TRUCK_NG = -1/all_data['Layers_in_out'].loc['TRUCK_NG']['GAS']
    # eff_TRUCK_METHANOL = -1/all_data['Layers_in_out'].loc['TRUCK_METHANOL']['METHANOL']
    # eff_TRUCK_FUEL_CELL = -1/all_data['Layers_in_out'].loc['TRUCK_FUEL_CELL']['H2']
    # eff_TRUCK_ELEC = -1/all_data['Layers_in_out'].loc['TRUCK_ELEC']['ELECTRICITY']
    # eff_H2_ELECTROLYSIS_elec = -1/all_data['Layers_in_out'].loc['H2_ELECTROLYSIS']['ELECTRICITY']
    # eff_H2_ELECTROLYSIS_heat_high_T = -1/all_data['Layers_in_out'].loc['H2_ELECTROLYSIS']['HEAT_HIGH_T']
    # eff_H2_ELECTROLYSIS_heat_low_T = 1/all_data['Layers_in_out'].loc['H2_ELECTROLYSIS']['HEAT_LOW_T_DHN']


def res_avail_params(data: pd.DataFrame):
    """
    Define the uncertainty parameters related to availability or resources.
    U[-32.1%, 32.1%]: wood, wet biomass, and waste.
    """
    l = ['WOOD', 'WET_BIOMASS', 'WASTE']
    df_design = pd.DataFrame(data=['par'] * len(l), index=['avail-' + i for i in l], columns=['type'])
    df_design['val'] = 0.0
    for res in l:
        df_design.at['avail-' + res, 'val'] = data.at[res, 'avail']

    df_stochastic = df_design.copy()
    df_stochastic['type'] = 'absolute Uniform'
    df_stochastic['val'] = df_stochastic['val'] * 0.321
    return df_design, df_stochastic


def res_einv_op_params(data: pd.DataFrame):
    """
    Define the uncertainty parameters related to einv_op of resources.
    FIXME: set by default to U[-25%, 25%] -> a study similar to the one conducted
        in the Ph.D. thesis of S. Moret must be conducted.
    """
    l = ['ELECTRICITY', 'GASOLINE', 'DIESEL', 'BIOETHANOL', 'BIODIESEL', 'LFO', 'GAS', 'GAS_RE', 'WOOD', 'WET_BIOMASS',
         'URANIUM', 'WASTE', 'H2', 'H2_RE', 'AMMONIA', 'METHANOL', 'AMMONIA_RE', 'METHANOL_RE']
    df_design = pd.DataFrame(data=['par'] * len(l), index=['einv_op-' + i for i in l], columns=['type'])
    df_design['val'] = 0.0
    for res in l:
        df_design.at['einv_op-' + res, 'val'] = data.at[res, 'einv_op']

    df_stochastic = df_design.copy()
    df_stochastic['type'] = 'absolute Uniform'
    df_stochastic['val'] = df_stochastic['val'] * 0.25
    return df_design, df_stochastic


def res_einv_constr_params(data: pd.DataFrame):
    """
    Define the uncertainty parameters related to einv_constr of technologies.
    FIXME: set by default U[-25%, 25%] -> a study similar to the one conducted
        in the Ph.D. thesis of S. Moret must be conducted.
    Note: the storage and CCS technologies are not taken into account.
    """
    l = ['AMMONIA_TO_H2', 'BATT_LI', 'BIOMASS_TO_HVC', 'BIOMASS_TO_METHANOL',
         'BIOMETHANATION', 'BIO_HYDROLYSIS', 'BOAT_FREIGHT_DIESEL', 'BOAT_FREIGHT_METHANOL', 'BOAT_FREIGHT_NG',
         'BUS_COACH_CNG_STOICH', 'BUS_COACH_DIESEL', 'BUS_COACH_FC_HYBRIDH2', 'BUS_COACH_HYDIESEL', 'CAR_BEV',
         'CAR_DIESEL', 'CAR_FUEL_CELL', 'CAR_GASOLINE', 'CAR_HEV', 'CAR_METHANOL', 'CAR_NG', 'CAR_PHEV', 'CCGT',
         'CCGT_AMMONIA', 'DEC_ADVCOGEN_GAS', 'DEC_ADVCOGEN_H2', 'DEC_BOILER_GAS', 'DEC_BOILER_OIL', 'DEC_BOILER_WOOD',
         'DEC_COGEN_GAS', 'DEC_COGEN_OIL', 'DEC_DIRECT_ELEC', 'DEC_HP_ELEC', 'DEC_SOLAR', 'DEC_THHP_GAS',
         'DHN_BOILER_GAS', 'DHN_BOILER_OIL', 'DHN_BOILER_WOOD', 'DHN_COGEN_BIO_HYDROLYSIS', 'DHN_COGEN_GAS',
         'DHN_COGEN_WASTE', 'DHN_COGEN_WET_BIOMASS', 'DHN_COGEN_WOOD', 'DHN_DEEP_GEO', 'DHN_HP_ELEC', 'DHN_SOLAR',
         'GASIFICATION_SNG', 'GAS_TO_HVC', 'GEOTHERMAL', 'H2_BIOMASS',
         'H2_ELECTROLYSIS', 'HABER_BOSCH', 'HYDRO_RIVER', 'IND_BOILER_COAL', 'IND_BOILER_GAS',
         'IND_BOILER_OIL', 'IND_BOILER_WASTE', 'IND_BOILER_WOOD', 'IND_COGEN_GAS', 'IND_COGEN_WASTE', 'IND_COGEN_WOOD',
         'IND_DIRECT_ELEC', 'METHANE_TO_METHANOL', 'METHANOL_TO_HVC', 'NUCLEAR',
         'OIL_TO_HVC', 'PHS', 'PV', 'PYROLYSIS_TO_FUELS', 'PYROLYSIS_TO_LFO', 'SMR', 'SYN_METHANATION',
         'SYN_METHANOLATION', 'TRAIN_FREIGHT', 'TRAIN_PUB', 'TRAMWAY_TROLLEY', 'TRUCK_DIESEL', 'TRUCK_ELEC',
         'TRUCK_FUEL_CELL', 'TRUCK_METHANOL', 'TRUCK_NG', 'WIND_OFFSHORE', 'WIND_ONSHORE']

    df_design = pd.DataFrame(data=['par'] * len(l), index=['einv_constr-' + i for i in l], columns=['type'])
    df_design['val'] = 0.0
    for res in l:
        df_design.at['einv_constr-' + res, 'val'] = data.at[res, 'einv_constr']

    df_stochastic = df_design.copy()
    df_stochastic['type'] = 'absolute Uniform'
    df_stochastic['val'] = df_stochastic['val'] * 0.25
    return df_design, df_stochastic


def res_demand_params(data: pd.DataFrame):
    """
    Define the uncertainty parameters related to eud.
    U[-10.5%, 5.9%]: elec, heat, non-energy
    U[-3.4%, 3.4%]: transport
    """
    l_HOUSEHOLDS = ['ELECTRICITY', 'LIGHTING', 'HEAT_LOW_T_SH', 'HEAT_LOW_T_HW']
    l_SERVICES = ['ELECTRICITY', 'LIGHTING', 'HEAT_LOW_T_SH', 'HEAT_LOW_T_HW']
    l_INDUSTRY = ['ELECTRICITY', 'LIGHTING', 'HEAT_HIGH_T', 'HEAT_LOW_T_SH', 'HEAT_LOW_T_HW', 'NON_ENERGY']
    l_TRANSPORTATION = ['MOBILITY_PASSENGER', 'MOBILITY_FREIGHT']
    cat_list = ['HOUSEHOLDS', 'SERVICES', 'INDUSTRY']

    df_design_list = []
    df_stochastic_list = []
    for l, cat, coeff in zip([l_HOUSEHOLDS, l_SERVICES, l_INDUSTRY], cat_list,[0.105, 0.105, 0.105, 0.034]):
        df_design = pd.DataFrame(data=['par'] * len(l), index=[cat + '-' + i for i in l], columns=['type'])
        df_design['val'] = 0.0
        df_design['dev'] = 0.0
        for res in l:
            val = data.at[res, cat]
            max_val = val * (1+0.059)
            min_val = val * (1-0.105)
            val_av = (max_val + min_val)/2
            val_dev = (max_val - min_val)/2
            df_design.at[cat + '-' + res, 'val'] = val_av
            df_design.at[cat + '-' + res, 'dev'] = val_dev

        df_stochastic = df_design.copy()
        df_stochastic['type'] = 'absolute Uniform'
        df_stochastic = df_stochastic.drop(['val'], axis=1)
        df_stochastic.columns = ['type', 'val']
        df_design = df_design.drop(['dev'], axis=1)
        df_design_list.append(df_design)
        df_stochastic_list.append(df_stochastic)

    # specific case of the transportation
    cat = 'TRANSPORTATION'
    df_design = pd.DataFrame(data=['par'] * len(l_TRANSPORTATION), index=[cat + '-' + i for i in l_TRANSPORTATION],
                             columns=['type'])
    df_design['val'] = 0.0
    for res in l_TRANSPORTATION:
        df_design.at[cat + '-' + res, 'val'] = data.at[res, cat]

    df_stochastic = df_design.copy()
    df_stochastic['type'] = 'absolute Uniform'
    df_stochastic['val'] = df_stochastic['val'] * 0.034
    df_design_list.append(df_design)
    df_stochastic_list.append(df_stochastic)

    return pd.concat(df_design_list, axis=0), pd.concat(df_stochastic_list, axis=0)


def tech_fmax_params(data: pd.DataFrame):
    """
    Define the uncertainty parameters related to f_max of renewable technologies.
    U[-24.1%, 24.1%]: PV, Wind off/onshore.
    NUCLEAR: f_max is between 0 and 5.6 GW -> U[0, 5.6]
    GEOTHERMAL: f_max is between 0 and 2.0 GW -> U[0, 2.0]
    DHN_DEEP_GEO: f_max is between 0 and 2.0 GW -> U[0, 2.0]
    """
    l = ['PV', 'WIND_OFFSHORE', 'WIND_ONSHORE']
    df_design = pd.DataFrame(data=['par'] * len(l), index=['f_max-' + i for i in l], columns=['type'])
    df_design['val'] = 0.0
    for res in l:
        df_design.at['f_max-' + res, 'val'] = data.at[res, 'f_max']

    df_stochastic = df_design.copy()
    df_stochastic['type'] = 'absolute Uniform'
    df_stochastic['val'] = df_stochastic['val'] * 0.241

    df2_design = pd.DataFrame([['par', 2.8], ['par', 1.0], ['par', 1.0]], columns=['type', 'val'],
                              index=['f_max-NUCLEAR', 'f_max-GEOTHERMAL', 'f_max-DHN_DEEP_GEO'])
    df2_stochastic = pd.DataFrame([['absolute Uniform', 2.8], ['absolute Uniform', 1.0], ['absolute Uniform', 1.0]],
                                  columns=['type', 'val'],
                                  index=['f_max-NUCLEAR', 'f_max-GEOTHERMAL', 'f_max-DHN_DEEP_GEO'])

    return df_design.append(df2_design), df_stochastic.append(df2_stochastic)


def tech_cpt_params(data: pd.DataFrame):
    """
    Define the uncertainty parameters related to c_pt of renewable resources.
    U[-11.1%, 11.1%]: 'PV', 'Wind_onshore', 'Wind_offshore', 'Hydro_river', 'Solar'
    """
    l = ['PV', 'Wind_onshore', 'Wind_offshore', 'Hydro_river', 'Solar']
    df_design = pd.DataFrame(data=['par'] * len(l), index=['c_pt-' + i for i in l], columns=['type'])
    df_design['val'] = 0.0
    for res in l:
        df_design.at['c_pt-' + res, 'val'] = data[res].mean()

    df_stochastic = df_design.copy()
    df_stochastic['type'] = 'absolute Uniform'
    df_stochastic['val'] = df_stochastic['val'] * 0.111

    return df_design, df_stochastic


def other_params(config: dict):
    """
    Define the uncertainty parameters related to other parameters:
     - electricity import capacity U[-10%, 10%]
     - i_rate U[-46.2%, 46.2%]
     - loss elec and heat U[-2.0%, 2.0%]
     - public/rail/boat and dhn share max U[-10.0%, 10.0%]
    """

    l1 = ['import_capacity', 'i_rate']
    df_design1 = pd.DataFrame(data=['par'] * len(l1), index=['other-' + i for i in l1], columns=['type'])
    df_design1['val'] = 0.0
    for p in l1:
        df_design1.at['other-' + p, 'val'] = config[p]

    df_stochastic1 = df_design1.copy()
    df_stochastic1['type'] = 'absolute Uniform'
    df_stochastic1['val'] = 0.0
    for p, coeff in zip(l1, [0.10, 0.462]):
        df_stochastic1.at['other-' + p, 'val'] = coeff * df_design1.at['other-' + p, 'val']

    l2 = ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max', 'share_heat_dhn_max']
    df_design2 = pd.DataFrame(data=['par'] * len(l2), index=['other-' + i for i in l2], columns=['type'])
    df_design2['val'] = 0.0
    for p in l2:
        df_design2.at['other-' + p, 'val'] = config['technologie_shares'][p]

    df_stochastic2 = df_design2.copy()
    df_stochastic2['type'] = 'absolute Uniform'
    df_stochastic2['val'] = df_stochastic2['val'] * 0.10

    l3 = ['ELECTRICITY', 'HEAT_LOW_T_DHN']
    df_design3 = pd.DataFrame(data=['par'] * len(l3), index=['other-' + i for i in l3], columns=['type'])
    df_design3['val'] = 0.0
    for p in l3:
        df_design3.at['other-' + p, 'val'] = config['loss_network'][p]

    df_stochastic3 = df_design3.copy()
    df_stochastic3['type'] = 'absolute Uniform'
    df_stochastic3['val'] = df_stochastic3['val'] * 0.02

    return pd.concat([df_design1, df_design2, df_design3], axis=0), pd.concat(
        [df_stochastic1, df_stochastic2, df_stochastic3], axis=0)


if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config_ = load_config(config_fn='config_uq.yaml')

    # Loading data
    all_data = es.import_data(user_data_dir=config_['user_data'], developer_data_dir=config_['developer_data'])
    # Modify the minimum capacities of some technologies using the configuration file
    for tech in config_['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config_['Technologies']['f_min'][tech]

    # Build the list of uncertain parameters
    df_design_res_av, df_stochastic_res_av = res_avail_params(data=all_data['Resources'])
    df_design_res_einv_op, df_stochastic_res_einv_op = res_einv_op_params(data=all_data['Resources'])
    df_design_demand, df_stochastic_demand = res_demand_params(data=all_data['Demand'])
    df_design_tech_fmax, df_stochastic_tech_fmax = tech_fmax_params(data=all_data['Technologies'])
    df_design_res_einv_constr, df_stochastic_res_einv_constr = res_einv_constr_params(data=all_data['Technologies'])
    df_design_res_c_pt, df_stochastic_res_c_pt = tech_cpt_params(data=all_data['Time_series'])
    df_design_other, df_stochastic_other = other_params(config=config_['system_limits'])

    df_design_ = pd.concat([df_design_res_av, df_design_res_einv_op, df_design_demand, df_design_tech_fmax,
                           df_design_res_einv_constr, df_design_res_c_pt, df_design_other], axis=0)
    df_stochastic_ = pd.concat([df_stochastic_res_av, df_stochastic_res_einv_op, df_stochastic_demand,
                               df_stochastic_tech_fmax, df_stochastic_res_einv_constr, df_stochastic_res_c_pt,
                               df_stochastic_other], axis=0)
    df_design_.to_csv('data_samples/design_space', sep=' ')
    df_stochastic_.to_csv('data_samples/stochastic_space', sep=' ')

    param_list = dict()
    param_list['avail'] = list(df_design_res_av.index)
    param_list['einv_op'] = list(df_design_res_einv_op.index)
    param_list['demand'] = list(df_design_demand.index)
    param_list['f_max'] = list(df_design_tech_fmax.index)
    param_list['einv_constr'] = list(df_design_res_einv_constr.index)
    param_list['c_pt'] = list(df_design_res_c_pt.index)
    param_list['other'] = list(df_design_other.index)

    json.dump(param_list, open("data_samples/param_list.json", "w"), sort_keys=True, indent=4)
