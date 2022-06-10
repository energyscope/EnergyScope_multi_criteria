import os.path
from typing import List

import matplotlib.pyplot as plt
from matplotlib import cm, colors
import numpy as np

import energyscope as es


def plot_multi_pareto_not_normalized(case_study_path: str, test_cases: List[str], epsilons: List[float]) -> None:

    plt.figure()
    plt.grid()
    plt.xlabel("COST (Beuro)")
    plt.ylabel("EINV (TWh)")

    cmap = cm.get_cmap('Spectral')

    for i, test_case in enumerate(test_cases):
        cost_opt_cost = es.get_total_cost(f"{case_study_path}/{test_case}/cost")
        einv_opt_cost = es.get_total_einv(f"{case_study_path}/{test_case}/cost")

        cost_opt_einv = es.get_total_cost(f"{case_study_path}/{test_case}/einv")
        einv_opt_einv = es.get_total_einv(f"{case_study_path}/{test_case}/einv")

        x_not_norm = [cost_opt_cost]
        y_not_norm = [einv_opt_cost]
        for epsilon in epsilons:
            dir_name = f"{case_study_path}/{test_case}/cost_epsilon_{epsilon}"
            if os.path.isdir(dir_name):
                cost = es.get_total_cost(dir_name)
                einv = es.get_total_einv(dir_name)
                x_not_norm += [cost]
                y_not_norm += [einv]

        # Adding CO2 extreme point
        x_not_norm += [cost_opt_einv]
        y_not_norm += [einv_opt_einv]
        x_not_norm = [i/1000. for i in x_not_norm]
        y_not_norm = [i/1000. for i in y_not_norm]

        plt.plot(x_not_norm, y_not_norm, c=cmap(1-i/5), label=test_case)
        # Optimums
        plt.scatter(x_not_norm[0], y_not_norm[0], c='k', marker='x', zorder=5)
        plt.scatter(x_not_norm[-1], y_not_norm[-1], c='k', marker='o', zorder=5)
        if i == len(test_cases)-1:
            plt.scatter(x_not_norm[0], y_not_norm[0], c='k', marker='x', zorder=5, label='EINV optimums')
            plt.scatter(x_not_norm[-1], y_not_norm[-1], c='k', marker='o', zorder=5, label='COST optimums')

    # plt.legend()
    plt.savefig("pareto_front_einv_cost.png")
    plt.show()


def plot_multi_pareto(case_study_path: str, test_cases: List[str], epsilons: List[float]) -> None:

    plt.figure()
    plt.grid()
    plt.xlabel(r"Deviation from COST optimal [$f_{COST}/f^*_{COST}-1$] (%)")
    plt.ylabel("Deviation from EINV optimal\n"
               r"[$f_{EINV}/f^*_{EINV}-1$] (%)")
    cmap = cm.get_cmap('Spectral')

    for i, test_case in enumerate(test_cases):
        cost_opt_cost = es.get_total_cost(f"{case_study_path}/{test_case}/cost")
        einv_opt_cost = es.get_total_einv(f"{case_study_path}/{test_case}/cost")

        cost_opt_einv = es.get_total_cost(f"{case_study_path}/{test_case}/einv")
        einv_opt_einv = es.get_total_einv(f"{case_study_path}/{test_case}/einv")

        x = [0.]
        y = [(einv_opt_cost/einv_opt_einv-1)*100]
        for epsilon in epsilons:
            dir_name = f"{case_study_path}/{test_case}/cost_epsilon_{epsilon}"
            if os.path.isdir(dir_name):
                cost = es.get_total_cost(dir_name)
                einv = es.get_total_einv(dir_name)
                x += [(cost/cost_opt_cost-1)*100]
                y += [(einv/einv_opt_einv-1)*100]

        # Adding CO2 extreme point
        x += [(cost_opt_einv/cost_opt_cost-1)*100]
        y += [0.]

        plt.plot(x, y, c=cmap(1-i/5), label=r"GWP $\leq$ "+ f"{test_case.split('_')[-1]}")
        # Optimums
        plt.scatter(x[0], y[0], c='k', marker='x', zorder=5)
        plt.scatter(x[-1], y[-1], c='k', marker='o', zorder=5)
        if i == len(test_cases)-1:
            plt.scatter(x[0], y[0], c='k', marker='x', zorder=5, label='COST optimums')
            plt.scatter(x[-1], y[-1], c='k', marker='o', zorder=5, label='EINV optimums')

    plt.legend()
    plt.savefig("pareto_front_norm_einv_cost.png")
    plt.show()


