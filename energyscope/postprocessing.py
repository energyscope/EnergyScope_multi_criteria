# -*- coding: utf-8 -*-
"""
This script provides postprocessing functions.

@author: Antoine Dubois, Jonathan Dumas
"""

import pandas as pd


def get_cost(cs: str):
    """
    Get the cost from cost_breakdown.csv.
    :param cs: directory name.
    :return cost values breakdown between C_inv, C_maint, and C_op.
    """
    cost = pd.read_csv(f"{cs}/output/cost_breakdown.csv", index_col=0, sep=',')

    return cost.sum()


def get_total_cost(output_path: str):
    costs = pd.read_csv(f"{output_path}/output/cost_breakdown.csv", index_col=0)
    return costs.sum().sum()


def get_gwp(cs: str):
    """
    Get the GWP from gwp_breakdown.csv.
    :param cs: directory name.
    :return GWP value.
    """
    gwp = pd.read_csv(f"{cs}/output/gwp_breakdown.csv", index_col=0, sep=',')

    return gwp.sum()


def get_total_gwp(output_path: str):
    gwp = pd.read_csv(f"{output_path}/output/gwp_breakdown.csv", index_col=0)
    return gwp.sum().sum()


def compute_einv_res(cs: str, all_data: dict):
    """
    Compute the Einv by RESOURCES part (Einv_op).
    :param cs: case study path
    :param all_data: the data into a dict of pd.DataFrames.
    :return: the data into pd.DataFrames
    """
    # Load Einv data
    df_einv = pd.read_csv(f"{cs}/output/einv_breakdown.csv", index_col=0)
    # Define the RESOURCES list
    resources = list(all_data['Resources'].index)
    return df_einv.loc[resources].copy()['Einv_op']


def compute_einv_tech(cs: str, all_data: dict):
    """
    Compute the Einv by TECHNOLOGIES part (Einv_const).
    :param cs: case study path
    :param all_data: the data into a dict of pd.DataFrames.
    :return: the data into pd.DataFrames
    """
    # Load Einv data
    df_einv = pd.read_csv(f"{cs}/output/einv_breakdown.csv", index_col=0)
    # Define the TECHNOLOGIES list
    technologies = list(all_data['Technologies'].index)
    return df_einv.loc[technologies].copy()['Einv_constr']


def get_total_einv(output_path: str):
    einv = pd.read_csv(f"{output_path}/output/einv_breakdown.csv", index_col=0)
    return einv.sum().sum()


def get_asset_value(output_path: str, param: str, tech: str, from_pickle=False):
    assets = pd.read_csv(f"{output_path}/output/assets.csv", index_col=0)
    assets.columns = [c.strip() for c in assets.columns]
    return float(assets.loc[tech, param])


def get_resource_used(output_path: str, res: str):
    resources_breakdown = pd.read_csv(f"{output_path}/output/resources_breakdown.csv", index_col=0)
    return resources_breakdown.loc[res, 'Used']


def fec_given_tech(tech: str, data: pd.DataFrame, prod_corr: float):
    """
    Compute the FEC related to a given EUD and TECHNO.
    :param tech: technology type to satisfy this EUD type such as IND_COGEN_GAS if EUD = HEAT_HIGH_T
    :param data: dataframe with the year_balance.csv
    :param prod_corr: FIXME: complete
    return: FEC value
    """

    # get the inputs for a given technology: electricity, gas, H2, etc.
    inputs_tech = data.loc[tech][data.loc[tech] < 0].copy()
    # get the outputs for a given technology: electricity, heat high T, heat low T FHN, etc.
    outputs_tech = data.loc[tech][data.loc[tech] > 0].copy()
    if outputs_tech.sum() == 0:
        return
    else:
        # remove C02 emissions
        outputs_labels = list(outputs_tech.index)
        for lab in ['CO2_ATM', 'CO2_INDUSTRY', 'CO2_CAPTURED']:
            if lab in outputs_labels:
                outputs_tech = outputs_tech.drop([lab], axis=0)
        # Ex: eud = 'HEAT_HIGH_T' and tech = 'IND_COGEN_GAS'
        # IND_COGEN_GAS inputs: gas with 2.1739
        # IND_COGEN_GAS outputs: electricity with 0.9565 and HEAT_HIGH_T with 1
        # -> FEC = (1 * (1+0.9565)) * (2.1739)
        # Warning a technology may have several inputs such as CAR_PHEV with 0.1376 of ELECTRICITY
        # and 0.1087 of GASOLINE for 1 of MOB_PRIVATE
        return (prod_corr / outputs_tech.sum()) * (-inputs_tech.sum())


