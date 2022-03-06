import random
import numpy as np
import time
import pickle
from multiprocessing import Process, Manager

from .instance_mcnf import generate_instance, mutate_instance
from .mcnf_dynamic import *

def launch_dataset(global_path, dataset_name, algorithm_list, nb_repetitions, nb_workers, duration_before_timeout):
    # Launches all the algorithms to test on the instance present in the dataset directory
    # The number of time algorithms are lauched is decided with nb_repetitions
    # nb_workers is the number of parallel threads used
    # if an algorithm takes more than duration_before_timeout time to finish, its thread is killed

    # Open the file containing the name of the instances
    instance_name_file = open(global_path + "/Dynamic_mcnf_paper_code/instance_files_dynamic/" + dataset_name + "/instance_name_file.p", "rb" )
    instance_name_list = pickle.load(instance_name_file)
    instance_name_file.close()

    log_file = open(global_path + "/Dynamic_mcnf_paper_code/log_file.txt", 'w')
    log_file.write("Start\n")
    log_file.close()

    manager = Manager()
    worker_list = []
    # Dictionnary of results
    result_dict = {algorithm_name : {instance_name : [None]*nb_repetitions for instance_name in instance_name_list} for algorithm_name in algorithm_list}
    # List of jobs to be done
    computation_list = [(repetition_index, instance_index, instance_name, algorithm_name) for repetition_index in range(nb_repetitions)
                                                                                            for instance_index, instance_name in enumerate(instance_name_list)
                                                                                                for algorithm_name in algorithm_list]

    while len(computation_list) + len(worker_list) > 0:

        remaining_worker_list = []
        # Cleaning finished jobs and killing jobs lasting more than duration_before_timeout
        for process, start_time, return_list, computation_info in worker_list:
            repetition_index, instance_index, instance_name, algorithm_name = computation_info

            if not process.is_alive():
                result_dict[algorithm_name][instance_name][repetition_index] = return_list[0]

            elif time.time() > start_time + duration_before_timeout:
                process.terminate()
                result_dict[algorithm_name][instance_name][repetition_index] = (None, None, None, None, None, duration_before_timeout)

            else:
                remaining_worker_list.append((process, start_time, return_list, computation_info))

        worker_list = remaining_worker_list

        # Launching new jobs if possible
        if len(worker_list) < nb_workers and len(computation_list) > 0:
            computation_info = computation_list.pop(0)
            repetition_index, instance_index, instance_name, algorithm_name = computation_info

            print_string = "repetition : {0}/{1}, instance : {2}/{3}, algorithm : {4}".format(repetition_index, nb_repetitions, instance_index, len(instance_name_list), algorithm_name)
            instance_file_path = global_path + "/Dynamic_mcnf_paper_code/instance_files_dynamic/" + dataset_name + "/" + instance_name + ".p"
            return_list = manager.list()

            process = Process(target=launch_solver_on_instance, args=(instance_file_path, algorithm_name, print_string, global_path, return_list))
            start_time = time.time()
            process.start()
            worker_list.append((process, start_time, return_list, computation_info))


    # Write the results in a file
    result_file = open(global_path + "/Dynamic_mcnf_paper_code/instance_files_dynamic/" + dataset_name + "/result_file.p", "wb" )
    pickle.dump(result_dict, result_file)
    result_file.close()

    import datetime
    log_file = open(global_path + "/Dynamic_mcnf_paper_code/log_file.txt", 'a')
    log_file.write(datetime.datetime.now().__str__())
    log_file.close()


