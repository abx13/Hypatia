import random
import time

from .mcnf_dynamic import *
from .instance_mcnf import generate_instance, mutate_instance
from .k_shortest_path import k_shortest_path_all_destination
from .launch_dataset_dynamic import analyse_results_list


def update_graph_capacity(graph, path, demand, reverse_graph=False):
    # deecrease the capacities in the graph taken by a commodity size "demand" and allocate to the path "path"
    # also computes the overload created
    # negative demands are possible to increase the capacity instead of decreasing it

    new_overload = 0

    for i in range(len(path)-1):
        node = path[i]
        neighbor = path[i+1]

        if reverse_graph:
            node, neighbor = neighbor, node

        old_overload = - min(0, graph[node][neighbor])
        graph[node][neighbor] -= demand
        new_overload += - min(0, graph[node][neighbor]) - old_overload

    return new_overload


temp = time.time()

# # First timestep generation
# size = 5
# graph_type, graph_generator_inputs, demand_generator_inputs = "grid", (size, size, size, 2*size, 15000, 10000), {"smaller_commodities" : True}
# graph_type, graph_generator_inputs, demand_generator_inputs = "grid", (size, size, size, 2*size, 10000, 10000), {}
size = 30
graph_type, graph_generator_inputs, demand_generator_inputs = "random_connected", (size, 5/size, int(size * 0.1), 10000), {}
graph, commodity_list, initial_path_list, origin_list = generate_instance(graph_type, graph_generator_inputs, demand_generator_inputs)

instance_list = []
graph_copy = [{neighbor : graph[node][neighbor] for neighbor in graph[node]} for node in range(len(graph))]
commodity_list_copy = [commodity for commodity in commodity_list]
instance_list.append((graph_copy, commodity_list_copy))

results_list = []
results_list.append(initial_path_list)

# Generating subsquent timesteps
for i in range(10):
    mutate_instance(graph, commodity_list, origin_list)
    graph_copy = [{neighbor : graph[node][neighbor] for neighbor in graph[node]} for node in range(len(graph))]
    commodity_list_copy = [c for c in commodity_list]
    instance_list.append((graph_copy, commodity_list_copy))


# Printing a few metrics of the generated instances
g,cl = instance_list.pop(0)
initial_path_list = results_list.pop(0)
nb_commodities = len(cl)
total_demand = sum([commodity[2] for commodity in cl])
nb_nodes = len(g)
mininmum_number_of_path_changes, _ = compute_mininmum_number_of_path_changes(instance_list, initial_path_list)
print("total_demand = ", total_demand)
print("nb_commodities = ", nb_commodities)
print("nb_nodes = ", nb_nodes)
print("nb_timesteps = ", len(instance_list))
print("max capacity", max(g[node][neighbor] for node in range(len(g)) for neighbor in g[node]))
print("mininmum_number_of_path_changes = ", mininmum_number_of_path_changes)


# Choice of the tested algorithms
algorithm_list = []
algorithm_list.append("SRR arc node")
algorithm_list.append("SRR arc path")
# algorithm_list.append("SRR arc node no penalization")
# algorithm_list.append("SRR arc path no penalization")
# algorithm_list.append("SRR restricted")
# algorithm_list.append("SRR restricted multi-time-step")
algorithm_list.append("B&B restricted short")
# algorithm_list.append("B&B restricted medium")
# algorithm_list.append("B&B restricted long")
# algorithm_list.append("Partial B&B restricted")
algorithm_list.append("SRR path-combination")
# algorithm_list.append("SRR path-combination no penalization")
# algorithm_list.append("SRR path-combination restricted")
# algorithm_list.append("SRR path-combination commodity")
# algorithm_list.append("SRR path-combination timestep")