def compute_fec(data: pd.DataFrame, user_data: str):
    """
    Compute the system FEC for a given simulation in GWh.
    :param data: year_balance.csv
    :param user_data: FIXME: complete
    :return FEC detailed by EUD and technologies into fec_details dict, and FEC aggregated by EUD into fec_tot dict.
    Assumption: FEC ELECTRICITY = EUF ELECTRICITY
    See the FEC computation details for a given EUD in the function fec_given_tech(eud=eud, tech=tech, data=data)
    """
    eud_types = ['HEAT_HIGH_T', 'HEAT_LOW_T_DHN', 'HEAT_LOW_T_DECEN', 'MOB_PUBLIC', 'MOB_PRIVATE', 'MOB_FREIGHT_RAIL',
                 'MOB_FREIGHT_BOAT', 'MOB_FREIGHT_ROAD', 'HVC', 'AMMONIA', 'METHANOL']

    df_aux_res = pd.read_csv(user_data + "/aux_resources.csv", index_col=0)
    resources = list(df_aux_res.index)
    fec_details = dict()
    fec_tot = dict()
    prod_tech_eud = dict()
    for eud in eud_types:
        fec_eud = []
        # list of tech that produced this eud
        prod_tech_eud[eud] = data[eud].drop(index=['END_USES_DEMAND'])[data[eud] > 0]
        prod_sum = prod_tech_eud[eud].sum()
        # total consumption of this energy
        conso_sum = -data[eud].drop(index=['END_USES_DEMAND'])[data[eud] < 0].sum()
        # Note: conso_eud + eud = prod_sum
        # We calculate the FEC of the eud and not of conso_eud + eud! -> a correction factor is required
        for tech in list(prod_tech_eud[eud].index):
            # correction factor to calculate the FEC corresponding at the consumption of the eud
            corr_factor = prod_tech_eud[eud][tech] / prod_sum
            prod_corr = prod_tech_eud[eud][tech] - conso_sum * corr_factor
            if tech not in resources:
                fec_tech_corr = fec_given_tech(tech=tech, data=data, prod_corr=prod_corr)
                # fec_tech = fec_given_tech(tech=tech, data=data, prod_corr=prod_tech_EUD[eud][tech])
            else:
                fec_tech_corr = prod_corr
                # fec_tech = prod_tech_EUD[eud][tech]
            # print('%s %s %.1f %.1f %.1f' %(eud, tech, fec_tech, fec_tech_corr, corr_factor))
            fec_eud.append([tech, fec_tech_corr])
        fec_details[eud] = pd.DataFrame(fec_eud)
        fec_tot[eud] = pd.DataFrame(fec_eud)[1].sum()
    fec_details['ELECTRICITY'] = data['ELECTRICITY'].loc['END_USES_DEMAND']
    fec_tot['ELECTRICITY'] = data['ELECTRICITY'].loc['END_USES_DEMAND']
    return fec_details, fec_tot


def compute_einv_details(cs: str, user_data: str, all_data: dict):
    """
    Compute the Einv by RESOURCES and TECHNOLOGIES, it details the breakdown by subcategories
     of RESOURCES and categories of TECHNOLOGIES.
    :param cs: case study path
    :param user_data: user_data directory
    :param all_data: the data into a dict of pd.DataFrames.
    :return: the data into pd.DataFrames
    """
    # Load Einv data
    df_einv = pd.read_csv(f"{cs}/output/einv_breakdown.csv", index_col=0)
    # Define the RESOURCES and TECHNOLOGIES lists
    resources = list(all_data['Resources'].index)
    technologies = list(all_data['Technologies'].index)
    df_inv_res = df_einv.loc[resources].copy()
    df_inv_tech = df_einv.loc[technologies].copy()
    # Get the category and subcategory indexes
    df_aux_res = pd.read_csv(user_data + "/aux_resources.csv", index_col=0)
    df_aux_tech = pd.read_csv(user_data + "/aux_technologies.csv", index_col=0)

    # 1. Compute the Einv by subcategory of resources
    res_subcat = list(df_aux_res['Subcategory'].values)
    res_subcat = list(dict.fromkeys(res_subcat))  # remove duplicate

    res_by_subcat = dict()
    for sub_cat in res_subcat:
        res_by_subcat[sub_cat] = list(df_aux_res['Subcategory'][df_aux_res['Subcategory'] == sub_cat].index)

    einv_res_by_subcat = dict()
    for sub_cat in res_by_subcat.keys():
        einv_res_by_subcat[sub_cat] = df_inv_res.loc[res_by_subcat[sub_cat]]
    df_inv_res_by_subcat = pd.DataFrame(
        data=[einv_res_by_subcat[sub_cat].sum().sum() for sub_cat in einv_res_by_subcat.keys()],
        index=einv_res_by_subcat.keys(), columns=['RESSOURCES'])  # FIXME: TYPO ?

    # 2. Compute the Einv by category of technologies
    tech_cat = list(df_aux_tech['Category'].values)
    tech_cat = list(dict.fromkeys(tech_cat))  # remove duplicate

    tech_by_cat = dict()
    for cat in tech_cat:
        tech_by_cat[cat] = list(df_aux_tech['Category'][df_aux_tech['Category'] == cat].index)

    einv_tech_by_cat = dict()
    for cat in tech_by_cat.keys():
        einv_tech_by_cat[cat] = df_inv_tech.loc[tech_by_cat[cat]]
    df_inv_tech_by_cat = pd.DataFrame(data=[einv_tech_by_cat[cat].sum().sum() for cat in einv_tech_by_cat.keys()],
                                      index=einv_tech_by_cat.keys(), columns=['TECHNOLOGIES'])

    return df_inv_res_by_subcat, df_inv_tech_by_cat


