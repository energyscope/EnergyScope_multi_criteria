import os
from pathlib import Path
import energyscope as es
import matplotlib.pyplot as plt
import numpy as np

def save_data_to_txt(data, header, case_study):
    filename = f'{case_study}_data_barh.txt'
    data_with_header = np.column_stack((header, data))
    np.savetxt(filename, data_with_header, delimiter=',', fmt='%s')


if __name__ == '__main__':
    analysis_only = True
    compute_TDs = False

    # define project path
    project_path = Path(__file__).parents[1]

    # loading the config file into a python dictionary
    config = es.load_config(config_fn='config_ref.yaml', project_path=project_path)
    config['Working_directory'] = os.getcwd()  # keeping current working directory into config

    # Reading the data of the csv
    es.import_data(config)

    if compute_TDs:
        es.build_td_of_days(config)

    # Example to change data:
    # config['all_data']['Resources'].loc['WOOD', 'avail'] = 23400
    # config['all_data']['Misc']['share_mobility_public_max'] = 0.5

    # f_max
    # config['all_data']['Technologies'].loc['NUCLEAR', 'f_max'] = 1000000

    if not analysis_only:
        # Printing the .dat files for the optimisation problem
        es.print_data(config)

        # Running EnergyScope
        es.run_es(config)

    # Example to print the sankey from this script
    if config['print_sankey']:
        sankey_path = config['cs_path'] / config['case_study'] / 'output' / 'sankey'
        es.drawSankey(path=sankey_path)

    outputs = es.read_outputs(config['case_study'], hourly_data=True, layers=['layer_ELECTRICITY','layer_HEAT_LOW_T_DECEN'])
    elec_assets = es.get_assets_l(layer='ELECTRICITY', eff_tech=config['all_data']['Layers_in_out'],
                                  assets=outputs['assets'])
    # Plots (examples)
    # primary resources used
    if config['print_barh']:
        fig2, ax2 = es.plot_barh(outputs['resources_breakdown'][['Used']], title='Primary energy [GWh/y]')
        data_barh_2 = outputs['resources_breakdown'][['Used']]
        header_2 = outputs['resources_breakdown'].index.values.reshape(-1, 1)
        #save_data_to_txt(data_barh_2, header_2, config['case_study'])
        fig3, ax3 = es.plot_barh(elec_assets[['f']], title='Electricity assets [GW_e]',x_label='Installed capacity [GW_e]')
        data_elec_assets_3 = elec_assets[['f']]
        header_elec_assets_3 = elec_assets.index.values.reshape(-1, 1)
        save_data_to_txt(data_elec_assets_3, header_elec_assets_3, config['case_study'])

    # layer_HEAT_LOW_T_DECEN for the 12 tds
    if config['print_hourly_data']:
        fig, ax = es.hourly_plot(plotdata=outputs['layer_HEAT_LOW_T_DECEN'], nbr_tds=12, show_plot=True)
        elec_layer_plot = es.plot_layer_elec_td(outputs['layer_ELECTRICITY'])