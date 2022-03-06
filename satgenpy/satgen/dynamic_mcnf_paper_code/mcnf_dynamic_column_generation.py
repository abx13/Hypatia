import numpy as np
import random
import time
import gurobipy
import heapq as hp

def create_column_generation_model(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, allowed_overflow=None, verbose=1):
    # Creates path-sequence formulation for the dynamic unsplittable flow problem
    nb_commodities = len(initial_path_list)
    nb_timesteps = len(instance_list)
    nb_nodes = len(instance_list[0][0])
    demand_list = [c[2] for c in instance_list[0][1]]
    arc_list = [(timestep, node, neighbor) for timestep, instance in enumerate(instance_list) for node in range(nb_nodes) for neighbor in instance[0][node]]

    if allowed_overflow is None:
        allowed_overflow = sum(demand_list) * 0.01

    # Create optimization model
    model = gurobipy.Model('netflow')
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.Params.OutputFlag = verbose
    # model.Params.Method = 3

    # Creating initial path-sequence variables
    combination_and_var_per_commodity = [[] for commodity_index in range(nb_commodities)]
    for commodity_index in range(nb_commodities):
        combination = []
        cost = 0
        current_path = initial_path_list[commodity_index]

        for timestep in range(nb_timesteps):
            path = possible_paths_per_commodity_per_timestep[timestep][commodity_index][0]
            combination.append(path)

            if path != current_path:
                cost += 1
                current_path = path

        var = model.addVar(obj=cost)

        combination_and_var_per_commodity[commodity_index].append((combination, var))

    # Create other variables
    overload_var = model.addVars(arc_list)
    total_overload_var = model.addVars(nb_timesteps, obj=1, name="total_overload")
    if verbose: print("variables created")

    # Convexity constraints :
    convexity_constraint_dict = model.addConstrs((sum(var for combination, var in combination_and_var_per_commodity[commodity_index]) == 1 for commodity_index in range(nb_commodities)), "convexity")
    if verbose: print("Convexity constraints created")

    # Capacity constraint
    capacity_constraint_dict = {}
    for timestep, instance in enumerate(instance_list):
        graph, commodity_list = instance
        edge_use_dict = {(node, neighbor): 0 for node in range(nb_nodes) for neighbor in graph[node]}

        for commodity_index, demand in enumerate(demand_list):
            for combination, var in combination_and_var_per_commodity[commodity_index]:
                path = combination[timestep]

                for node_index in range(len(path)-1):
                    node, neighbor = path[node_index], path[node_index+1]
                    edge_use_dict[node, neighbor] += var * demand

        for node in range(nb_nodes):
            for neighbor in graph[node]:
                capacity_constraint_dict[timestep, node, neighbor] = model.addConstr((edge_use_dict[node, neighbor] - overload_var[timestep, node, neighbor] <= graph[node][neighbor]))

    total_capacity_constraint_dict = model.addConstrs(overload_var.sum(timestep, '*', '*') - total_overload_var[timestep] <= allowed_overflow for timestep in range(nb_timesteps))
    if verbose: print("Capacity constraints created")

    return model, (combination_and_var_per_commodity, overload_var, convexity_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict)