def compute_primary_energy(cs: str, user_data: str, run: str, all_data: dict):
    """
    Compute the primary energy for a given case study.
    :param cs: case study path.
    :param user_data: user_data directory
    :param run: run name.
    :param all_data: FIXME: complete
    :return: the data into pd.DataFrames.
    """
    # load year_balance.csv
    df_y_balance = pd.read_csv(f"{cs}/output/year_balance.csv", index_col=0)

    # list the resources
    resources = list(all_data['Resources'][all_data['Resources']['Category'] != 'Others'].index)
    # remove resources related to CO2
    resources.remove('CO2_EMISSIONS')

    # select primary energy from the year_balance.csv into a pd.DataFrame
    # df_temp = df_y_balance.loc[resources].sum().loc[['ELECTRICITY', 'GASOLINE', 'DIESEL', 'LFO', 'GAS', 'WOOD',
    #                                                  'WET_BIOMASS', 'COAL', 'URANIUM', 'WASTE', 'H2', 'AMMONIA',
    #                                                  'METHANOL',
    #                                                  'RES_WIND', 'RES_SOLAR', 'RES_HYDRO', 'RES_GEO']] / 1000  # TWh

    df_temp = df_y_balance.loc[resources].sum(axis=1) / 1000  # TWh
    df_primary_energy = pd.DataFrame(data=df_temp.values, index=df_temp.index, columns=['RESSOURCES'])

    # Label each resource by its subcategory: ['Other non-renewable', 'Fossil fuel', 'Biomass', 'Non-biomass']
    df_primary_energy['Subcategory'] = ''
    df_aux_res = pd.read_csv(user_data + "/aux_resources.csv", index_col=0)
    for ind in df_primary_energy.index:
        df_primary_energy['Subcategory'].loc[ind] = df_aux_res.loc[ind]['Subcategory']

    # List of the subcategories into a list
    res_subcat = list(df_primary_energy['Subcategory'].values)
    res_subcat = list(dict.fromkeys(res_subcat))  # remove duplicate

    # aggregate the primary energy by subcategory
    primary_dict = dict()
    for subcat in res_subcat:
        primary_dict[subcat] = df_primary_energy[df_primary_energy['Subcategory'] == subcat]['RESSOURCES'].sum()

    return pd.DataFrame(data=primary_dict.values(), index=primary_dict.keys(), columns=[run]), \
        df_primary_energy.sort_values(by=['Subcategory'])


# Function to compute the annual average emission factors of each resource from the outputs #
def compute_gwp_op(import_folders, out_path='STEP_2_Energy_Model'):
    # import data and model outputs
    resources = pd.read_csv(import_folders[0] + '/Resources.csv', index_col=2, header=2)
    yb = pd.read_csv(out_path + '/output/year_balance.csv', index_col=0)

    # clean df and get useful data
    yb.rename(columns=lambda x: x.strip(), inplace=True)
    yb.rename(index=lambda x: x.strip(), inplace=True)
    gwp_op_data = resources['gwp_op'].dropna()
    res_names = list(gwp_op_data.index)
    res_names_red = list(set(res_names) & set(list(yb.columns)))  # resources that are a layer
    yb2 = yb.drop(index='END_USES_DEMAND')
    tot_year = yb2.mul(yb2.gt(0)).sum()[res_names_red]

    # compute the actual resources used to produce each resource
    res_used = pd.DataFrame(0, columns=res_names_red, index=res_names)
    for r in res_names_red:
        yb_r = yb2.loc[yb2.loc[:, r] > 0, :]
        for i, j in yb_r.iterrows():
            if i in res_names:
                res_used.loc[i, r] = res_used.loc[i, r] + j[i]
            else:
                s = list(j[j < 0].index)[0]
                res_used.loc[s, r] = res_used.loc[s, r] - j[s]

    # differentiate the imported resources from the ones that are the mix
    # between the imported ones and the produced ones
    gwp_op_imp = gwp_op_data.copy()
    gwp_op_imp.rename(index=lambda x: x + '_imp', inplace=True)
    gwp_op = pd.concat([gwp_op_data.copy(), gwp_op_imp])
    res_used_imp = pd.DataFrame(0, index=res_used.index, columns=res_used.columns)
    for i, j in res_used.iteritems():
        res_used_imp.loc[i, i] = j[i]
        res_used.loc[i, i] = 0
    res_used_imp.rename(index=lambda x: x + '_imp', inplace=True)
    all_res_used = pd.concat([res_used, res_used_imp])

    # compute the gwp_op of each mix through looping over the equations
    gwp_op_new = gwp_op.copy()
    conv = 100
    count = 0
    while conv > 1e-6:
        gwp_op = gwp_op_new
        gwp_op_new = pd.concat([(all_res_used.mul(gwp_op, axis=0).sum() / tot_year).fillna(0), gwp_op_imp])
        conv = (gwp_op_new - gwp_op).abs().sum()
        count += 1

    gwp_op_final = gwp_op_new[res_names_red]

    return gwp_op_final.combine_first(gwp_op_data)
