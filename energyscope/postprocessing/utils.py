import pandas as pd


def get_total_cost(output_path):
    costs = pd.read_csv(f"{output_path}/output/cost_breakdown.csv", index_col=0)
    return costs.sum().sum()


def get_total_gwp(output_path):
    gwp = pd.read_csv(f"{output_path}/output/gwp_breakdown.csv", index_col=0)
    return gwp.sum().sum()


def get_total_einv(output_path):
    einv = pd.read_csv(f"{output_path}/output/einv_breakdown.csv", index_col=0)
    return einv.sum().sum()


def get_asset_value(output_path: str, param: str, tech: str):
    assets = pd.read_csv(f"{output_path}/output/assets.csv", index_col=0)
    assets.columns = [c.strip() for c in assets.columns]
    return assets.loc[tech, param]


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