def plot_pareto(case_study_path: str, test_case: str, epsilons: List[float]) -> None:

    cost_opt_cost = es.get_total_cost(f"{case_study_path}/{test_case}/cost")
    einv_opt_cost = es.get_total_einv(f"{case_study_path}/{test_case}/cost")
    print(f"Optimal COST {cost_opt_cost:.2f}")
    print(f"EINV at optimal COST {einv_opt_cost:.2f}")

    cost_opt_einv = es.get_total_cost(f"{case_study_path}/{test_case}/einv")
    einv_opt_einv = es.get_total_einv(f"{case_study_path}/{test_case}/einv")
    print(f"COST at optimal EINV {cost_opt_einv:.2f}")
    print(f"Optimal EINV {einv_opt_einv:.2f}")
    print()

    x = [0.]
    y = [(einv_opt_cost/einv_opt_einv-1)*100]
    print(y)
    for epsilon in epsilons:
        dir_name = f"{case_study_path}/{test_case}/cost_epsilon_{epsilon}"
        print(dir_name)
        cost = es.get_total_cost(dir_name)
        einv = es.get_total_einv(dir_name)
        print(cost, einv)
        x += [(cost/cost_opt_cost-1)*100]
        y += [(einv/einv_opt_einv-1)*100]

    # Adding CO2 extreme point
    x += [(cost_opt_einv/cost_opt_cost-1)*100]
    y += [0.]

    print([round(i, 2) for i in x])
    print([round(j, 2) for j in y])
    # plt.plot(x, y,)
    fig = plt.plot(x, y, 'o', c='C1')
    plt.plot([x[0], x[-1]], [y[0], y[-1]], 'o', c='r')
    plt.grid()
    plt.xlabel("Deviation from COST optimal (%)")
    plt.ylabel("Deviation from EINV optimal (%)")
    # plt.title("Pareto front (Cost vs Einv)")

    # plt.savefig('pareto_cost_einv.png')

    plot_suboptimal_space = False
    if plot_suboptimal_space:

        plt.grid(False)
        x_fill = [x[0]] + x + [100, 100, x[0]]
        y_fill = [100] + y + [y[-1], 100, 100]
        plt.fill(x_fill, y_fill, c='grey', alpha=0.5)
        plt.xlim([-1, x[-1]*1.1])
        plt.ylim([-5, y[0]*1.1])

        plt.savefig('pareto_cost_einv_space.png')

        x_fill = x[1:5] + [x[4], x[1]]
        y_fill = y[1:5] + [y[1], y[1]]
        plt.fill(x_fill, y_fill, c='green', alpha=0.5)
        # x_fill = x[1:5] + [x[4], 0, 0, x[1]]
        # y_fill = y[1:5] + [0, 0, y[1], y[1]]
        # plt.fill(x_fill, y_fill, c='red', alpha=0.5)
        plt.xlim([-1, x[-1]*1.1])
        plt.ylim([-5, y[0]*1.1])

        plt.savefig('pareto_cost_einv_space_non_empty.png')

    plt.show()


def plot_necessary_condition(case_study_path: str, test_case: str,
                             run_name: str, techs: List[str],
                             epsilons: List, epsilons_pairs: List):

    # Optimums
    cost_path = f"{case_study_path}/{test_case}/cost"
    cost_opt_cost = es.get_total_cost(cost_path)
    einv_opt_cost = es.get_total_einv(cost_path)

    einv_path = f"{case_study_path}/{test_case}/einv"
    cost_opt_einv = es.get_total_cost(einv_path)
    einv_opt_einv = es.get_total_einv(einv_path)

    pareto_xs = [0.0]
    pareto_ys = [(einv_opt_cost/einv_opt_einv-1)*100]
    pareto_values = [round(sum([es.get_asset_value(cost_path, "f", tech) for tech in techs]), 3)]
    # values = [round(sum([es.get_resource_used(cost_path, tech) for tech in techs]), 3)]

    # Pareto front
    for epsilon in epsilons:
        path = f"{case_study_path}/{test_case}/cost_epsilon_{epsilon}"
        cost = es.get_total_cost(path)
        einv = es.get_total_einv(path)
        pareto_xs += [round((cost/cost_opt_cost-1)*100, 3)]
        pareto_ys += [round((einv/einv_opt_einv-1)*100, 3)]
        pareto_values += [round(sum([es.get_asset_value(path, "f", tech) for tech in techs]), 3)]
        # values += [round(sum([es.get_resource_used(path, tech) for tech in techs]), 3)]

    pareto_xs += [(cost_opt_einv/cost_opt_cost-1)*100]
    pareto_ys += [0.0]
    pareto_values += [round(sum([es.get_asset_value(einv_path, "f", tech) for tech in techs]), 3)]
    # values += [round(sum([es.get_resource_used(einv_path, tech) for tech in techs]), 3)]

    if 0:
        plt.xlabel("Deviation from cost optimal (%)")

        ax1 = plt.subplot()
        plt.plot(xs, ys)
        plt.ylabel("Deviation from Einv optimal (%)", color='C0')

        ax2 = ax1.twinx()
        plt.plot(xs, values, c='C1')
        plt.grid()
        plt.ylabel('Installed capacity', color='C1')

    # Limits of the epsilon optimal spaces
    invariants_xs = []
    invariants_ys = []
    invariants_values = []
    for epsilon_cost, epsilon_einv in epsilons_pairs:
        path = f"{case_study_path_}/{test_case_}/{run_name}_{epsilon_cost}_{epsilon_einv}"
        invariants_values += [round(sum([es.get_asset_value(path, "f", tech) for tech in techs]), 2)]
        # values += [round(sum([es.get_resource_used(path, tech) for tech in techs]), 2)]
        invariants_xs += [epsilon_cost*100]
        invariants_ys += [epsilon_einv*100]

    print(invariants_values)
    plt.figure()
    plt.grid(zorder=1)

    # Plot pareto
    plt.plot(pareto_xs, pareto_ys)

    cmap = cm.get_cmap('viridis')
    scalar_map = cm.ScalarMappable(norm=colors.Normalize(0, 50), cmap=cmap)
    cbar = plt.colorbar(scalar_map)
    plt.scatter(invariants_xs, invariants_ys, s=100, c=invariants_values, zorder=2, norm=colors.Normalize(0, 50))
    # plt.grid()
    plt.xlabel("Deviation from cost optimal (%)")
    plt.ylabel("Deviation from Einv optimal (%)")
    plt.xlim([-0.5, 10])
    plt.ylim([-0.5, 45])


