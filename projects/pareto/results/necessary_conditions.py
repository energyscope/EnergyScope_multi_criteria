"""
Analysis of the necessary conditions
"""

import yaml
import os

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

import energyscope as es

if __name__ == '__main__':

    case_study_dir = "../../../case_studies"
    test_case = "gwp_constraint_35000"
    data_dir = '../../../Data'
    user_data_dir = data_dir + "/User_data"

    obj1 = 'cost'
    obj2 = 'einv'

    fontsize = 12
    plt.rc('font', size=fontsize)
    plt.rc('axes', labelsize=fontsize)

    case_res = yaml.load(open("../resources.yaml", 'r'), Loader=yaml.FullLoader)
    endo_res = case_res['imports']

    for case in ['locals', 'imports', 'methanol-re', 'gas', 'elec-import']:
        # Get results folders
        folder_names = sorted([f for f in os.listdir(f"{case_study_dir}/{test_case}")
                               if f"{case}_{obj1}_{obj2}_" in f])
        print(folder_names)
        # Get corresponding epsilon pairs and pareto front epsilons
        # (suppose that all epsilon pairs are associated to all pareto front epsilons)
        epsilons_pairs = sorted(list(set([tuple(map(float, fd.split("_")[3:5])) for fd in folder_names])))
        epsilons_pareto = sorted(list(set([float(fd.split("_")[-1]) for fd in folder_names])))

        print(epsilons_pareto)
        print(epsilons_pairs)
        totals = pd.DataFrame(0., index=epsilons_pareto, columns=pd.MultiIndex.from_tuples(epsilons_pairs))
        endo_totals = pd.DataFrame(0., index=epsilons_pareto, columns=pd.MultiIndex.from_tuples(epsilons_pairs))

        endo_dict = dict.fromkeys(endo_res)
        for res in endo_res:
            endo_dict[res] = pd.DataFrame(0., index=epsilons_pareto, columns=pd.MultiIndex.from_tuples(epsilons_pairs))

        for epsilon1, epsilon2 in epsilons_pairs:
            for epsilon_pareto in epsilons_pareto:
                path = f"{case_study_dir}/{test_case}/{case}_{obj1}_{obj2}_{epsilon1}_{epsilon2}_{epsilon_pareto}"
                if not os.path.isdir(path):
                    print(epsilon1, epsilon2)
                    continue
                totals.loc[epsilon_pareto][(epsilon1, epsilon2)] = sum(
                    [es.get_resource_used(path, res) for res in case_res[case]]) / 1000.
                endo_totals.loc[epsilon_pareto][(epsilon1, epsilon2)] = sum(
                    [es.get_resource_used(path, res) for res in endo_res]) / 1000.
                for res in endo_res:
                    endo_dict[res].loc[epsilon_pareto][(epsilon1, epsilon2)] = es.get_resource_used(path, res)

        print(f"{case.upper()}:\n{totals.round().to_string()}\n")
        print(f"{case.upper()}:\n{endo_totals.round().to_string()}\n")
        necessary_conditions = totals.min().round().unstack(level=1)
        min_idx = totals.idxmin()
        min_idx_flat = [(id1, id2, min_idx.values[i]) for i, (id1, id2) in enumerate(min_idx.index)]
        print(f"{case.upper()}:\n{necessary_conditions.to_string()}\n")
        necessary_conditions.index = [c*100 for c in necessary_conditions.index]
        necessary_conditions.columns = [c*100 for c in necessary_conditions.columns]
        necessary_conditions.to_csv('test.csv')

        plt.figure()
        ax = plt.subplot()
        vmax = 200 if case == 'locals' or case == 'imports' else 40
        cmap = 'viridis_r' if case == 'locals' or case == 'imports' else 'Blues'
        plt.imshow(necessary_conditions, cmap=cmap, vmin=0, vmax=vmax)
        plt.colorbar(label='TWh')
        plt.xticks(range(len(necessary_conditions)), [int(c) for c in necessary_conditions.columns])
        plt.yticks(range(len(necessary_conditions)), [int(i) for i in necessary_conditions.index])
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")
        ax.set_ylabel(r"Deviation in $C_{tot}$ (%)")
        ax.set_xlabel(r"Deviation in $E_{in, tot}$ (%)")

        for (j, i), label in np.ndenumerate(necessary_conditions):
            color = 'w' if case == 'imports' else 'k'
            label = int(label) if not np.isnan(label) else label
            ax.text(i, j, label, ha='center', va='center', c=color)

        if case == 'locals' or case == 'imports':
            plt.title(case)

        plt.tight_layout()
        plt.savefig(f"necessary_conditions_{case}.pdf")

    plt.show()