def launch_solver_on_instance(instance_file_path, algorithm_name, print_string, global_path, return_list):
    # Lauch the algorithm named algortihm_name on the instance store in the file at instance_file_path

    print(print_string)

    # Read the instance in the instance file
    instance_file = open(instance_file_path, "rb" )
    instance_list, initial_path_list = pickle.load(instance_file)
    instance_file.close()

    initial_graph, initial_commodity_list = instance_list.pop(0)
    nb_commodities = len(initial_commodity_list)
    nb_timesteps = len(instance_list)
    nb_nodes = len(initial_graph)
    print(len(initial_graph))
    print(nb_commodities)

    temp = time.time()

    # Launch the chosen algorithm
    if algorithm_name == "SRR arc node" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_node_one_timestep, verbose=0)
    if algorithm_name == "SRR arc path" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_path_one_timestep, verbose=0)
    if algorithm_name == "SRR arc node no penalization" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_node_one_timestep, solver_keyword_arguments={"flow_penalisation" : 0}, verbose=0)
    if algorithm_name == "SRR arc path no penalization" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_path_one_timestep, solver_keyword_arguments={"flow_penalisation" : 0}, verbose=0)
    if algorithm_name == "SRR restricted" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_path_one_timestep, solver_keyword_arguments={"nb_path_generations" : 0}, verbose=0)
    if algorithm_name == "SRR restricted multi-time-step" : results_list = SRR_arc_path2(instance_list, initial_path_list, verbose=0)
    if algorithm_name == "B&B restricted short" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, Branch_and_Bound_arc_path_one_timestep, solver_keyword_arguments={"time_limit" : 1.7 ** (np.sqrt(nb_nodes)) / 50, "nb_threads" : 1}, verbose=0)
    if algorithm_name == "B&B restricted medium" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, Branch_and_Bound_arc_path_one_timestep, solver_keyword_arguments={"time_limit" : 1.7 ** (np.sqrt(nb_nodes)) / 10, "nb_threads" : 1}, verbose=0)
    if algorithm_name == "B&B restricted long" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, Branch_and_Bound_arc_path_one_timestep, solver_keyword_arguments={"time_limit" : 1.7 ** (np.sqrt(nb_nodes)) / 2, "nb_threads" : 1}, verbose=0)
    if algorithm_name == "Partial B&B restricted" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, Branch_and_Bound_arc_path_one_timestep, solver_keyword_arguments={"nb_new_binary_var" : 1 + nb_commodities // 10, "time_limit" : 1.7 ** (np.sqrt(nb_nodes)) / 40, "nb_threads" : 1}, verbose=0)
    if algorithm_name == "SRR path-combination" : results_list = SRR_path_combinations(instance_list, initial_path_list)
    if algorithm_name == "SRR path-combination no penalization" : results_list = SRR_path_combinations(instance_list, initial_path_list, flow_penalisation=0)
    if algorithm_name == "SRR path-combination restricted" : results_list = SRR_path_combinations(instance_list, initial_path_list, exact_var_generation=False)
    if algorithm_name == "SRR path-combination commodity" : results_list = SRR_path_combinations2(instance_list, initial_path_list)
    if algorithm_name == "SRR path-combination timestep" : results_list = SRR_path_combinations2(instance_list, initial_path_list, rounding_method="round_by_timestep")

    computing_time = time.time() - temp

    total_path_changes, min_nb_of_path_changes, path_changes_ratio, total_overload, overload_ratio = analyse_results_list(instance_list, initial_path_list, results_list)

    log_file = open(global_path + "/Dynamic_mcnf_paper_code/log_file.txt", 'a')
    log_file.write("Finished : " + instance_file_path + ", " + print_string + "\n")
    log_file.close()

    print("Finished")

    return_list.append((total_path_changes, min_nb_of_path_changes, path_changes_ratio, total_overload, overload_ratio, computing_time))


def analyse_results_list(instance_list, initial_path_list, results_list):
    # Compute various metrics extracted from the solution of an algorithm
    nb_timesteps = len(instance_list)
    allowed_overflow = sum([commodity[2] for commodity in instance_list[0][1]]) * 0.01
    old_path_list = initial_path_list
    total_path_changes = total_overload = 0
    min_nb_of_path_changes, _ = compute_mininmum_number_of_path_changes(instance_list, initial_path_list)

    for instance, new_path_list in zip(instance_list, results_list):
        nb_path_changes = 0
        graph, commodity_list = instance
        use_graph = [{neighbor : 0 for neighbor in graph[node]} for node in range(len(graph))]

        for commodity, old_path, new_path in zip(commodity_list, old_path_list, new_path_list):
            update_graph_capacity(use_graph, new_path, -commodity[2])

            if old_path != new_path:
                nb_path_changes += 1

        overload_graph = [{neighbor : max(0, use_graph[node][neighbor] - graph[node][neighbor]) for neighbor in graph[node]} for node in range(len(graph))]
        overload = sum([sum(dct.values()) for dct in overload_graph])
        total_overload += max(0, overload - allowed_overflow)

        total_path_changes += nb_path_changes
        old_path_list = new_path_list

    path_changes_ratio = total_path_changes / min_nb_of_path_changes
    overload_ratio = total_overload / (allowed_overflow * nb_timesteps)

    return total_path_changes, min_nb_of_path_changes, path_changes_ratio, total_overload, overload_ratio


if __name__ == "__main__":
    # Set the path to the global directory
    # global_path = "/home/disc/f.lamothe"
    global_path = "/home/francois/Desktop"
    # assert False, "Unassigned global_path : Complete global_path with the path to the main directory"

    # Set the number of repetition
    nb_repetitions = 1
    nb_workers = 30
    duration_before_timeout = 3*60*60

    settings_list = []
    settings_list.append(("graph_scaling_dataset_easy", ["SRR arc node", "SRR arc path", "SRR arc node no penalization", "SRR arc path no penalization", 'SRR restricted', 'SRR restricted multi-time-step', "B&B restricted short", "B&B restricted medium", "B&B restricted long", "SRR path-combination", "SRR path-combination no penalization", "SRR path-combination timestep", "SRR path-combination commodity", "SRR path-combination restricted"]))
    settings_list.append(("graph_scaling_dataset_hard", ["SRR arc node", "SRR arc path", "SRR arc node no penalization", "SRR arc path no penalization", 'SRR restricted', 'SRR restricted multi-time-step', "B&B restricted short", "B&B restricted medium", "B&B restricted long", "SRR path-combination", "SRR path-combination no penalization", "SRR path-combination timestep", "SRR path-combination commodity", "SRR path-combination restricted"]))
    settings_list.append(("graph_scaling_dataset_random", ["SRR arc node", "SRR arc path", "SRR arc node no penalization", "SRR arc path no penalization", 'SRR restricted', 'SRR restricted multi-time-step', "B&B restricted short", "B&B restricted medium", "SRR path-combination", "SRR path-combination no penalization", "SRR path-combination timestep", "SRR path-combination commodity", "SRR path-combination restricted"]))
    settings_list.append(("commodity_scaling_dataset", ["SRR arc node", "SRR arc path", "SRR arc node no penalization", "SRR arc path no penalization", 'SRR restricted', 'SRR restricted multi-time-step', "B&B restricted short", "B&B restricted medium", "B&B restricted long", "SRR path-combination", "SRR path-combination no penalization", "SRR path-combination timestep", "SRR path-combination commodity", "SRR path-combination restricted"]))


    for dataset_name, algorithm_list in settings_list:
        launch_dataset(global_path, dataset_name, algorithm_list, nb_repetitions, nb_workers, duration_before_timeout)