if __name__ == '__main__':

    case_study_path_ = "/home/duboisa1/Global_Grid/code/EnergyScope_multi_criteria/case_studies"
    test_case_ = 'gwp_constraint_10000'
    if 0:
        epsilons_ = [1/160, 1/80, 1/40, 1/20, 1/10]  # , 0.15]  # [e/100 for e in range(1, 13)]
        # plot_pareto(case_study_path_, test_case_, epsilons_)

    if 0:

        case_techs = {"loc_res": ["WIND_OFFSHORE", "WIND_ONSHORE", "PV"],
                      "hps": ["DEC_HP_ELEC", "DEC_THHP_GAS", "DHN_HP_ELEC"]}
        run_name_ = 'hps'
        techs_ = case_techs[run_name_]
        epsilons_ = [0.003125, 0.00625, 0.0125, 0.025, 0.05, 0.1, 0.15]
        epsilons_ = [1/160, 1/80, 1/40, 1/20]
        epsilons_pairs_ = [(0.025, 0.5), (0.025, 0.4), (0.025, 0.3), (0.025, 0.2),
                           (0.05, 0.4), (0.05, 0.3), (0.05, 0.2), (0.05, 0.1),
                           (0.075, 0.3), (0.075, 0.2), (0.075, 0.1), (0.075, 0.05),
                           (0.1, 0.3), (0.1, 0.2), (0.1, 0.1), (0.1, 0.05),
                           (0.125, 0.2), (0.125, 0.1), (0.125, 0.05),
                           (0.15, 0.2), (0.15, 0.1), (0.15, 0.05),
                           (0.175, 0.1), (0.175, 0.05)]
        epsilons_pairs_ = [(2.5/100, 40/100), (2.5/100, 30/100), (2.5/100, 20/100),
                           (5/100, 30/100), (5/100, 20/100),
                           (7.5/100, 20/100), (7.5/100, 10/100)]

        test_case_ = 'gwp_constraint_10000'
        plot_necessary_condition(case_study_path_, test_case_, run_name_, techs_, epsilons_, epsilons_pairs_)
        test_case_ = 'gwp_constraint_30000'
        plot_necessary_condition(case_study_path_, test_case_, run_name_, techs_, epsilons_, epsilons_pairs_)
        test_case_ = 'gwp_constraint_inf'
        plot_necessary_condition(case_study_path_, test_case_, run_name_, techs_, epsilons_, epsilons_pairs_)
        plt.show()

    if 1:
        case_study_path_ = "/home/duboisa1/Global_Grid/code/EnergyScope_multi_criteria/case_studies"

        test_cases_ = ['gwp_constraint_10000', 'gwp_constraint_20000', 'gwp_constraint_30000',
                       'gwp_constraint_40000', 'gwp_constraint_50000']

        epsilons_ = [1 / 160, 1 / 80, 1 / 40, 1 / 20, 1 / 10]

        plot_multi_pareto(case_study_path_, test_cases_, epsilons_)
        plot_multi_pareto_not_normalized(case_study_path_, test_cases_, epsilons_)
