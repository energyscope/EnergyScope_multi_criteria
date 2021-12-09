import matplotlib.pyplot as plt

import energyscope as es


def plot_pareto(case_study_path, test_case, epsilons):

    cost_opt_cost = es.get_total_cost(f"{case_study_path}/{test_case}")
    einv_opt_cost = es.get_total_einv(f"{case_study_path}/{test_case}")
    print(f"Optimal Cost {cost_opt_cost:.2f}")
    print(f"Einv at optimal cost {einv_opt_cost:.2f}")

    cost_opt_einv = es.get_total_cost(f"{case_study_path}/{test_case}_einv")
    einv_opt_einv = es.get_total_einv(f"{case_study_path}/{test_case}_einv")
    print(f"Cost at optimal einv {cost_opt_einv:.2f}")
    print(f"Optimal einv {einv_opt_einv:.2f}")
    print()

    x = [0.]
    y = [(einv_opt_cost/einv_opt_einv-1)*100]
    print(y)
    for epsilon in epsilons:
        dir = f"{case_study_path}/{test_case}_epsilon_{epsilon}"
        print(dir)
        cost = es.get_total_cost(dir)
        einv = es.get_total_einv(dir)
        print(cost, einv)
        x += [(cost/cost_opt_cost-1)*100]
        y += [(einv/einv_opt_einv-1)*100]

    # Adding CO2 extreme point
    x += [(cost_opt_einv/cost_opt_cost-1)*100]
    y += [0.]

    print([round(i, 2) for i in x])
    print([round(j, 2) for j in y])
    # plt.plot(x, y,)
    plt.plot(x, y, 'o', c='C1')
    plt.plot([x[0], x[-1]], [y[0], y[-1]], 'o', c='r')
    plt.grid()
    plt.xlabel("Deviation from cost optimal (%)")
    plt.ylabel("Deviation from Einv optimal (%)")
    # plt.title("Pareto front (Cost vs Einv)")

    plt.savefig('pareto_cost_einv.png')
    exit()

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


if __name__ == '__main__':

    case_study_path = "/home/duboisa1/Global_Grid/code/EnergyScope/case_studies"
    test_case = 'pareto/run3'
    epsilons = [0.0125, 0.025, 0.05, 0.1, 0.15]  # [e/100 for e in range(1, 13)]


    # plot_pareto(case_study_path, test_case, epsilons)

    epsilons_pairs = [(0.05, 0.1), (0.05, 0.2), (0.05, 0.3)]

    for epsilon_cost, epsilon_einv in epsilons_pairs:

        path = f"{case_study_path}/{test_case}_wind_{epsilon_cost}_{epsilon_einv}"
        print(path)
        print(es.get_asset_value(path, "f", "WIND_OFFSHORE"))
