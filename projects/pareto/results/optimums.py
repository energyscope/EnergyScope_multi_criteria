"""
Analysis of the optimums
"""
import pandas as pd
import yaml

import energyscope as es
from energyscope.utils import get_names


if __name__ == '__main__':

    case_study_dir = "../../../case_studies"
    test_case = "gwp_constraint_35000"
    data_dir = '../../../Data'
    user_data_dir = data_dir + "/User_data"

    objs = ['cost', 'einv', 'gwp']

    case_res = yaml.load(open("../resources.yaml", 'r'), Loader=yaml.FullLoader)

    # Get objective values of each optimum
    for obj in objs:
        path = f"{case_study_dir}/{test_case}/{obj}"
        cost = es.get_total_cost(path)
        einv = es.get_total_einv(path)
        gwp = es.get_total_gwp(path)

        print(f"At {obj} optimum:")
        print(f"COST: {cost / 1e3:.2f} B€, EINV: {einv / 1e3:.2f} TWh, GWP: {gwp:.2f} kt\n")

    # Get total endogenous and exogenous values
    for obj in objs:
        path = f"{case_study_dir}/{test_case}/{obj}"
        locals_tot = pd.Series({res: es.get_resource_used(path, res) for res in case_res['locals']}).sum()
        imports_tot = pd.Series({res: es.get_resource_used(path, res) for res in case_res['imports']}).sum()

        print(f"\nOpt {obj}")
        print(f"LOCALS {locals_tot / 1e3:.2f} TWh, IMPORTS {imports_tot / 1e3:.2f} TWh, "
              f"Total {(locals_tot + imports_tot) / 1e3:.2f} TWh")

    # Get individual endogenous and exogenous values
    locals_res_list = []
    imports_res_list = []
    for obj in objs:
        print(obj)
        path = f"{case_study_dir}/{test_case}/{obj}"
        locals_res = pd.Series({res: es.get_resource_used(path, res) for res in case_res['locals']})
        imports_res = pd.Series({res: es.get_resource_used(path, res) for res in case_res['imports']})

        locals_res_list += [(locals_res[locals_res.round() != 0] / 1e3)]
        imports_res_list += [(imports_res[imports_res.round() != 0] / 1e3)]

    locals_res_df = pd.concat(locals_res_list, axis=1).round(3)
    imports_res_df = pd.concat(imports_res_list, axis=1).round(3)
    locals_res_df.columns = objs
    imports_res_df.columns = objs
    locals_res_df.index = get_names(locals_res_df.index.to_list(), 'resources', user_data_dir)
    imports_res_df.index = get_names(imports_res_df.index.to_list(), 'resources', user_data_dir)
    print(f"LOCALS:\n{locals_res_df.sort_index()}")
    print(f"\nIMPORTS:\n{imports_res_df.sort_index()}")