# Launch the chosen algorithm
for algorithm_name in algorithm_list:
    if algorithm_name == "SRR arc node" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_node_one_timestep, verbose=1)
    if algorithm_name == "SRR arc path" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_path_one_timestep, verbose=1)
    if algorithm_name == "SRR arc node no penalization" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_node_one_timestep, solver_keyword_arguments={"flow_penalisation" : 0}, verbose=1)
    if algorithm_name == "SRR arc path no penalization" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_path_one_timestep, solver_keyword_arguments={"flow_penalisation" : 0}, verbose=1)
    if algorithm_name == "SRR restricted" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, SRR_arc_path_one_timestep, solver_keyword_arguments={"nb_path_generations" : 0}, verbose=1)
    if algorithm_name == "SRR restricted multi-time-step" : results_list = SRR_arc_path2(instance_list, initial_path_list, verbose=1)
    if algorithm_name == "B&B restricted short" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, Branch_and_Bound_arc_path_one_timestep, solver_keyword_arguments={"time_limit" : 1.7 ** (np.sqrt(nb_nodes)) / 50, "nb_threads" : 1}, verbose=1)
    if algorithm_name == "B&B restricted medium" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, Branch_and_Bound_arc_path_one_timestep, solver_keyword_arguments={"time_limit" : 1.7 ** (np.sqrt(nb_nodes)) / 10, "nb_threads" : 1}, verbose=1)
    if algorithm_name == "B&B restricted long" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, Branch_and_Bound_arc_path_one_timestep, solver_keyword_arguments={"time_limit" : 1.7 ** (np.sqrt(nb_nodes)) / 2, "nb_threads" : 1}, verbose=1)
    if algorithm_name == "Partial B&B restricted" : results_list = iterate_one_timestep_solver(instance_list, initial_path_list, Branch_and_Bound_arc_path_one_timestep, solver_keyword_arguments={"nb_new_binary_var" : 1 + nb_commodities // 10, "time_limit" : 1.7 ** (np.sqrt(nb_nodes)) / 40, "nb_threads" : 1}, verbose=1)
    if algorithm_name == "SRR path-combination" : results_list = SRR_path_combinations(instance_list, initial_path_list)
    if algorithm_name == "SRR path-combination no penalization" : results_list = SRR_path_combinations(instance_list, initial_path_list, flow_penalisation=0)
    if algorithm_name == "SRR path-combination restricted" : results_list = SRR_path_combinations(instance_list, initial_path_list, exact_var_generation=False)
    if algorithm_name == "SRR path-combination commodity" : results_list = SRR_path_combinations2(instance_list, initial_path_list)
    if algorithm_name == "SRR path-combination timestep" : results_list = SRR_path_combinations2(instance_list, initial_path_list, rounding_method="round_by_timestep")

print("total_time = ", time.time() - temp)

# Printing results
commodity_path_list = initial_path_list
total_overload = 0
total_change = 0
total_necessary_change = 0
validity_duration_per_commodity = [[0] for commodity_index in range(nb_commodities)]
allowed_overflow = total_demand * 0.01
print("allowed overflow = ", allowed_overflow)
for timestep, commodity_path_list_2 in enumerate(results_list):
    nb_path_changes = 0
    graph, commodity_list = instance_list[timestep]
    use_graph = [{neighbor : 0 for neighbor in graph[node]} for node in range(len(graph))]

    for commodity_index, path in enumerate(commodity_path_list_2):
        assert is_correct_path(graph, commodity_list[commodity_index], path)
        if commodity_path_list[commodity_index] != path:
            validity_duration_per_commodity[commodity_index].append(0)
            nb_path_changes += 1

        validity_duration_per_commodity[commodity_index][-1] += 1
        update_graph_capacity(use_graph, path, -commodity_list[commodity_index][2])

    overload_graph = [{neighbor : max(0, use_graph[node][neighbor] - graph[node][neighbor]) for neighbor in graph[node]} for node in range(len(graph))]
    overload = sum([sum(dct.values()) for dct in overload_graph])
    total_overload += max(0, overload - allowed_overflow)
    print("overload = ", overload)
    total_change += nb_path_changes

    commodity_path_list = commodity_path_list_2

print("total_change = ", total_change)
print("mininmum_number_of_path_changes = ", mininmum_number_of_path_changes)
print("total_change ratio = ", total_change / mininmum_number_of_path_changes)
print("total_overload = ", total_overload)
