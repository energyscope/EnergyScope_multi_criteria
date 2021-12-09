import pandas as pd


def generate_demand_csv():

    # Demand
    demand = pd.read_excel("Data_management/DATA.xlsx", sheet_name='2.3 EUD', index_col=0, header=1, usecols=range(5))
    demand.columns = [x.strip() for x in demand.columns]
    demand.index = [x.strip() for x in demand.index]

    # Add additional information
    demand_aux = pd.read_csv("Data/User_data/aux_demand.csv", index_col=0)
    demand = pd.merge(demand, demand_aux, left_index=True, right_index=True)

    # Rename and reorder columns
    demand.index.name = 'parameter name'
    demand = demand.reset_index()
    demand = demand[['Category', 'Subcategory', 'parameter name', 'HOUSEHOLDS',
                     'SERVICES', 'INDUSTRY', 'TRANSPORTATION', 'Units']]

    demand.to_csv("Data/User_data/Demand.csv", sep=',', index=False)


def generate_resources_csv():

    # Resources
    resources = pd.read_excel("Data_management/DATA.xlsx", sheet_name='2.1 RESOURCES', index_col=0, header=1,
                              usecols=range(5))
    resources.index = [x.strip() for x in resources.index]
    resources.columns = [x.split(" ")[0] for x in resources.columns]

    # Add additional information
    resources_aux = pd.read_csv("Data/User_data/aux_resources.csv", index_col=0)
    resources = pd.merge(resources, resources_aux, left_index=True, right_index=True)

    # Rename and reorder columns
    resources.index.name = 'parameter name'
    resources = resources.reset_index()
    resources = resources[['Category', 'Subcategory', 'parameter name', 'avail', 'gwp_op', 'c_op', 'einv_op']]
    # resources.columns = ['Category', 'Subcategory', 'parameter name', 'Availability', 'Direct and indirect emissions',
    #                      'Price', 'Direct emissions']

    # Add a line with units
    units = pd.Series(['', '', 'units', '[GWh/y]', '[ktCO2-eq./GWh]', '[Meuro/GWh]', '[GWh/y]'],
                      index=resources.columns)
    resources = pd.concat((units.to_frame().T, resources), axis=0)

    resources.to_csv("Data/User_data/Resources.csv", sep=',', index=False)


def generate_technologies_csv():

    # Technologies
    technologies = pd.read_excel("Data_management/DATA.xlsx", sheet_name='3.2 TECH', index_col=1)
    technologies = technologies.drop(technologies.columns[[0]], axis=1)
    technologies.index = [x.strip() for x in technologies.index]

    # Add additional information
    technologies_aux = pd.read_csv("Data/User_data/aux_technologies.csv", index_col=0)
    technologies = pd.merge(technologies, technologies_aux, left_index=True, right_index=True)

    # Rename and reorder columns
    technologies.index.name = 'parameter name'
    technologies = technologies.reset_index()
    technologies = technologies[['Category', 'Subcategory', 'Technologies name', 'parameter name', 'c_inv',  'c_maint',
                                 'gwp_constr', 'einv_constr', 'lifetime', 'c_p', 'fmin_perc', 'fmax_perc',
                                 'f_min', 'f_max']]

    # Add a line with units
    units = pd.Series(['', '', 'Name (simplified)', 'Name (in model and documents)',
                       '[Meuro/GW],[Meuro/GWh],[Meuro/(Mkmpass/h)],[Meuro/(Mtonkm/h)]',
                       '[Meuro/GW],[Meuro/GWh],[Meuro/(Mkmpass/h)],[Meuro/(Mtonkm/h)]',
                       '[ktonCO2_eq/GW],[ktonCO2_eq/GWh],[ktonCO2_eq/(Mkmpass/h)],[ktonCO2_eq/(Mtonkm/h)]',
                       '[GWh/y]', '[years]', '[]', '[]', '[]', '[GW]', '[GW]'],
                      index=technologies.columns)
    technologies = pd.concat((units.to_frame().T, technologies), axis=0)

    technologies.to_csv("Data/User_data/Technologies.csv", sep=',', index=False)


def generate_layers_csv():

    # Layers in-out
    layers = pd.read_excel("Data_management/DATA.xlsx", sheet_name='3.1 layers_in_out', index_col=1)
    layers = layers.drop(layers.columns[0], axis=1)
    layers.columns = [x.strip() for x in layers.columns]
    layers.to_csv("Data/Developer_data/Layers_in_out.csv", sep=',')


def generate_storage_csv():

    # Storage eff in
    storage_eff_in = pd.read_excel("Data_management/DATA.xlsx", sheet_name='3.3 STO', header=2, nrows=25, index_col=0)
    storage_eff_in.index = [x.strip() for x in storage_eff_in.index]
    storage_eff_in.to_csv("Data/Developer_data/Storage_eff_in.csv", sep=',')

    # Storage eff out
    storage_eff_out = pd.read_excel("Data_management/DATA.xlsx", sheet_name='3.3 STO', header=30, nrows=25, index_col=0)
    storage_eff_out.index = [x.strip() for x in storage_eff_out.index]
    storage_eff_out.to_csv("Data/Developer_data/Storage_eff_out.csv", sep=',')

    # Storage characteristics
    storage_c = pd.read_excel("Data_management/DATA.xlsx", sheet_name='3.3 STO', header=58, nrows=25, index_col=0)
    storage_c.index = [x.strip() for x in storage_c.index]
    storage_c.dropna(axis=1).to_csv("Data/Developer_data/Storage_characteristics.csv", sep=',')


def generate_time_series_csv():

    # Time series
    time_series = pd.read_excel("Data_management/DATA.xlsx", sheet_name='1.1 Time Series', index_col=0, header=1,
                                usecols=range(11), nrows=8761)
    time_series = time_series.drop(time_series.columns[0], axis=1)
    time_series = time_series.drop(time_series.index[0])
    time_series.columns = ["Electricity (%_elec)", "Space Heating (%_sh)",
                           "Passanger mobility (%_pass)", "Freight mobility (%_freight)",
                           "PV", "Wind_onshore", "Wind_offshore", "Hydro_river", "Solar"]
    time_series.to_csv("Data/Developer_data/Time_series.csv", sep=',')


def estd_excel_to_csv():

    generate_demand_csv()
    generate_resources_csv()
    generate_technologies_csv()
    generate_layers_csv()
    generate_storage_csv()
    generate_time_series_csv()


if __name__ == '__main__':
    generate_technologies_csv()
