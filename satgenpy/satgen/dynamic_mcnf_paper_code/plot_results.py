import random
import numpy as np
import time
import pickle
import matplotlib.pyplot as plt
import scipy.stats


def mean_confidence_interval_bootstrap(data, confidence=0.95, nb_iterations=1000):
    # Compute the mean and confidence interval of the the input data array-like using a bootstrap method.

    data = 1.0 * np.array(data)
    size = len(data)
    mean = np.mean(data)

    mean_list =[]
    for i in range(nb_iterations):
        sample = np.random.choice(data, size=size, replace=True)
        mean_list.append(np.mean(sample))

    mean_list.sort()
    upper_confidence_interval_bound = mean_list[int(nb_iterations * confidence + 0.5)]
    lower_confidence_interval_bound = mean_list[int(nb_iterations * (1 - confidence) + 0.5)]

    return mean, lower_confidence_interval_bound, upper_confidence_interval_bound


def plot_results(abscisse, results, algorithm_list, colors, formating, title, x_log=True, y_log=True, interval=True, x_label="Nb_nodes", y_label="Performance", legend_position="upper left"):
    # Creates one figure with all its parameters

    figure = plt.figure()
    plt.rcParams.update({'font.size': 13})
    if x_log : plt.xscale("log")
    if y_log :
        # plt.yscale("log")
        plt.yscale("symlog", linthresh=10**-5)
    ax = figure.gca()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    # plt.xticks([30, 50, 100, 200, 400], [30, 50, 100, 200, 400])
    # plt.xticks([10, 20, 30, 50, 100, 200, 400], [10, 20, 30, 50, 100, 200, 400])
    # plt.xticks([7, 20, 50, 100], ["$7~x~10^0$", "$2~x~10^1$", "$5~x~10^1$", "$10^2$"])
    plt.xticks([20, 50, 100], ["$2~x~10^1$", "$5~x~10^1$", "$10^2$"])

    for algorithm_name in algorithm_list:
        if interval:
            plt.plot(abscisse, results[algorithm_name][0], formating[algorithm_name], label=algorithm_name, color=colors[algorithm_name]) # print the main curve
            plt.fill_between(abscisse, results[algorithm_name][1], results[algorithm_name][2], alpha=0.25, facecolor=colors[algorithm_name], edgecolor=colors[algorithm_name]) # print the intervals around the main curve
            if legend_position is not None:
                ax.legend(loc=legend_position, framealpha=0.3)

        else:
            plt.plot(abscisse, results[algorithm_name], label=algorithm_name, color=colors[algorithm_name])
            if legend_position is not None:
                ax.legend(loc=legend_position, framealpha=0.3)

    return figure


