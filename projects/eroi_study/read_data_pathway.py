# -*- coding: utf-8 -*-
"""
@author: Jonathan Dumas

Create data for 2015 and 2050.
WARNING: Einv data for 2015 and 2050 are copied from 2035.
Other data: demand, Layers_in_out, Resources, and technologies (cost, GWP, etc) are copied from the excel files of EnergyScope_pathway-master
https://github.com/energyscope/EnergyScope_pathway
"""

import os
import pandas as pd
import numpy as np

if __name__ == '__main__':

    cwd = os.getcwd()
    print("Current working directory: {0}".format(cwd))

    df_efficiency_2015 = pd.read_csv('data_pathway/efficiencies_2015.csv', sep=',', index_col=0)
    df_efficiency_2015.to_csv('data_pathway/Layers_in_out_2015.csv', sep=',')

    df_efficiency_2035 = pd.read_csv('data_pathway/efficiencies_2035.csv', sep=',', index_col=0)
    df_efficiency_2035.to_csv('data_pathway/Layers_in_out_2035.csv', sep=',')

    df_efficiency_2050 = pd.read_csv('data_pathway/efficiencies_2050.csv', sep=',', index_col=0)
    df_efficiency_2050.to_csv('data_pathway/Layers_in_out_2050.csv', sep=',')

    # df_test = pd.read_csv('data_pathway/Resources_2050.csv', sep=',', index_col=0)
    # df_test2 = pd.read_csv('data_pathway/Resources_2035.csv', sep=',', index_col=0)

    # Load the original Technologies data from 2035
    year = '2050' # '2015, '2050'
    df_TECH = pd.read_csv('data_pathway/Technologies_2035.csv', sep=',', index_col=0)
    # Load the input data
    df_TECH_input = pd.read_csv('data_pathway/Technologies_'+year+'_input.csv', sep=',', index_col=0)
    tech_list = list(df_TECH['parameter name'].values[1:])

    # Reorder by index the input data following the index of the Technologies data from 2035
    copy_list = []
    for tech in tech_list:
        copy_list.append(df_TECH_input.loc[tech].astype(float).values)
    df_TECH_input_reordered = pd.DataFrame(data=np.asarray(copy_list), index=tech_list, columns=df_TECH_input.columns)
    # Add the einv_constr from 2035
    df_TECH_input_reordered['einv_constr'] = df_TECH['einv_constr'].copy().values[1:]
    # Reorder the column in the same order than the Technologies data from 2035
    df_TECH_input_final = df_TECH_input_reordered[['c_inv',
     'c_maint', 'gwp_constr', 'einv_constr', 'lifetime', 'c_p', 'fmin_perc',
     'fmax_perc', 'f_min', 'f_max']].copy()

    # Build a DataFrame with the same format than 2035
    df_TECH_copy = pd.DataFrame(index=df_TECH.iloc[1:].index, data=df_TECH.iloc[1:]['Subcategory'].copy(), columns=['Subcategory'])
    df_TECH_copy['Technologies name'] = df_TECH.iloc[1:]['Technologies name'].copy()
    df_TECH_copy['parameter name'] = df_TECH.iloc[1:]['parameter name'].copy()
    for col in df_TECH_input_final.columns:
        df_TECH_copy[col] = df_TECH_input_final[col].copy().values
    df_TECH_copy.to_csv('data_pathway/Technologies_'+year+'.csv', sep=',')