def run_column_generation(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, model, model_attributes, nb_iterations=10**10,
                            fixed_paths_per_commodity_per_timestep=None, changeable_commodities_indices=None, var_delete_proba=0.3, exact_var_generation=False,
                            flow_penalisation=0, verbose=1):
    # Runs the column generation process for a path-sequence formulation of the dynamic unsplittable flow problem
    # The column generation can either consider fixed sets of paths for each commodity of consider that all paths are allowed
    nb_commodities = len(initial_path_list)
    nb_nodes = len(instance_list[0][0])
    nb_timesteps = len(instance_list)
    demand_list = [c[2] for c in instance_list[0][1]]
    combination_and_var_per_commodity, overload_var, convexity_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = model_attributes
    t = [0]*5

    if changeable_commodities_indices is None:
        changeable_commodities_indices = list(range(nb_commodities))

    # Only usefull if fixed sets of paths are considered : precomputes some information for faster computations in the main loop
    dual_computation_information = create_dual_computation_information(possible_paths_per_commodity_per_timestep, instance_list)

    for iter_index in range(nb_iterations):

        temp = time.time()
        model.update()
        model.optimize()
        t[0] += time.time() - temp

        if verbose:
            print(iter_index, " #########    ")
            print("ObjVal = ", model.ObjVal)
            print("path changes = ", sum(var.X * var.Obj for tuple_list in combination_and_var_per_commodity for combination, var in tuple_list))
            print("overload = ", sum(overload_var[var_index].X for var_index in overload_var))
            print("Nb Variables = ", sum(len(tuple_list) for tuple_list in combination_and_var_per_commodity))
            print(t)

        for commodity_index, tuple_list in enumerate(combination_and_var_per_commodity):
            new_tuple_list = []

            for combination, var in tuple_list:
                if var.Vbasis != 0 and random.random() < var_delete_proba:
                    assert var.X < 0.1, var.X
                    model.remove(var)
                else:
                    new_tuple_list.append((combination, var))

            combination_and_var_per_commodity[commodity_index] = new_tuple_list

        dual_array = create_dual_array(capacity_constraint_dict, instance_list, flow_penalisation)
        reduced_cost_graph_per_timestep = [[{neighbor : -capacity_constraint_dict[timestep, node, neighbor].Pi + flow_penalisation for neighbor in instance[0][node]} for node in range(nb_nodes)] for timestep, instance in enumerate(instance_list)]
        shortest_paths_structure = {(timestep1, timestep2) : {} for timestep1 in range(nb_timesteps) for timestep2 in range(timestep1, nb_timesteps)}
        cumulated_reduced_cost_graphs = {}

        for timestep1 in range(nb_timesteps):
            cumulated_reduced_cost_graph = reduced_cost_graph_per_timestep[timestep1]

            for timestep2 in range(timestep1, nb_timesteps):
                cumulated_reduced_cost_graph = [{neighbor : cumulated_reduced_cost_graph[node][neighbor] for neighbor in cumulated_reduced_cost_graph[node]} for node in range(nb_nodes)]

                if timestep2 != timestep1:
                    for node in range(nb_nodes):
                        for neighbor in list(cumulated_reduced_cost_graph[node].keys()):
                            if neighbor in reduced_cost_graph_per_timestep[timestep2][node]:
                                cumulated_reduced_cost_graph[node][neighbor] += reduced_cost_graph_per_timestep[timestep2][node][neighbor]
                            else:
                                cumulated_reduced_cost_graph[node].pop(neighbor)

                cumulated_reduced_cost_graphs[timestep1, timestep2] = cumulated_reduced_cost_graph

        nb_new_var = 0
        for commodity_index in changeable_commodities_indices:
            if verbose: print(commodity_index, end='   \r')

            temp = time.time()

            convexity_dual_val = convexity_constraint_dict[commodity_index].Pi
            initial_path = initial_path_list[commodity_index]

            commodity_informations = [instance_list[timestep][1][commodity_index] for timestep in range(nb_timesteps)]

            if fixed_paths_per_commodity_per_timestep is None:
                fixed_paths_per_timestep = [None] * nb_timesteps
            else:
                fixed_paths_per_timestep = [fixed_paths_per_commodity[commodity_index] for fixed_paths_per_commodity in fixed_paths_per_commodity_per_timestep]

            if exact_var_generation:
                option_reduced_price_list = get_option_reduced_price_list_exact(shortest_paths_structure, reduced_cost_graph_per_timestep, cumulated_reduced_cost_graphs, commodity_informations, initial_path, fixed_paths_per_timestep=fixed_paths_per_timestep)
            else:
                option_reduced_price_list = get_option_reduced_price_list(dual_computation_information[commodity_index], dual_array, reduced_cost_graph_per_timestep, commodity_informations, fixed_paths_per_timestep=fixed_paths_per_timestep)
            t[1] += time.time() - temp

            temp = time.time()
            combination, combination_reduced_cost = pricing_problem(option_reduced_price_list, initial_path, convexity_dual_val)
            t[2] += time.time() - temp

            temp = time.time()
            if combination_reduced_cost < -10**-6 :
                nb_new_var += 1
                column = gurobipy.Column()
                column.addTerms(1, convexity_constraint_dict[commodity_index])
                combination_cost = 0

                for timestep, path in enumerate(combination):
                    for node_index in range(len(path)-1):
                        node, neighbor = path[node_index], path[node_index + 1]
                        column.addTerms(demand_list[commodity_index], capacity_constraint_dict[timestep, node, neighbor])

                    # combination_cost += flow_penalisation * (len(path) - 1)
                    parent_path = initial_path_list[commodity_index] if timestep == 0 else combination[timestep - 1]
                    combination_cost += int(path != parent_path)

                var = model.addVar(obj=combination_cost, column=column)
                combination_and_var_per_commodity[commodity_index].append((combination, var))
            t[3] += time.time() - temp

        if verbose :
            print(t)
            print("nb_new_var = ", nb_new_var)

        if nb_new_var == 0:
            break

    model.update()
    model.optimize()


