import random
import numpy as np
import time
import pickle


from .instance_mcnf import generate_instance, mutate_instance


nb_repetitions = 10
nb_unique_exp = 10
nb_timesteps = 10

# Size of the graph : controls the number of nodes and arcs
# size_list = [3, 4, 5, 6, 7, 9, 10, 12, 13, 15]
# size_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
# size_list = [12, 20, 30, 42, 56, 90, 110, 156, 182, 240]
# size_list = [3, 4, 5, 6, 7, 9, 10, 12]
# size_list = [2, 3, 4, 5, 6, 7, 8, 9]
size_list = [12, 20, 30, 42, 56, 90, 110, 132, 156, 182, 210, 240]
# size_list = [6]*nb_unique_exp
size_list = np.array(size_list)

# Capacity of the arcs of the graph
capacity_list = [10000] * nb_unique_exp
# capacity_list = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]

# Upper bound on the size of the commodities
max_demand_list = [1500] * nb_unique_exp
# max_demand_list = [int(np.sqrt(capa)) for capa in capacity_list]

# Choose here the type of graph to be created: note that the size parameter does not have the same meaning for both types
instance_parameter_list = []
for size, capacity, max_demand in zip(size_list, capacity_list, max_demand_list):
    # instance_parameter_list.append(("grid", (size, size, size, 2*size, 5000 + capacity, capacity), {"max_demand" : max_demand, "smaller_commodities" : True}))
    # instance_parameter_list.append(("grid", (size, size, size, 2*size, capacity, capacity), {"max_demand" : max_demand}))
    instance_parameter_list += [("random_connected", (size, 5/size, int(size * 0.1), capacity), {"max_demand" : max_demand})]


# Complete with the path to the main directory
global_path = "/home/francois/Desktop/"

# Complete name of the directory that will contain the instances
# experience_string = "graph_scaling_dataset_easy/"
# experience_string = "graph_scaling_dataset_hard/"
experience_string = "graph_scaling_dataset_random/"
# experience_string = "commodity_scaling_dataset/"

i = -1
instance_name_list = []
for graph_type, graph_generator_inputs, demand_generator_inputs in instance_parameter_list:
    i += 1
    for j in range(0, nb_repetitions):
        print(i,j)

        # Generate the graph and the commodity list
        graph, commodity_list, initial_path_list, origin_list = generate_instance(graph_type, graph_generator_inputs, demand_generator_inputs)

        instance_list = []

        # Generating subsquent timesteps
        for timestep in range(nb_timesteps + 1):
            graph_copy = [{neighbor : graph[node][neighbor] for neighbor in graph[node]} for node in range(len(graph))]
            commodity_list_copy = [c for c in commodity_list]
            instance_list.append((graph_copy, commodity_list_copy))
            mutate_instance(graph, commodity_list, origin_list)

        if graph_type == "grid":
            size = size_list[i]
            nb_nodes = size ** 2 + size
        elif graph_type == "random_connected":
            nb_nodes = size_list[i]

        instance_name = graph_type + "_" + str(nb_nodes) + "_" + str(capacity_list[i]) + "_" + str(max_demand_list[i]) + "_" + str(j) + "_" + str(nb_timesteps)

        # Store the created instance
        instance_file = open(global_path + "dynamic_mcnf_paper_code/instance_files_dynamic/" + experience_string + instance_name + ".p", "wb" )
        pickle.dump((instance_list, initial_path_list), instance_file)
        instance_file.close()

        instance_name_list.append(instance_name)

# Create a file containing the name of all the instances
instance_name_file = open(global_path + "dynamic_mcnf_paper_code/instance_files_dynamic/" + experience_string + "instance_name_file.p", "wb" )
pickle.dump(instance_name_list, instance_name_file)
instance_name_file.close()
