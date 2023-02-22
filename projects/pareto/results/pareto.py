"""
Analysis of the Pareto front
"""

import os

import pandas as pd
import yaml
from matplotlib import pyplot as plt

import energyscope as es
from energyscope.utils import get_names, get_colors

obj_functions = {
    "cost": es.get_total_cost,
    "einv": es.get_total_einv,
    "gwp": es.get_total_gwp
}


def get_folder_names(min_obj, constr_obj):

    folder_names = sorted([f for f in os.listdir(f"{case_study_dir}/{test_case}")
                           if f"min_{min_obj}_{constr_obj}_epsilon_" in f])
    return [constr_obj] + folder_names + [min_obj]


if __name__ == '__main__':

    case_study_dir = "../../../case_studies"
    test_case = "gwp_constraint_35000"
    data_dir = '../../../Data'
    user_data_dir = data_dir + "/User_data"

    fontsize = 12
    plt.rc('font', size=fontsize)
    plt.rc('axes', labelsize=fontsize)

    objs = ['cost', 'einv', 'gwp']

    case_res = yaml.load(open("../resources.yaml", 'r'), Loader=yaml.FullLoader)

    # Get Pareto front between two objectives
    minimised_obj = 'einv'  # einv or gwp
    constrained_obj = 'cost'  # cost or einv
    folder_names_ = get_folder_names(minimised_obj, constrained_obj)

    # Compute pareto front
    minimised_obj_values = [round(obj_functions[minimised_obj](f"{case_study_dir}/{test_case}/{fd}"))
                            for fd in folder_names_]
    constr_obj_values = [round(obj_functions[constrained_obj](f"{case_study_dir}/{test_case}/{fd}"))
                         for fd in folder_names_]

    print(constr_obj_values, minimised_obj_values)
    constr_obj_perc = [round((v/constr_obj_values[0]-1)*100, 3) for v in constr_obj_values]
    minimised_obj_perc = [round((v/minimised_obj_values[-1]-1)*100, 3) for v in minimised_obj_values]
    print(constr_obj_perc, minimised_obj_perc)
    xtickslabels = [f'{v/1000:.1f}\n({c:.1f}%)' for v, c in zip(constr_obj_values, constr_obj_perc)]
    ytickslabels = [f'{v/1000:.1f}\n({c:.1f}%)' for v, c in zip(minimised_obj_values, minimised_obj_perc)]
    print(xtickslabels)
    print(ytickslabels)
    plt.scatter(constr_obj_values, minimised_obj_values)
    plt.plot(constr_obj_values, minimised_obj_values, '--', alpha=0.5)
    xindices = [0, 3, 4, 5, 7]
    constr_obj_values = [constr_obj_values[i] for i in xindices]
    xtickslabels_reduced = [xtickslabels[i] for i in xindices]
    yindices = [0, 1, 2, 3, 4, 7]
    minimised_obj_values = [minimised_obj_values[i] for i in yindices]
    ytickslabels_reduced = [ytickslabels[i] for i in yindices]
    plt.xticks(ticks=constr_obj_values, labels=xtickslabels_reduced)
    plt.yticks(ticks=minimised_obj_values, labels=ytickslabels_reduced)
    plt.xlabel(r"$C_{tot}$ (B€)")
    plt.ylabel(r"$E_{in, tot}$ (TWh)")
    plt.tight_layout()
    plt.savefig('pareto_front.pdf')
    # plt.show()

    # Get energy sources for different Pareto points
    xtickslabels = [f'{round(c, 2)}' for c in constr_obj_perc]
    ytickslabels = [f'{round(c, 2)}' for c in minimised_obj_perc]
    for case in ['locals', 'imports']:
        res_list = []
        for fd in folder_names_:
            path = f"{case_study_dir}/{test_case}/{fd}"
            res_ds = pd.Series({res: es.get_resource_used(path, res) for res in case_res[case]})

            res_list += [(res_ds[res_ds.round() != 0] / 1e3)]

        res_df = pd.concat(res_list, axis=1).round(3)
        res_df.columns = [f.split("_")[-1] for f in folder_names_]
        old_index = res_df.index
        res_df.index = get_names(res_df.index.to_list(), 'resources', user_data_dir)
        new_index = res_df.index
        res_df = res_df.sort_index()
        sorted_new_index, sorted_old_index = zip(*sorted(list(zip(new_index, old_index))))

        res_df = res_df[res_df.sum(axis=1).round() != 0]
        colors = get_colors(list(sorted_old_index), 'resources', user_data_dir)
        legend_labels = sorted_new_index
        _, ax = plt.subplots(1)
        res_df.T.plot(ax=ax, kind='bar', stacked=True, color=colors.values)
        ax.legend(labels=legend_labels, bbox_to_anchor=(1, 1), loc="upper left")
        ax.set_ylabel("TWh")
        ax.set_xlabel(r"Deviation from $C_{tot}$ (%)")
        ax.set_xticklabels(xtickslabels, rotation=0)
        plt.tight_layout()

        res_df.loc['Total'] = res_df.sum()
        print(f"{case.upper()}:\n{res_df.to_string()}")

        plt.savefig(f"pareto_{case}_bar.pdf")

    # plt.show()