def dijkstra(graph, initial_node, destination_node=None, return_path=False):
    priority_q = [(0, initial_node, None)]
    parent_list = [None] * len(graph)
    distances = [None] * len(graph)

    while priority_q:
        value, current_node, parent_node = hp.heappop(priority_q)
        if distances[current_node] is None:
            parent_list[current_node] = parent_node
            distances[current_node] = value

            if current_node == destination_node:
                break

            for neighbor in graph[current_node]:
                if distances[neighbor] is None:
                    hp.heappush(priority_q, (value + graph[current_node][neighbor], neighbor, current_node))

    if return_path and destination_node is not None:
        path = [destination_node]
        path_cost = 0
        current_node = destination_node

        while current_node != initial_node:
            path_cost += graph[parent_list[current_node]][current_node]
            current_node = parent_list[current_node]
            path.append(current_node)

        path.reverse()
        return path, path_cost

    return parent_list, distances


def shortest_path_all_destination(graph, initial_node):
    nb_nodes = len(graph)
    parent_list, distances = dijkstra(graph, initial_node)
    shortest_path_list = [None] * nb_nodes
    shortest_path_list[initial_node] = ([initial_node], 0)

    for node in range(nb_nodes):
        if shortest_path_list[node] is None and parent_list[node] is not None:
            compute_shortest_path(graph, shortest_path_list, parent_list, node)

    return shortest_path_list


def compute_shortest_path(graph, shortest_path_list, parent_list, node):
    parent = parent_list[node]
    if shortest_path_list[parent] is None:
        compute_shortest_path(graph, shortest_path_list, parent_list, parent)

    parent_path, parent_path_cost = shortest_path_list[parent]
    shortest_path_list[node] = (parent_path + [node], parent_path_cost + graph[parent][node])


def shortest_path_graph_all_destination(graph, initial_node):
    nb_nodes = len(graph)
    parent_list, distances = dijkstra(graph, initial_node)

    shortest_path_tree = [[] for node in range(nb_nodes)]
    for node in range(nb_nodes):
        if parent_list[node] is not None:
            shortest_path_tree[parent_list[node]].append(node)

    node_order = []
    pile = [initial_node]
    while pile:
        current_node = pile.pop(0)
        node_order.append(current_node)
        for neighbor in shortest_path_tree[current_node]:
            pile.append(neighbor)

    node_position = [None] * nb_nodes
    for index, node in enumerate(node_order):
        node_position[node] = index

    shortest_path_graph = [[] for node in range(nb_nodes)]
    for node in range(nb_nodes):
        for neighbor in graph[node]:
            if distances[node] is not None and distances[neighbor] == distances[node] + graph[node][neighbor] and node_position[node] < node_position[neighbor]:
                shortest_path_graph[neighbor].append(node)

    # l = [len(shortest_path_graph[node]) for node in range(nb_nodes) if shortest_path_graph[node] != []]
    # print(sum(l)/len(l))

    return shortest_path_graph