def plot_dataset(global_path, dataset_name, algorithm_list=None, x_label="Nb nodes", legend_position="upper left"):
    # This function reads the results of a dataset, aggregates the results of instances with the same parameters and calls the plotting function

    # Opening the result file
    result_file = open(global_path + "/dynamic_mcnf_paper_code/instance_files_dynamic/" + dataset_name + "/result_file.p", "rb" )
    result_dict = pickle.load(result_file)
    result_file.close()

    if algorithm_list is None:
        algorithm_list = list(result_dict.keys())

    # Color for each algorithm
    colors = {"SRR arc node" : '#1f77b4', "SRR arc path" : '#ff7f0e', "SRR restricted" : '#ff7f0e',
                "B&B restricted medium" : '#2ca02c', 'Partial B&B restricted' : '#2ca02c', "SRR path-combination" : '#d62728',
                "SRR path-combination restricted" : '#d62728', 'SRR arc path no penalization' : '#ff7f0e', 'B&B restricted short' : '#2ca02c',
                'B&B restricted long' : '#2ca02c', 'SRR path-combination no penalization' : '#d62728', 'SRR path-combination timestep' : '#9467bd',
                'SRR arc node no penalization' : '#1f77b4', 'SRR path-combination commodity' : '#eeee00'}

    # Line style for each algorithm
    formating = {"SRR arc node" : '-', "SRR arc path" : '-', "SRR restricted" : '-s',
                "B&B restricted medium" : '-', 'Partial B&B restricted' : '-o', "SRR path-combination" : '-',
                "SRR path-combination restricted" : '-s', 'SRR arc path no penalization' : '-o', 'B&B restricted short' : '-s',
                'B&B restricted long' : '-o', 'SRR path-combination no penalization' : '-o', 'SRR path-combination timestep' : '-',
                 'SRR arc node no penalization' : '-o', 'SRR path-combination commodity' : '-'}

    results_performance = {algorithm_name : ([], [], []) for algorithm_name in result_dict}
    results_compututing_time = {algorithm_name : ([], [], []) for algorithm_name in result_dict}
    results_overflow_ratio = {algorithm_name : ([], [], []) for algorithm_name in result_dict}

    for algorithm_name in algorithm_list:
        temp_dict = {}
        for instance_name in result_dict[algorithm_name]:
            # size = int(instance_name.split('_')[2]) # use for graph_scaling_dataset
            size = int(instance_name.split('_')[1]) # use for graph_scaling_dataset_random and commodity_scaling_dataset
            if size not in temp_dict:
                temp_dict[size] = []
            temp_dict[size].extend(result_dict[algorithm_name][instance_name])

        for size in sorted(list(temp_dict.keys())):
            results_list = [res if res[0] is not None else (0, 0, 10, 10**5, 10, 10**4) for res in temp_dict[size]]

            _, _, performance_list, _, overflow_ratio_list, computing_time_list = zip(*results_list)
            overflow_ratio_list = [x for x in overflow_ratio_list]
            performance_list = [x - 1 for x in performance_list]

            # Aggregation of the performance : mean and bound of the confidence interval
            performance_mean, performance_low, performance_up = mean_confidence_interval_bootstrap(list(performance_list))
            results_performance[algorithm_name][0].append(performance_mean)
            results_performance[algorithm_name][1].append(performance_low) # prevent bad plotting in log scales
            results_performance[algorithm_name][2].append(performance_up)

            # Aggregation of the computing time : mean and bound of the confidence interval
            computing_time_mean, computing_time_low, computing_time_up = mean_confidence_interval_bootstrap(list(computing_time_list))
            results_compututing_time[algorithm_name][0].append(computing_time_mean)
            results_compututing_time[algorithm_name][1].append(computing_time_low)
            results_compututing_time[algorithm_name][2].append(computing_time_up)

            # Aggregation of the overflow ratio : mean and bound of the confidence interval
            overflow_ratio_mean, overflow_ratio_low, overflow_ratio_up = mean_confidence_interval_bootstrap(list(overflow_ratio_list))
            results_overflow_ratio[algorithm_name][0].append(overflow_ratio_mean)
            results_overflow_ratio[algorithm_name][1].append(overflow_ratio_low)
            results_overflow_ratio[algorithm_name][2].append(overflow_ratio_up)

    # abscisse = [182.23, 362.88, 685.2, 1038.48, 1615.56, 2462.05, 3512.71, 5048.89, 8138.71, 11644.12]
    # abscisse = [63, 125.0, 234.0, 350.2, 540.3, 800.9, 1200.5, 1730.7, 2750.1, 3900.5]
    abscisse = list(temp_dict.keys())

    #Call to the plotting function for the differents metrics (performance, computing time, ...)
    # performance_figure = plot_results(abscisse, results_performance, algorithm_list, colors, formating, "Performance vs number of nodes", x_label=x_label, y_label="Path-change ratio", legend_position=legend_position)
    # computing_time_figure = plot_results(abscisse, results_compututing_time, algorithm_list, colors, formating, "Computing time vs number of nodes", x_label=x_label, y_label="Computing time", legend_position=legend_position)
    # overflow_ratio_figure = plot_results(abscisse, results_overflow_ratio, algorithm_list, colors, formating, "Total overflow vs number of nodes", x_label=x_label, y_label="Total overflow", legend_position=legend_position)
    performance_figure = plot_results(abscisse, results_performance, algorithm_list, colors, formating, "Performance vs nombre de noeuds", x_label=x_label, y_label="Ratio de changements de chemin", legend_position=legend_position)
    computing_time_figure = plot_results(abscisse, results_compututing_time, algorithm_list, colors, formating, "Temps de calcul vs nombre de noeuds", x_label=x_label, y_label="Temps de calcul", legend_position=legend_position)
    overflow_ratio_figure = plot_results(abscisse, results_overflow_ratio, algorithm_list, colors, formating, "Total overflow vs number of nodes", x_label=x_label, y_label="Ratio de dépassement de capacité", legend_position=legend_position)
    plt.show()


if __name__ == "__main__":
    # Set the path to the global directory
    # global_path = "/home/disc/f.lamothe"
    # global_path = "/home/francois/Desktop"
    assert False, "Unassigned global_path : Complete global_path with the path to the main directory"

    dataset_name = "graph_scaling_dataset_easy"
    # dataset_name = "graph_scaling_dataset_hard"
    # dataset_name = "graph_scaling_dataset_random"
    # dataset_name = "commodity_scaling_dataset"

    algorithm_list = []
    algorithm_list.append("SRR arc node")
    algorithm_list.append("SRR arc path")
    # algorithm_list.append("SRR arc node no penalization")
    # algorithm_list.append("SRR arc path no penalization")
    algorithm_list.append("SRR restricted")
    algorithm_list.append("B&B restricted short")
    # algorithm_list.append("B&B restricted medium")
    algorithm_list.append("B&B restricted long")
    algorithm_list.append("SRR path-combination")
    # algorithm_list.append("SRR path-combination no penalization")
    # algorithm_list.append("SRR path-combination timestep")
    # algorithm_list.append("SRR path-combination commodity")
    algorithm_list.append("SRR path-combination restricted")

    plot_dataset(global_path, dataset_name, algorithm_list, x_label="Nombre de noeuds", legend_position=None)
