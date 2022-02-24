# -*- coding: utf-8 -*-
"""
This script quantifies the impact of uncertain parameters on the model output.
For the uncertainty ranges see Appendix D, Table D.1 Ph.D. thesis G. Limpens.
The ranges were determined by the Ph.D. of S. Morret see Table 2.1.
At this stage we only consider uncertainty on:
- EUD;
- resources availability;
- resources einv_op: same ranges than c_op;
- technologies f_max capacities: fmax is uncertain only for renewable resources: PV, wind offshore and onshore
- technologies einv_const: same ranges than c_inv
- technologies capacity factors;

Extensions by including uncertainty on:
- cost: c_op, c_maint, and c_inv
- gwp: gwp_op and gwp_const
- efficiencies
- einv_const: storage technologies
- einv_op and einv_const: determine relevant uncertainty intervals

@author: Jonathan Dumas
"""

import yaml
import os
import scipy.special

import pandas as pd
import energyscope as es
import numpy as np
import matplotlib.pyplot as plt

from sys import platform

from energyscope.utils import load_config


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


N_samples = 500
ID_sample = 1

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    # Load configuration into a dict
    config = load_config(config_fn='config_uq.yaml')

    # Loading data
    all_data = es.import_data(user_data_dir=config['user_data'], developer_data_dir=config['developer_data'])
    # Modify the minimum capacities of some technologies
    for tech in config['Technologies']['f_min']:
        all_data['Technologies']['f_min'].loc[tech] = config['Technologies']['f_min'][tech]

    # Generate samples of EUD based on uncertainty ranges
    # U[-10.5%, 10.5%]: EUD elec, heat, non-energy
    # U[-3.4%, 3.4%]: EUD transport
    df_demand_min = pd.read_csv('data_uq/demand-uq-min.csv', index_col=0)
    df_demand_max = pd.read_csv('data_uq/demand-uq-max.csv', index_col=0)
    df_eud_samples_list = []
    for eud in all_data['Demand'].index:
        for type in ['HOUSEHOLDS', 'SERVICES', 'INDUSTRY','TRANSPORTATION']:
            # U[min, max] with min and max both = 0 or both != 0.
            if df_demand_min.at[eud, type] != 0:
                val_min = all_data['Demand'].at[eud, type] * (1+df_demand_min.at[eud, type]/100)
                val_max = all_data['Demand'].at[eud, type] * (1+df_demand_max.at[eud, type]/100)
                df_eud_samples_list.append(pd.DataFrame(data=np.random.uniform(val_min, val_max, N_samples), columns=[eud+'-'+type]))
    df_eud_samples = pd.concat(df_eud_samples_list,axis=1)
    df_eud_samples.to_csv('data_uq/demand-samples-' + str(ID_sample) + '.csv')

    # Generate samples of resources parameters based on uncertainty ranges
    # availability U[-32.1%, 32.1%]: wood, wet biomass, and waste
    # einv_op: by default U[-25%, 25%] -> a study similar to the one conducted in the Ph.D. thesis of S. Moret must be conducted
    df_res_min = pd.read_csv('data_uq/resources-uq-min.csv', index_col=0)
    df_res_max = pd.read_csv('data_uq/resources-uq-max.csv', index_col=0)
    # convert the columns 'avail', 'gwp_op', 'c_op', 'einv_op' from object type to float64
    all_data['Resources'][['avail', 'gwp_op', 'c_op', 'einv_op']] = all_data['Resources'][['avail', 'gwp_op', 'c_op', 'einv_op']].astype('float')
    df_res_samples_list = []
    for type in ['avail', 'einv_op']:
        for res in all_data['Resources'].index:
            # U[min, max] with min and max both = 0 or both != 0.
            if df_res_min.at[res, type] != 0:
                val_min = all_data['Resources'].at[res, type] * (1+df_res_min.at[res, type]/100)
                val_max = all_data['Resources'].at[res, type] * (1+df_res_max.at[res, type]/100)
                df_res_samples_list.append(pd.DataFrame(data=np.random.uniform(val_min, val_max, N_samples), columns=[type+'-'+res]))
    df_res_samples = pd.concat(df_res_samples_list,axis=1)
    df_res_samples.to_csv('data_uq/resources-samples-' + str(ID_sample) + '.csv')

    # df_res_copy = all_data['Resources'].drop(['Category', 'Subcategory', 'gwp_op', 'c_op'], axis=1).copy()
    # df_res_copy.to_csv('data_uq/resources-uq-min.csv')
    # df_res_copy.to_csv('data_uq/resources-uq-max.csv')

    # Generate samples of technologies parameters based on uncertainty ranges
    # f_max U[-24.1%, 24.1%]: PV, Wind off/onshore, hydro river, PHS
    # c_p: electricity production tech, industrial and district heating technologies, mobility (private, public, and freight), hydrogen production tech, synthetic fuels conversion tech,
    # c_p U[-2.4%, 2.4%]
    # Warning: all technologies with c_p = 100% are not concerned -> decentralized heating, storages, and renewable technologies
    # einv_const: CCS and storages technologies -> not taken into account
    # einv_const: by default U[-25%, 25%] -> a study similar to the one conducted in the Ph.D. thesis of S. Moret must be conducted

    # The following technologies are not taken into account:
    # COAL_IGCC, COAL_US, IND_BOILER_COAL -> not used when constraining GHG emissions
    # Boilers: "boilers are rarely used more than 50% of the time, so the constraints containing the boilers capacity factor are never activated"
    # convert dtype from object to float
    all_data['Technologies'][['c_inv', 'c_maint',
                              'gwp_constr', 'einv_constr', 'lifetime', 'c_p', 'fmin_perc',
                              'fmax_perc', 'f_min', 'f_max']] = all_data['Technologies'][['c_inv', 'c_maint',
                              'gwp_constr', 'einv_constr', 'lifetime', 'c_p', 'fmin_perc',
                              'fmax_perc', 'f_min', 'f_max']].astype('float')
    df_tech_min = pd.read_csv('data_uq/tech-uq-min.csv', index_col=0)
    df_tech_max = pd.read_csv('data_uq/tech-uq-max.csv', index_col=0)
    df_tech_samples_list = []
    for type in ['einv_constr', 'c_p', 'f_max']:
        for tech in all_data['Technologies'].index:
            if df_tech_min.at[tech, type] != 0:
                val_min = all_data['Technologies'].at[tech, type]* (1+df_tech_min.at[tech, type]/100)
                val_max = all_data['Technologies'].at[tech, type]* (1+df_tech_max.at[tech, type]/100)
                df_tech_samples_list.append(pd.DataFrame(data=np.random.uniform(val_min, val_max, N_samples), columns=[type+'-'+tech]))
    df_tech_samples_list.append(pd.DataFrame(data=np.random.uniform(0, 5.6, N_samples), columns=['f_max'+'-'+'NUCLEAR'])) # f_max_nuc U[0, 5.6] GW
    df_tech_samples_list.append(pd.DataFrame(data=np.random.uniform(0, 2.0, N_samples), columns=['f_max'+'-'+'GEOTHERMAL']))  # f_max_geo U[0, 2.0] GW
    df_tech_samples = pd.concat(df_tech_samples_list,axis=1)
    df_tech_samples.to_csv('data_uq/tech-samples-' + str(ID_sample) + '.csv')

    # df_tech_copy = all_data['Technologies'].drop(['Category', 'Subcategory', 'Technologies name', 'c_inv', 'c_maint', 'gwp_constr', 'lifetime', 'fmin_perc', 'fmax_perc', 'f_min'], axis=1).copy()
    # df_tech_copy.to_csv('data_uq/tech-uq-min.csv')
    # df_tech_copy.to_csv('data_uq/tech-uq-max.csv')

    # Generate samples of capacity factors of seasonable renewables technologies: PV, wind on/offshore, hydro river, and solar
    df_cpt_samples_list = []
    for tech_cp in ['PV', 'Wind_onshore', 'Wind_offshore', 'Hydro_river', 'Solar']:
        val_min = all_data['Time_series'][tech_cp].mean() * (1+11.1/100)
        val_max = all_data['Time_series'][tech_cp].mean() * (1+-11.1/100)
        df_cpt_samples_list.append(pd.DataFrame(data=np.random.uniform(val_min, val_max, N_samples), columns=['cpt-'+tech_cp]))
    df_cpt_samples = pd.concat(df_cpt_samples_list,axis=1)
    df_cpt_samples.to_csv('data_uq/cpt-samples-' + str(ID_sample) + '.csv')

    # Other parameters
    # electricity import capacity U[-10%, 10%]: -> from the configuration file
    # i_rate U[-46.2%, 46.2%]: -> from the configuration file
    # %loss elec and heat U[-2.0%, 2.0%]: -> from the configuration file
    # public/rail/boat and dhn share max  U[-10.0%, 10.0%]: -> from the configuration file
    df_other_samples_list = []
    for param in ['import_capacity', 'i_rate']:
        val_min = config['system_limits'][param] * (1+10/100)
        val_max = config['system_limits'][param] * (1-10/100)
        df_other_samples_list.append(pd.DataFrame(data=np.random.uniform(val_min, val_max, N_samples), columns=['other-'+param]))
    for share_max in ['share_mobility_public_max', 'share_freight_train_max', 'share_freight_boat_max', 'share_heat_dhn_max']:
        val_min = config['system_limits']['technologie_shares'][share_max] * (1+10/100)
        val_max = config['system_limits']['technologie_shares'][share_max] * (1-10/100)
        df_other_samples_list.append(pd.DataFrame(data=np.random.uniform(val_min, val_max, N_samples), columns=['other-' + share_max]))
    for loss_network in ['ELECTRICITY', 'HEAT_LOW_T_DHN']:
        val_min = config['system_limits']['loss_network'][loss_network] * (1+10/100)
        val_max = config['system_limits']['loss_network'][loss_network] * (1-10/100)
        df_other_samples_list.append(pd.DataFrame(data=np.random.uniform(val_min, val_max, N_samples), columns=['other-' + loss_network]))
    df_other_samples = pd.concat(df_other_samples_list,axis=1)
    df_other_samples.to_csv('data_uq/other-samples-' + str(ID_sample) + '.csv')

    # mature standard U[-5.7%, 5.7%]
    # df_eff_mature_std_samples_list = []
    # eff_tech_list, tech_list = eff_mature_standard_tech(df=all_data['Layers_in_out'])
    # for eff_tech, tech_name in zip(eff_tech_list, tech_list):
    #     val_min = eff_tech * (1 + 5.7 / 100)
    #     val_max = eff_tech * (1 - 5.7 / 100)
    #     df_eff_mature_std_samples_list.append(pd.DataFrame(data=np.random.uniform(val_min, val_max, N_samples), columns=['eff_' + tech_name]))
    # df_eff_mature_std_samples = pd.concat(df_eff_mature_std_samples_list, axis=1)
    # df_eff_mature_std_samples.to_csv('data_uq/eff-mature-std-samples.csv')

    # Concatenate all samples
    df_all_samples = pd.concat([df_eud_samples, df_res_samples, df_tech_samples, df_other_samples], axis=1)
    df_all_samples.to_csv('data_uq/all-samples-' + str(ID_sample) + '.csv')

    print('%s uncertain parameters' %(len(df_all_samples.columns)))
    print('first-order PCE %s number of coefficients ' %(scipy.special.binom(len(df_all_samples.columns)+1, 1)))
    print('second-order PCE %s number of coefficients' %(scipy.special.binom(len(df_all_samples.columns)+2, 2)))