def compute_path_from_shortest_path_graph(shortest_path_graph, origin, destination):
    current_node = destination
    path = [current_node]

    while current_node != origin:

        if len(shortest_path_graph[current_node]) == 0:
            return

        current_node = np.random.choice(shortest_path_graph[current_node])
        path.append(current_node)

    path.reverse()
    return path


def is_correct_path(graph, commodity, path):
    # function that checks if a path is valid for a commodity in an instance

    origin, destination, demand = commodity
    is_correct =  path[0] == origin and path[-1] == destination

    for node_index in range(len(path)-1):
        node, neighbor = path[node_index], path[node_index+1]
        is_correct = is_correct and neighbor in graph[node]
        if not is_correct:
            break

    return is_correct


def get_option_reduced_price_list(dual_computation_information, dual_array, reduced_cost_graph_per_timestep, commodity_informations, fixed_paths_per_timestep=None):
    nb_timesteps = len(dual_computation_information)
    option_reduced_price_list = []

    for timestep, information in enumerate(dual_computation_information):
        reduced_cost_graph = reduced_cost_graph_per_timestep[timestep]

        if fixed_paths_per_timestep is not None and fixed_paths_per_timestep[timestep] is not None:
            fixed_path = fixed_paths_per_timestep[timestep]
            path_cost = 0
            origin, destination, demand = commodity_informations[timestep]

            for node_index in range(len(fixed_path)-1):
                node, neighbor = fixed_path[node_index], fixed_path[node_index+1]
                path_cost += reduced_cost_graph[node][neighbor]

            option_reduced_price_list.append([(tuple(fixed_path), path_cost * demand)])

        else:
            origin, destination, demand = commodity_informations[timestep]
            path_tuple_list, dual_extractor = information
            path_cost_list = list(demand * sum(dual_array[dual_extractor]))
            option_reduced_price_list.append(list(zip(path_tuple_list, path_cost_list)))

    return option_reduced_price_list


def get_option_reduced_price_list_exact(shortest_paths_structure, reduced_cost_graph_per_timestep, cumulated_reduced_cost_graphs, commodity_informations, initial_path, fixed_paths_per_timestep=None, create_same_path_per_commodity=True):
    nb_timesteps = len(reduced_cost_graph_per_timestep)
    last_fixed_path = initial_path
    starting_timestep = 0

    option_reduced_price_list = []
    for timestep, commodity_information in enumerate(commodity_informations):
        if fixed_paths_per_timestep is not None and fixed_paths_per_timestep[timestep] is not None:
            starting_timestep = timestep + 1
            last_fixed_path = fixed_paths_per_timestep[timestep]

        reduced_cost_graph = reduced_cost_graph_per_timestep[timestep]
        if is_correct_path(reduced_cost_graph, commodity_information, last_fixed_path):
            path_cost = 0

            for node_index in range(len(last_fixed_path)-1):
                node, neighbor = last_fixed_path[node_index], last_fixed_path[node_index+1]
                path_cost += reduced_cost_graph[node][neighbor]

            option_reduced_price_list.append([(tuple(last_fixed_path), path_cost * commodity_information[2])])
        else:
            option_reduced_price_list.append([])

    for timestep1 in range(starting_timestep, nb_timesteps):
        origin, destination, demand = commodity_informations[timestep1]
        for timestep2 in range(timestep1, nb_timesteps):

            if destination != commodity_informations[timestep2][1]:
                break

            if create_same_path_per_commodity:
                if origin not in shortest_paths_structure[timestep1, timestep2]:
                    shortest_paths_structure[timestep1, timestep2][origin] = shortest_path_all_destination(cumulated_reduced_cost_graphs[timestep1, timestep2], origin)
                path_and_cost = shortest_paths_structure[timestep1, timestep2][origin][destination]
                path = None if path_and_cost is None else path_and_cost[0]

            else:
                if origin not in shortest_paths_structure[timestep1, timestep2]:
                    shortest_paths_structure[timestep1, timestep2][origin] = shortest_path_graph_all_destination(cumulated_reduced_cost_graphs[timestep1, timestep2], origin)
                shortest_path_graph = shortest_paths_structure[timestep1, timestep2][origin]
                path = compute_path_from_shortest_path_graph(shortest_path_graph, origin, destination)

            if path is not None:
                for timestep3 in range(timestep1, timestep2+1):

                    path_cost = 0
                    for node_index in range(len(path)-1):
                        node, neighbor = path[node_index], path[node_index+1]
                        path_cost += reduced_cost_graph_per_timestep[timestep3][node][neighbor]

                    option_reduced_price_list[timestep3].append((tuple(path), path_cost * demand))

    return option_reduced_price_list


