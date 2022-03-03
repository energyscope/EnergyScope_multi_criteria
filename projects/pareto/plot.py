from typing import List

import matplotlib.pyplot as plt

import energyscope as es


def plot_pareto(case_study_path: str, test_case: str, epsilons: List[float]) -> None:

    cost_opt_cost = es.get_total_cost(f"{case_study_path}/{test_case}/cost")
    einv_opt_cost = es.get_total_einv(f"{case_study_path}/{test_case}/cost")
    print(f"Optimal Cost {cost_opt_cost:.2f}")
    print(f"Einv at optimal cost {einv_opt_cost:.2f}")

    cost_opt_einv = es.get_total_cost(f"{case_study_path}/{test_case}/einv")
    einv_opt_einv = es.get_total_einv(f"{case_study_path}/{test_case}/einv")
    print(f"Cost at optimal einv {cost_opt_einv:.2f}")
    print(f"Optimal einv {einv_opt_einv:.2f}")
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
    plt.xlabel("Deviation from cost optimal (%)")
    plt.ylabel("Deviation from Einv optimal (%)")
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


def plot_necessary_condition(case_study_path: str, test_case: str):

    techs = ["WIND_OFFSHORE", "WIND_ONSHORE", "PV"]
    # techs = ["DEC_HP_ELEC", "DEC_THHP_GAS", "DHN_HP_ELEC"]
    # techs = ['GAS']
    run_name = 'loc_res'
    epsilons = [0.003125, 0.00625, 0.0125, 0.025, 0.05, 0.1, 0.15]
    epsilons = [1/160, 1/80, 1/40, 1/20]
    epsilons_pairs = [(0.025, 0.5), (0.025, 0.4), (0.025, 0.3), (0.025, 0.2),
                      (0.05, 0.4), (0.05, 0.3), (0.05, 0.2), (0.05, 0.1),
                      (0.075, 0.3), (0.075, 0.2), (0.075, 0.1), (0.075, 0.05),
                      (0.1, 0.3), (0.1, 0.2), (0.1, 0.1), (0.1, 0.05),
                      (0.125, 0.2), (0.125, 0.1), (0.125, 0.05),
                      (0.15, 0.2), (0.15, 0.1), (0.15, 0.05),
                      (0.175, 0.1), (0.175, 0.05)]
    epsilons_pairs = [(2.5/100, 40/100), (2.5/100, 30/100), (2.5/100, 20/100),
                      (5/100, 30/100), (5/100, 20/100), (5/100, 10/100),
                      (7.5/100, 20/100), (7.5/100, 10/100)]

    # Optimums
    cost_path = f"{case_study_path}/{test_case}/cost"
    cost_opt_cost = es.get_total_cost(cost_path)
    einv_opt_cost = es.get_total_einv(cost_path)

    einv_path = f"{case_study_path}/{test_case}/einv"
    cost_opt_einv = es.get_total_cost(einv_path)
    einv_opt_einv = es.get_total_einv(einv_path)

    xs = [0.0]
    ys = [(einv_opt_cost/einv_opt_einv-1)*100]
    values = [round(sum([es.get_asset_value(cost_path, "f", tech) for tech in techs]), 3)]
    # values = [round(sum([es.get_resource_used(cost_path, tech) for tech in techs]), 3)]

    # Pareto front
    for epsilon in epsilons:
        path = f"{case_study_path}/{test_case}/cost_epsilon_{epsilon}"
        cost = es.get_total_cost(path)
        einv = es.get_total_einv(path)
        xs += [round((cost/cost_opt_cost-1)*100, 3)]
        ys += [round((einv/einv_opt_einv-1)*100, 3)]
        values += [round(sum([es.get_asset_value(path, "f", tech) for tech in techs]), 3)]
        # values += [round(sum([es.get_resource_used(path, tech) for tech in techs]), 3)]

    xs += [(cost_opt_einv/cost_opt_cost-1)*100]
    ys += [0.0]
    values += [round(sum([es.get_asset_value(einv_path, "f", tech) for tech in techs]), 3)]
    # values += [round(sum([es.get_resource_used(einv_path, tech) for tech in techs]), 3)]

    plt.xlabel("Deviation from cost optimal (%)")

    ax1 = plt.subplot()
    plt.plot(xs, ys)
    plt.ylabel("Deviation from Einv optimal (%)", color='C0')

    ax2 = ax1.twinx()
    plt.plot(xs, values, c='C1')
    plt.grid()
    plt.ylabel('Installed capacity', color='C1')

    # Limits of the epsilon optimal spaces
    for epsilon_cost, epsilon_einv in epsilons_pairs:
        path = f"{case_study_path_}/{test_case_}/{run_name}_{epsilon_cost}_{epsilon_einv}"
        values += [round(sum([es.get_asset_value(path, "f", tech) for tech in techs]), 2)]
        # values += [round(sum([es.get_resource_used(path, tech) for tech in techs]), 2)]
        xs += [epsilon_cost*100]
        ys += [epsilon_einv*100]

    print(xs)
    print(ys)
    print(list(zip(xs, ys, values)))
    plt.figure()
    plt.grid(zorder=1)
    plt.scatter(xs, ys, s=100, c=values, cmap='viridis', zorder=2)
    plt.colorbar()
    # plt.grid()
    plt.xlabel("Deviation from cost optimal (%)")
    plt.ylabel("Deviation from Einv optimal (%)")
    plt.show()
    exit()


if __name__ == '__main__':

    case_study_path_ = "/home/duboisa1/Global_Grid/code/EnergyScope_multi_criteria/case_studies"
    test_case_ = 'pareto/gwp_constraint_50000'
    epsilons_ = [1/160, 0.0125, 0.025, 0.05]  #, 0.15]  # [e/100 for e in range(1, 13)]

    # plot_pareto(case_study_path_, test_case_, epsilons_)
    plot_necessary_condition(case_study_path_, test_case_)

