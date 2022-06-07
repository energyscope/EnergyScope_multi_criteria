import os.path
from typing import List

from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
from matplotlib import cm, colors
import numpy as np

import energyscope as es



if __name__ == '__main__':

    case_study_path_ = "/home/duboisa1/Global_Grid/code/EnergyScope_multi_criteria/case_studies"
    test_case_ = 'three_objectives'

    # --- Optimums --- #

    cost_at_opt_cost = es.get_total_cost(f"{case_study_path_}/{test_case_}/cost")
    einv_at_opt_cost = es.get_total_einv(f"{case_study_path_}/{test_case_}/cost")
    gwp_at_opt_cost = es.get_total_gwp(f"{case_study_path_}/{test_case_}/cost")

    cost_at_opt_einv = es.get_total_cost(f"{case_study_path_}/{test_case_}/einv")
    einv_at_opt_einv = es.get_total_einv(f"{case_study_path_}/{test_case_}/einv")
    gwp_at_opt_einv = es.get_total_gwp(f"{case_study_path_}/{test_case_}/einv")

    cost_at_opt_gwp = es.get_total_cost(f"{case_study_path_}/{test_case_}/gwp")
    einv_at_opt_gwp = es.get_total_einv(f"{case_study_path_}/{test_case_}/gwp")
    gwp_at_opt_gwp = es.get_total_gwp(f"{case_study_path_}/{test_case_}/gwp")

    print(f"Optimal Cost {cost_at_opt_cost:.2f}, {(cost_at_opt_cost/cost_at_opt_cost-1)*100:.2f}")
    print(f"Einv at optimal cost {einv_at_opt_cost:.2f}, {(einv_at_opt_cost/einv_at_opt_einv-1)*100:.2f}")
    print(f"GWP at optimal cost {gwp_at_opt_cost:.2f}, {(gwp_at_opt_cost/gwp_at_opt_gwp-1)*100:.2f}")

    print(f"Cost at optimal einv {cost_at_opt_einv:.2f}, {(cost_at_opt_einv/cost_at_opt_cost-1)*100:.2f}")
    print(f"Optimal einv {einv_at_opt_einv:.2f}, {(einv_at_opt_einv/einv_at_opt_einv-1)*100:.2f}")
    print(f"GWP at optimal einv {gwp_at_opt_einv:.2f}, {(gwp_at_opt_einv/gwp_at_opt_gwp-1)*100:.2f}")

    print(f"Cost at optimal GWP {cost_at_opt_gwp:.2f}, {(cost_at_opt_gwp/cost_at_opt_cost-1)*100:.2f}")
    print(f"Einv at optimal GWP {einv_at_opt_gwp:.2f}, {(einv_at_opt_gwp/einv_at_opt_einv-1)*100:.2f}")
    print(f"Optimal GWP {gwp_at_opt_gwp:.2f}, {(gwp_at_opt_gwp/gwp_at_opt_gwp-1)*100:.2f}")

    # --- Pareto fronts --- #
    fig = plt.figure()  # x = cost, y = einv, z = gwp
    ax = plt.axes(projection='3d')
    ax.set_xlabel("Deviation Cost")
    ax.set_ylabel("Deviation Einv")
    ax.set_zlabel("Deviation GWP")
    ax.set_xlim([-0.01, 250])
    ax.set_ylim([-0.01, 250])
    ax.set_zlim([-0.01, 250])

    # Cost vs Einv
    dev_cost_vs_einv = [0., 0.003125, 0.00625, 0.0125, 0.025, 0.05, 0.1, 0.15, round(cost_at_opt_einv/cost_at_opt_cost-1, 2)]
    dev_einv_vs_cost = [round(einv_at_opt_cost/einv_at_opt_einv-1, 2)]
    for epsilon in dev_cost_vs_einv[1:-1]:
        dir_path = f"{case_study_path_}/{test_case_}/min_einv_cost_epsilon_{epsilon}"
        dev_einv_vs_cost += [round(es.get_total_einv(dir_path)/einv_at_opt_einv-1, 3)]
    dev_einv_vs_cost += [0.]
    dev_cost_vs_einv = [x*100 for x in dev_cost_vs_einv]
    dev_einv_vs_cost = [x*100 for x in dev_einv_vs_cost]
    print(list(zip(dev_cost_vs_einv, dev_einv_vs_cost)))
    ax.scatter(dev_cost_vs_einv, dev_einv_vs_cost, [0]*len(dev_cost_vs_einv))

    # Cost vs GWP
    dev_cost_vs_gwp = [0., 0.0125, 0.025, 0.05, 0.1, 0.15, 0.2, 0.25, round(cost_at_opt_gwp/cost_at_opt_cost-1, 2)]
    dev_gwp_vs_cost = [round(gwp_at_opt_cost/gwp_at_opt_gwp-1, 2)]
    for epsilon in dev_cost_vs_gwp[1:-1]:
        dir_path = f"{case_study_path_}/{test_case_}/min_gwp_cost_epsilon_{epsilon}"
        dev_gwp_vs_cost += [round(es.get_total_gwp(dir_path)/gwp_at_opt_gwp-1, 3)]
    dev_gwp_vs_cost += [0.]
    dev_cost_vs_gwp = [x*100 for x in dev_cost_vs_gwp]
    dev_gwp_vs_cost = [x*100 for x in dev_gwp_vs_cost]
    print(list(zip(dev_cost_vs_gwp, dev_gwp_vs_cost)))
    ax.scatter(dev_cost_vs_gwp, [0]*len(dev_cost_vs_gwp), dev_gwp_vs_cost)

    # Einv vs GWP
    dev_einv_vs_gwp = [0, 0.05, 0.1, 0.25, 0.5, 0.75, 1.00, 1.25, round(einv_at_opt_gwp/einv_at_opt_einv-1, 2)]
    dev_gwp_vs_einv = [round(gwp_at_opt_einv/gwp_at_opt_gwp-1, 2)]
    for epsilon in dev_einv_vs_gwp[1:-1]:
        dir_path = f"{case_study_path_}/{test_case_}/min_gwp_einv_epsilon_{epsilon}"
        dev_gwp_vs_einv += [round(es.get_total_gwp(dir_path)/gwp_at_opt_gwp-1, 3)]
    dev_gwp_vs_einv += [0.]
    dev_einv_vs_gwp = [x*100 for x in dev_einv_vs_gwp]
    dev_gwp_vs_einv = [x*100 for x in dev_gwp_vs_einv]
    print(list(zip(dev_einv_vs_gwp, dev_gwp_vs_einv)))
    ax.scatter([0]*len(dev_einv_vs_gwp), dev_einv_vs_gwp, dev_gwp_vs_einv)

    # 2d plots
    fig2, axes = plt.subplots(1, 3, figsize=(16, 5))
    axes[0].grid()
    axes[0].scatter(dev_cost_vs_einv, dev_einv_vs_cost, c='C0', s=100)
    axes[0].set_xlabel("Deviation from Cost optimum (%)")
    axes[0].set_ylabel("Deviation from Einv optimum (%)")
    # axes[1, 1].set_xlim([-0.1, 2.5])
    # axes[1, 1].set_ylim([-0.1, 2.5])
    axes[1].grid()
    axes[1].scatter(dev_cost_vs_gwp, dev_gwp_vs_cost, c='C1', s=100)
    axes[1].set_xlabel("Deviation from Cost optimum (%)")
    axes[1].set_ylabel("Deviation from GWP optimum (%)")
    # axes[0, 1].set_xlim([-0.1, 2.5])
    # axes[0, 1].set_ylim([-0.1, 2.5])
    axes[2].grid()
    axes[2].scatter(dev_einv_vs_gwp, dev_gwp_vs_einv, c='C2', s=100)
    axes[2].set_xlabel("Deviation from Einv optimum (%)")
    axes[2].set_ylabel("Deviation from GWP optimum (%)")
    # axes[0, 0].set_xlim([-0.1, 2.5])
    # axes[0, 0].set_ylim([-0.1, 2.5])
    # fig2.tight_layout()
    plt.savefig("pareto_fronts_3_objectives.png", bbox_inches='tight')

    # plt.show()

    # --- Necessary conditions --- #

    res_to_minimize = {'locals': ["WOOD", "WET_BIOMASS", "WASTE", "RES_WIND", "RES_SOLAR", "RES_HYDRO", "RES_GEO"],
                       'imports': ["ELECTRICITY", "METHANOL", "AMMONIA", "H2", "COAL", "GAS", "LFO", "DIESEL",
                                   "GASOLINE", "BIODIESEL", "BIOETHANOL", "H2_RE", "GAS_RE", "AMMONIA_RE",
                                   "METHANOL_RE"]}
    run_name = 'imports'
    resources = res_to_minimize[run_name]
    # Pairs (dev cost, dev einv, dev gwp)
    epsilons_tuples = [
        (5/100, 20/100, 100/100), (5/100, 20/100, 200/100),
        (5/100, 40/100, 100/100), (5/100, 40/100, 200/100),
        (10/100, 20/100, 100/100), (10/100, 20/100, 200/100),
        (10/100, 40/100, 100/100), (10/100, 40/100, 200/100)
    ]

    # Values at optimums
    objs = ['cost', 'einv', 'gwp']
    for obj in objs:
        path = f"{case_study_path_}/{test_case_}/{obj}"
        value = round(sum([es.get_resource_used(path, res) for res in resources]) / 1000., 1)
        print(f"Value at {obj} optimum: {value}")

    invariants_values = []
    for epsilon_cost, epsilon_einv, epsilon_gwp in epsilons_tuples:
        path = f"{case_study_path_}/{test_case_}/{run_name}_{epsilon_cost}_{epsilon_einv}_{epsilon_gwp}"
        if not os.path.isdir(path):
            continue
        invariants_values += [round(sum([es.get_resource_used(path, res) for res in resources]) / 1000., 1)]

    print(invariants_values)