def create_dual_array(capacity_constraint_dict, instance_list, flow_penalisation):
    nb_nodes = len(instance_list[0][0])
    nb_timesteps = len(instance_list)
    dual_array = np.zeros((nb_timesteps, nb_nodes, nb_nodes))

    for timestep, instance in enumerate(instance_list):
        graph, commodity_list = instance
        for node in range(nb_nodes):
            for neighbor in graph[node]:
                dual_array[timestep,node,neighbor] = -capacity_constraint_dict[timestep, node, neighbor].Pi + flow_penalisation

    return dual_array


def create_dual_computation_information(possible_paths_per_commodity_per_timestep, instance_list):
    nb_commodities = len(possible_paths_per_commodity_per_timestep[0])
    dual_computation_information = [[] for commodity_index in range(nb_commodities)]

    for timestep, possible_paths_per_commodity in enumerate(possible_paths_per_commodity_per_timestep):
        information = []
        for commodity_index, path_list in enumerate(possible_paths_per_commodity):
            path_tuple_list = [tuple(path) for path in path_list]

            max_nb_arc = max([len(path) for path in path_list])-1
            dual_extractor = (np.ones((max_nb_arc, len(path_list)), dtype="int") * timestep, np.zeros((max_nb_arc, len(path_list)), dtype="int"), np.zeros((max_nb_arc, len(path_list)), dtype="int"))

            for index, path in enumerate(path_list):
                for node_index in range(len(path)-1):
                    dual_extractor[1][node_index][index] = path[node_index]
                    dual_extractor[2][node_index][index] = path[node_index+1]

            dual_computation_information[commodity_index].append((path_tuple_list, dual_extractor))

    return dual_computation_information



def pricing_problem(option_reduced_price_list, initial_path, convexity_dual_val, path_change_penalty=1):
    nb_timesteps = len(option_reduced_price_list)
    dynamic_programming_parent_list = []
    old_value_function = {tuple(initial_path) : -convexity_dual_val}
    best_old_path_tuple = tuple(initial_path)

    for timestep, option_list in enumerate(option_reduced_price_list):
        new_value_function = {}
        dynamic_programming_parent = {}
        best_new_path_tuple = None

        for path_tuple, path_cost in option_list:
            new_value_function[path_tuple] = old_value_function[best_old_path_tuple] + path_cost + path_change_penalty
            dynamic_programming_parent[path_tuple] = best_old_path_tuple

            if path_tuple in old_value_function and old_value_function[path_tuple] + path_cost < new_value_function[path_tuple]:
                new_value_function[path_tuple] = old_value_function[path_tuple] + path_cost
                dynamic_programming_parent[path_tuple] = path_tuple

            if best_new_path_tuple is None or new_value_function[path_tuple] < best_new_value:
                best_new_path_tuple = path_tuple
                best_new_value = new_value_function[path_tuple]

        best_old_path_tuple = best_new_path_tuple


        dynamic_programming_parent_list.append(dynamic_programming_parent)
        old_value_function = new_value_function

    combination_reduced_cost = 10**10
    for path_tuple in old_value_function:
        if old_value_function[path_tuple] < combination_reduced_cost:
            combination_reduced_cost = old_value_function[path_tuple]
            last_path_tuple = path_tuple

    combination = [list(last_path_tuple)]
    current_path_tuple = last_path_tuple

    for reverse_timestep in range(nb_timesteps):
        timestep = nb_timesteps - 1 - reverse_timestep
        parent_path_tuple = dynamic_programming_parent_list[timestep][current_path_tuple]
        current_path_tuple = parent_path_tuple
        combination.append(list(current_path_tuple))

    combination.pop()
    combination.reverse()

    return combination, combination_reduced_cost
