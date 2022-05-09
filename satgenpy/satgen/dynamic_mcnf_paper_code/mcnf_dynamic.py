import heapq as hp
import random
import numpy as np
import time

from .mcnf_dynamic_column_generation import create_column_generation_model, run_column_generation
from .k_shortest_path import k_shortest_path_all_destination
from .mcnf_dynamic_continuous import *


def find_fitting_most_capacited_path(graph1, graph2, origin, destination, minimum_capacity):
    # this is a dijkstra like algorithm that computes the most capacited path from the origin to the destination
    # the best capacity is according to graph1 but only edges with capacities >= minimum_capacity in graph2 are taken into account
    priority_q = [(-10.**10, origin, None)]

    parent_list = [None] * len(graph1)
    visited = [False]*len(graph1)
    best_capacity = [None] * len(graph1)

    while priority_q != []:
        c, current_node, parent_node = hp.heappop(priority_q)
        capa_of_current_node = -c

        if not visited[current_node]:
            visited[current_node] = True
            parent_list[current_node] = parent_node
            best_capacity[current_node] = capa_of_current_node

            if current_node == destination:
                break

            for neighbor in graph1[current_node]:
                if not visited[neighbor] and graph2[current_node][neighbor] >= minimum_capacity:
                    hp.heappush(priority_q, (-min(capa_of_current_node, graph1[current_node][neighbor][0]), neighbor, current_node))

    if parent_list[destination] is None:
        return None, None

    path = [destination]
    current_node = destination
    while current_node != origin:
        current_node = parent_list[current_node]
        path.append(current_node)
    path.reverse()

    return path, best_capacity[destination]

def find_fitting_shortest_path(graph1, graph2, origin, destination, minimum_capacity):
    # this is a dijkstra like algorithm that computes the shortest path with enough capacity from the origin to the destination
    # the edge distances come from graph1 in 2nd position, and only edges with capacities >= minimum_capacity in graph2 are taken into account
    priority_q = [(0, -10.**10, origin, None)]

    parent_list = [None] * len(graph1)
    visited = [False]*len(graph1)
    best_capacity = [None] * len(graph1)

    while priority_q != []:
        distance, c, current_node, parent_node = hp.heappop(priority_q)
        capa_of_current_node = -c

        if not visited[current_node]:
            visited[current_node] = True
            parent_list[current_node] = parent_node
            best_capacity[current_node] = capa_of_current_node

            if current_node == destination:
                break

            for neighbor in graph1[current_node]:
                if not visited[neighbor] and graph2[current_node][neighbor] >= minimum_capacity:
                    hp.heappush(priority_q, (graph1[current_node][neighbor][1]+distance, -min(capa_of_current_node, graph1[current_node][neighbor][0]), neighbor, current_node))

    if parent_list[destination] is None:
        return None, None

    path = [destination]
    current_node = destination
    while current_node != origin:
        current_node = parent_list[current_node]
        path.append(current_node)
    path.reverse()

    return path, best_capacity[destination]

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
        if type(graph[node][neighbor]) is list:
            old_overload = - min(0, graph[node][neighbor][0])
            graph[node][neighbor][0] -= demand
            new_overload += - min(0, graph[node][neighbor][0]) - old_overload
        else:
            old_overload = - min(0, graph[node][neighbor])
            graph[node][neighbor] -= demand
            new_overload += - min(0, graph[node][neighbor]) - old_overload

    return new_overload

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

def remove_cycle_from_path(path):
    # Create a path where the cycles present in the input path have been removed
    is_in_path = set()
    new_path = []

    for node in path:
        if node in is_in_path:
            while new_path[-1] != node:
                node_to_remove = new_path.pop()
                is_in_path.remove(node_to_remove)

        else:
            is_in_path.add(node)
            new_path.append(node)

    return new_path


def compute_mininmum_number_of_path_changes(instance_list, initial_path_list):
    # Method that compute a solution of the dynamic unsplittable flow problem with a
    # minimim number of path changes : capacities are considered to be infinite

    nb_timesteps = len(instance_list)
    nb_commodities = len(initial_path_list)
    nb_nodes = len(instance_list[0][0])

    mininmum_number_of_path_changes = 0
    results_list = [[] for timestep in range(nb_timesteps)]

    for commodity_index, initial_path in enumerate(initial_path_list):
        for timestep, instance in enumerate(instance_list):
            graph, commodity_list = instance
            origin, destination, demand = commodity_list[commodity_index]

            if not is_correct_path(graph, commodity_list[commodity_index], initial_path):
                current_timestep = timestep
                break

        else:
            current_timestep = nb_timesteps

        for timestep in range(current_timestep):
            results_list[timestep].append(initial_path)

        while current_timestep != nb_timesteps:
            mininmum_number_of_path_changes += 1

            current_graph, current_commodity_list = instance_list[current_timestep]
            origin, destination, demand = current_commodity_list[commodity_index]
            validity_graph = [{neighbor : current_timestep for neighbor in current_graph[node]} for node in range(nb_nodes)]

            for timestep in range(current_timestep + 1, nb_timesteps):
                graph, commodity_list = instance_list[timestep]

                if destination == commodity_list[commodity_index][1]:
                    for node in range(nb_nodes):
                        for neighbor in validity_graph[node]:
                            if neighbor in graph[node] and validity_graph[node][neighbor] == timestep - 1:
                                validity_graph[node][neighbor] += 1

            path, furthest_valid_timestep = find_fitting_most_capacited_path(validity_graph, validity_graph, origin, destination, 0)

            for timestep in range(current_timestep, furthest_valid_timestep+1):
                results_list[timestep].append(path)

            current_timestep = furthest_valid_timestep + 1

    return mininmum_number_of_path_changes, results_list


def SRR_arc_path(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep=None, nb_initial_path_created=4, actualisation_threshold=None,
                    flow_penalisation=10**-5, rounding_method="round_by_timestep", verbose=1):
    # Solver that considers several timestep at a time but only a restricted amount of paths per commodity
    # A dynamic arc-path formulation is used to compute the linear relaxation
    # The SRR heuristic is used to compute an integer solution from the linear relaxation

    demand_list = [demand for origin, destination, demand in instance_list[0][1]]
    nb_commodities = len(demand_list)
    nb_timesteps = len(instance_list)
    nb_nodes = len(instance_list[0][0])
    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda commodity_index:demand_list[commodity_index])
    results_list = [[None] * nb_commodities for timestep in range(nb_timesteps)]

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes/10)
    rounding_counter = actualisation_threshold + 1

    # Creating the set of allowed paths for each commodity
    if possible_paths_per_commodity_per_timestep is None:
        all_possible_paths = [set([tuple(initial_path_list[commodity_index])]) for commodity_index in range(nb_commodities)]

        for graph, commodity_list in instance_list:
            shortest_paths_structure = {}
            for commodity_index, commodity in enumerate(commodity_list):
                origin, destination, demand = commodity

                if origin not in shortest_paths_structure:
                    shortest_paths_structure[origin] = k_shortest_path_all_destination(graph, origin, nb_initial_path_created)
                path_and_cost_list = shortest_paths_structure[origin][destination]

                for path, path_cost in path_and_cost_list:
                    path = remove_cycle_from_path(path)
                    all_possible_paths[commodity_index].add(tuple(path))

        all_possible_paths = [[list(path) for path in path_set] for path_set in all_possible_paths]
        possible_paths_per_commodity_per_timestep = [[[] for commodity_index in range(nb_commodities)] for timestep in range(len(instance_list))]
        for timestep, instance in enumerate(instance_list):
            graph, commodity_list = instance
            for commodity_index, commodity in enumerate(commodity_list):
                 for path in all_possible_paths[commodity_index]:
                     if is_correct_path(graph, commodity, path):
                         possible_paths_per_commodity_per_timestep[timestep][commodity_index].append(path)

    # Creating the dynamic arc-path formulation for the linear relaxation
    model, variables, constraints = arc_path_model(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, flow_penalisation=flow_penalisation, verbose=verbose>1)
    path_and_var_per_commodity_per_timestep, overload_var_dict, total_overload_var_dict, delta_var_dict = variables
    convexity_constraint_dict, delta_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = constraints

    # Choosing a rounding order
    sorted_commodity_indices = sorted(list(range(nb_commodities)), key= lambda commodity_index : demand_list[commodity_index]) # commodities are sorted by demand so that the biggest are assigned first and the smallest fills the gaps
    if rounding_method == "round_by_timestep":
        path_to_round_list = [(commodity_index, timestep) for timestep in range(nb_timesteps-1, -1, -1) for commodity_index in sorted_commodity_indices]
    elif rounding_method == "round_by_commodity":
        path_to_round_list = [(commodity_index, timestep) for commodity_index in sorted_commodity_indices for timestep in range(nb_timesteps-1, -1, -1)]
    elif rounding_method == "random_order":
        path_to_round_list = [(commodity_index, timestep) for commodity_index in sorted_commodity_indices for timestep in range(nb_timesteps-1, -1, -1)]
        path_to_round_list.shuffle()
    else:
        assert False, "This rounding method is not implemented, check your spelling or contribute"

    # main loop of the SRR heuristic
    while path_to_round_list:

        # at the beginning or when the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0
            model.update()
            model.optimize()

            if verbose :
                print("nb_remaining_paths_to_round = ", len(path_to_round_list))
                print(model.Objval, sum(var.X for var in overload_var_dict.values()), sum(var.X for var in delta_var_dict.values()))

        commodity_index, timestep = path_to_round_list.pop()

        # Randomized rounding step
        path_and_var = path_and_var_per_commodity_per_timestep[timestep][commodity_index]
        proba_list = np.array([max(0, var.X) for path, var in path_and_var])
        chosen_path_index = np.random.choice(len(path_and_var), p=proba_list/sum(proba_list))
        chosen_path, chosen_var = path_and_var[chosen_path_index]

        if proba_list[chosen_path_index] < 1:
            rounding_counter += 1

        results_list[timestep][commodity_index] = chosen_path
        model.addConstr(chosen_var == 1)

    model.update()
    model.optimize()

    return results_list


def SRR_arc_path2(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep=None, nb_initial_path_created=4, actualisation_threshold=None,
                    flow_penalisation=10**-5, verbose=1):
    # Solver that considers several timestep at a time but only a restricted amount of paths per commodity
    # A dynamic arc-path formulation is used to compute the linear relaxation
    # The SRR heuristic is used to compute an integer solution from the linear relaxation

    demand_list = [demand for origin, destination, demand in instance_list[0][1]]
    nb_commodities = len(demand_list)
    nb_timesteps = len(instance_list)
    nb_nodes = len(instance_list[0][0])
    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda commodity_index:demand_list[commodity_index])
    results_list = [[None] * nb_commodities for timestep in range(nb_timesteps)]

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes/10)
    rounding_counter = actualisation_threshold + 1

    # Creating the set of allowed paths for each commodity
    if possible_paths_per_commodity_per_timestep is None:
        all_possible_paths = [set([tuple(initial_path_list[commodity_index])]) for commodity_index in range(nb_commodities)]

        for graph, commodity_list in instance_list:
            shortest_paths_structure = {}
            for commodity_index, commodity in enumerate(commodity_list):
                origin, destination, demand = commodity

                if origin not in shortest_paths_structure:
                    shortest_paths_structure[origin] = k_shortest_path_all_destination(graph, origin, nb_initial_path_created)
                path_and_cost_list = shortest_paths_structure[origin][destination]

                for path, path_cost in path_and_cost_list:
                    path = remove_cycle_from_path(path)
                    all_possible_paths[commodity_index].add(tuple(path))

        all_possible_paths = [[list(path) for path in path_set] for path_set in all_possible_paths]
        possible_paths_per_commodity_per_timestep = [[[] for commodity_index in range(nb_commodities)] for timestep in range(len(instance_list))]
        for timestep, instance in enumerate(instance_list):
            graph, commodity_list = instance
            for commodity_index, commodity in enumerate(commodity_list):
                 for path in all_possible_paths[commodity_index]:
                     if is_correct_path(graph, commodity, path):
                         possible_paths_per_commodity_per_timestep[timestep][commodity_index].append(path)

    # Creating the dynamic arc-path formulation for the linear relaxation
    model, variables, constraints = arc_path_model(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, flow_penalisation=flow_penalisation, verbose=verbose>1)
    path_and_var_per_commodity_per_timestep, overload_var_dict, total_overload_var_dict, delta_var_dict = variables
    convexity_constraint_dict, delta_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = constraints

    sorted_commodity_indices = sorted(list(range(nb_commodities)), key= lambda commodity_index : demand_list[commodity_index]) # commodities are sorted by demand so that the biggest are assigned first and the smallest fills the gaps

    # main loop : 1 commodity is assigned in each iteration
    while sorted_commodity_indices:

        # at the beginning or when the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0
            model.update()
            model.optimize()

            if verbose :
                print("nb_remaining_commodities_to_round = ", len(sorted_commodity_indices))
                print(model.Objval, sum(var.X for var in overload_var_dict.values()), sum(var.X for var in delta_var_dict.values()))

        commodity_index = sorted_commodity_indices.pop()

        # Randomized rounding step : the flow of a commodity must be decomposed as a combination of path-sequences so that roundings do not create unnecessary path-changes
        path_and_amount_per_timestep = [[(path, var.X) for path, var in path_and_var_per_commodity_per_timestep[timestep][commodity_index]] for timestep in range(nb_timesteps)]
        path_sequence_and_amount = decompose_in_path_sequences(path_and_amount_per_timestep)
        proba_list = np.maximum(np.array([amount for path_sequence, amount in path_sequence_and_amount]),0)
        chosen_path_index = np.random.choice(len(path_sequence_and_amount), p=proba_list/sum(proba_list))
        chosen_path_sequence, _ = path_sequence_and_amount[chosen_path_index]

        if proba_list[chosen_path_index] < 1:
            rounding_counter += 1

        # Applying the randomized rounding decisions to the linear formulation
        for timestep in range(nb_timesteps):
            for path, var in path_and_var_per_commodity_per_timestep[timestep][commodity_index]:
                if path == chosen_path_sequence[timestep]:
                    results_list[timestep][commodity_index] = path
                    model.addConstr(var == 1)

    model.update()
    model.optimize()

    return results_list


def iterate_one_timestep_solver(instance_list, initial_path_list, one_timestep_solver, solver_keyword_arguments={}, verbose=1):
    # Take an instance over several timestep and give them one by one to SRR_arc_path_one_timestep

    nb_timesteps = len(instance_list)
    current_path_list = initial_path_list
    results_list = []

    for timestep in range(nb_timesteps):
        if verbose: print("timestep = ", timestep)
        graph, commodity_list = instance_list[timestep]
        current_path_list = one_timestep_solver(graph, commodity_list, current_path_list, **solver_keyword_arguments, verbose=verbose)
        results_list.append(current_path_list)

    return results_list


def SRR_arc_node_one_timestep(graph, commodity_list, initial_path_list, actualisation_threshold=None, flow_penalisation=10**-5, verbose=1):
    # Takes the graph and commodities of a timestep in input together with the path of the commodities in the last timestep
    # Try to minimize the overload and the number of path changes
    # The SRR heuristic is used on an arc-node formulation

    nb_commodities = len(commodity_list)
    nb_nodes = len(graph)
    demand_list = [c[2] for c in commodity_list]
    results_list = [None for commodity_index in range(nb_commodities)]

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes/10)

    # Creating the arc-node formulation
    model, variables, constraints  = arc_node_one_timestep_model(graph, commodity_list, initial_path_list, flow_penalisation=flow_penalisation, verbose=verbose>1)
    initial_path_var, flow_var, overload_var, total_overload_var, delta_var = variables
    delta_constraint_dict, linking_constraint_dict, flow_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = constraints

    model.update()
    model.optimize()
    if verbose : print("Objval = ", model.Objval)
    # Extracting the information necessary for the randomized rounding from the solution of the linear relaxation
    allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)

    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda x : demand_list[x])
    rounding_counter = 0

    # Main loop : one commodity is assigned at each iteration
    while sorted_commodity_indices:
        commodity_index = sorted_commodity_indices.pop()
        origin, destination, demand = commodity_list[commodity_index]
        allocation_graph = allocation_graph_per_origin[origin]
        if verbose:
            print("#####################", len(sorted_commodity_indices), demand, end='   \r')

        if commodity_index in initial_path_values:
            initial_path_used_capacity = demand * initial_path_values[commodity_index]
        else:
            initial_path_used_capacity = 0

        # Finding the path used by the commodity
        remaining_demand = demand - initial_path_used_capacity
        path_list = [initial_path_list[commodity_index]]
        used_capacity_list = [initial_path_used_capacity]
        while remaining_demand > 10**-6:
            path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, demand)
            if path is None or path_capacity <= 10**-5:
                path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, -10**10)

            used_capacity = min(path_capacity, remaining_demand)
            path_list.append(path)
            used_capacity_list.append(used_capacity)
            remaining_demand -= used_capacity
            update_graph_capacity(allocation_graph, path, used_capacity)

        if len(path_list) > 1:
            rounding_counter += 1

        # Choose a path for the commodity
        #proba_list = np.array(used_capacity_list) / sum(used_capacity_list)
        #chosen_path_index = np.random.choice(len(path_list), p=proba_list)
        chosen_path_index = np.where(used_capacity_list == np.max(used_capacity_list))[0][0]
        chosen_path = path_list[chosen_path_index]

        # allcoate the commodity and update the capacities in different graphs
        update_graph_capacity(remaining_capacity_graph, chosen_path, demand)
        results_list[commodity_index] = chosen_path

        # change the linear model to take into account a path fixing
        flow_constraint_dict[origin, origin].RHS -= demand
        flow_constraint_dict[origin, destination].RHS += demand


        if commodity_index in initial_path_var:
            model.addConstr((initial_path_var[commodity_index] == 0))

        for node_index in range(len(chosen_path)-1):
            node, neighbor = chosen_path[node_index], chosen_path[node_index + 1]
            capacity_constraint_dict[node, neighbor].RHS -= demand

        # THIS IS IMPORTANT
        model.update()

        # When the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0

            model.update()
            model.optimize()

            if verbose : print("Objval = ", model.Objval)

            allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)


    return results_list

def SRR_arc_node_one_timestep_shorter(graph, commodity_list, initial_path_list, actualisation_threshold=None, flow_penalisation=10**-5, verbose=1):
    # Takes the graph and commodities of a timestep in input together with the path of the commodities in the last timestep
    # Try to minimize the overload and the number of path changes
    # Tries to reduce distance from above algo
    # The SRR heuristic is used on an arc-node formulation

    nb_commodities = len(commodity_list)
    nb_nodes = len(graph)
    demand_list = [c[2] for c in commodity_list]
    results_list = [None for commodity_index in range(nb_commodities)]

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes/10)

    # Creating the arc-node formulation
    model, variables, constraints  = arc_node_one_timestep_model(graph, commodity_list, initial_path_list, flow_penalisation=flow_penalisation, verbose=verbose>1)
    initial_path_var, flow_var, overload_var, total_overload_var, delta_var = variables
    delta_constraint_dict, linking_constraint_dict, flow_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = constraints

    model.update()
    model.optimize()
    if verbose : print("Objval = ", model.Objval)
    # Extracting the information necessary for the randomized rounding from the solution of the linear relaxation
    allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)

    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda x : demand_list[x])
    rounding_counter = 0

    # Main loop : one commodity is assigned at each iteration
    while sorted_commodity_indices:
        commodity_index = sorted_commodity_indices.pop()
        origin, destination, demand = commodity_list[commodity_index]
        allocation_graph = allocation_graph_per_origin[origin]
        if verbose:
            print("#####################", len(sorted_commodity_indices), demand, end='   \r')

        if commodity_index in initial_path_values:
            initial_path_used_capacity = demand * initial_path_values[commodity_index]
        else:
            initial_path_used_capacity = 0

        # Finding the path used by the commodity
        remaining_demand = demand - initial_path_used_capacity
        path_list = [initial_path_list[commodity_index]]
        used_capacity_list = [initial_path_used_capacity]
        #try to get shortest path
        chosen_path, path_capacity = find_fitting_shortest_path(allocation_graph, remaining_capacity_graph, origin, destination, demand)
        if chosen_path is not None:#we found a good solution
            #try to find out if there are other possibilities
            used_capacity = min(path_capacity, remaining_demand)
            update_graph_capacity(allocation_graph, chosen_path, used_capacity)
            otherpossible, _ = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, demand)
            rounding_counter += (otherpossible != None)#increment rounding counter if there are other possibilities
        else: #otherwise, try to find the best capacity path
            while remaining_demand > 10**-6:
                path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, demand)
                if path is None or path_capacity <= 10**-5:
                    path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, -10**10)

                used_capacity = min(path_capacity, remaining_demand)
                path_list.append(path)
                used_capacity_list.append(used_capacity)
                remaining_demand -= used_capacity
                update_graph_capacity(allocation_graph, path, used_capacity)

            if len(path_list) > 1:
                rounding_counter += 1

            # Choose a path for the commodity
            proba_list = np.array(used_capacity_list) / sum(used_capacity_list)
            chosen_path_index = np.random.choice(len(path_list), p=proba_list)
            chosen_path = path_list[chosen_path_index]

        # allcoate the commodity and update the capacities in different graphs
        update_graph_capacity(remaining_capacity_graph, chosen_path, demand)
        results_list[commodity_index] = chosen_path

        # change the linear model to take into account a path fixing
        flow_constraint_dict[origin, origin].RHS -= demand
        flow_constraint_dict[origin, destination].RHS += demand


        if commodity_index in initial_path_var:
            model.addConstr((initial_path_var[commodity_index] == 0))

        for node_index in range(len(chosen_path)-1):
            node, neighbor = chosen_path[node_index], chosen_path[node_index + 1]
            capacity_constraint_dict[node, neighbor].RHS -= demand

        # THIS IS IMPORTANT
        model.update()

        # When the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0

            model.update()
            model.optimize()

            if verbose : print("Objval = ", model.Objval)

            allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)


    return results_list

def SRR_arc_node_one_timestep_shorterc(graph, commodity_list, initial_path_list, actualisation_threshold=None, flow_penalisation=10**-5, verbose=1):
    # Takes the graph and commodities of a timestep in input together with the path of the commodities in the last timestep
    # Try to minimize the overload and the number of path changes
    # Tries to reduce distance from above algo
    # The SRR heuristic is used on an arc-node formulation

    nb_commodities = len(commodity_list)
    nb_nodes = len(graph)
    demand_list = [c[2] for c in commodity_list]
    results_list = [None for commodity_index in range(nb_commodities)]

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes/10)

    # Creating the arc-node formulation
    model, variables, constraints  = arc_node_one_timestep_model_b(graph, commodity_list, initial_path_list, flow_penalisation=flow_penalisation, verbose=verbose>1)
    initial_path_var, flow_var, overload_var, total_overload_var, delta_var = variables
    delta_constraint_dict, linking_constraint_dict, flow_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = constraints

    model.update()
    model.optimize()
    if verbose : print("Objval = ", model.Objval)
    # Extracting the information necessary for the randomized rounding from the solution of the linear relaxation
    allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)

    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda x : demand_list[x])
    rounding_counter = 0

    # Main loop : one commodity is assigned at each iteration
    while sorted_commodity_indices:
        commodity_index = sorted_commodity_indices.pop()
        origin, destination, demand = commodity_list[commodity_index]
        allocation_graph = allocation_graph_per_origin[origin]
        if verbose:
            print("#####################", len(sorted_commodity_indices), demand, end='   \r')

        if commodity_index in initial_path_values:
            initial_path_used_capacity = demand * initial_path_values[commodity_index]
        else:
            initial_path_used_capacity = 0

        # Finding the path used by the commodity
        # Finding the path used by the commodity
        remaining_demand = demand - initial_path_used_capacity
        path_list = [initial_path_list[commodity_index]]
        used_capacity_list = [initial_path_used_capacity]
        while remaining_demand > 10**-6:
            path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, demand)
            if path is None or path_capacity <= 10**-5:
                path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, -10**10)

            used_capacity = min(path_capacity, remaining_demand)
            path_list.append(path)
            used_capacity_list.append(used_capacity)
            remaining_demand -= used_capacity
            update_graph_capacity(allocation_graph, path, used_capacity)

        if len(path_list) > 1:
            rounding_counter += 1
        
        # Choose a path for the commodity
        #proba_list = np.array(used_capacity_list) / sum(used_capacity_list)
        #chosen_path_index = np.random.choice(len(path_list), p=proba_list)
        chosen_path_index = np.where(used_capacity_list == np.max(used_capacity_list))[0][0]
        chosen_path = path_list[chosen_path_index]
        
        # allcoate the commodity and update the capacities in different graphs
        update_graph_capacity(remaining_capacity_graph, chosen_path, demand)
        results_list[commodity_index] = chosen_path

        # change the linear model to take into account a path fixing
        flow_constraint_dict[origin, origin].RHS -= demand
        flow_constraint_dict[origin, destination].RHS += demand


        if commodity_index in initial_path_var:
            model.addConstr((initial_path_var[commodity_index] == 0))

        for node_index in range(len(chosen_path)-1):
            node, neighbor = chosen_path[node_index], chosen_path[node_index + 1]
            capacity_constraint_dict[node, neighbor].RHS -= demand

        # THIS IS IMPORTANT
        model.update()

        # When the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0

            model.update()
            model.optimize()

            if verbose : print("Objval = ", model.Objval)

            allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)


    return results_list

def SRR_arc_node_one_timestep_shorterd(graph, commodity_list, initial_path_list, actualisation_threshold=None, flow_penalisation=10**-5, verbose=1):
    # Takes the graph and commodities of a timestep in input together with the path of the commodities in the last timestep
    # Try to minimize the overload and the number of path changes
    # Tries to reduce distance from above algo
    # The SRR heuristic is used on an arc-node formulation

    nb_commodities = len(commodity_list)
    nb_nodes = len(graph)
    demand_list = [c[2] for c in commodity_list]
    results_list = [None for commodity_index in range(nb_commodities)]

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes/10)

    # Creating the arc-node formulation
    model, variables, constraints  = arc_node_one_timestep_model(graph, commodity_list, initial_path_list, flow_penalisation=flow_penalisation, verbose=verbose>1)
    initial_path_var, flow_var, overload_var, total_overload_var, delta_var = variables
    delta_constraint_dict, linking_constraint_dict, flow_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = constraints

    model.update()
    model.optimize()
    if verbose : print("Objval = ", model.Objval)
    # Extracting the information necessary for the randomized rounding from the solution of the linear relaxation
    allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)

    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda x : demand_list[x])
    rounding_counter = 0

    # Main loop : one commodity is assigned at each iteration
    while sorted_commodity_indices:
        commodity_index = sorted_commodity_indices.pop()
        origin, destination, demand = commodity_list[commodity_index]
        allocation_graph = allocation_graph_per_origin[origin]
        if verbose:
            print("#####################", len(sorted_commodity_indices), demand, end='   \r')

        if commodity_index in initial_path_values:
            initial_path_used_capacity = demand * initial_path_values[commodity_index]
        else:
            initial_path_used_capacity = 0

        # Finding the path used by the commodity
        remaining_demand = demand - initial_path_used_capacity
        path_list = [initial_path_list[commodity_index]]
        used_capacity_list = [initial_path_used_capacity]
        while remaining_demand > 10**-6:
            #try to get shortest path
            path, path_capacity = find_fitting_shortest_path(allocation_graph, remaining_capacity_graph, origin, destination, demand)
            #else other algos
            if path is None or path_capacity <= 10**-5:
                path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, demand)
                if path is None or path_capacity <= 10**-5:
                    path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, -10**10)

            used_capacity = min(path_capacity, remaining_demand)
            path_list.append(path)
            used_capacity_list.append(used_capacity)
            remaining_demand -= used_capacity
            update_graph_capacity(allocation_graph, path, used_capacity)

            if len(path_list) > 1:
                rounding_counter += 1

            # Choose a path for the commodity
            proba_list = np.array(used_capacity_list) / sum(used_capacity_list)
            chosen_path_index = np.random.choice(len(path_list), p=proba_list)
            chosen_path = path_list[chosen_path_index]

        # allcoate the commodity and update the capacities in different graphs
        update_graph_capacity(remaining_capacity_graph, chosen_path, demand)
        results_list[commodity_index] = chosen_path

        # change the linear model to take into account a path fixing
        flow_constraint_dict[origin, origin].RHS -= demand
        flow_constraint_dict[origin, destination].RHS += demand


        if commodity_index in initial_path_var:
            model.addConstr((initial_path_var[commodity_index] == 0))

        for node_index in range(len(chosen_path)-1):
            node, neighbor = chosen_path[node_index], chosen_path[node_index + 1]
            capacity_constraint_dict[node, neighbor].RHS -= demand

        # THIS IS IMPORTANT
        model.update()

        # When the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0

            model.update()
            model.optimize()

            if verbose : print("Objval = ", model.Objval)

            allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)


    return results_list

def SRR_arc_node_one_timestep_shortere(graph, commodity_list, initial_path_list, actualisation_threshold=None, flow_penalisation=10**-5, verbose=1):
    # Takes the graph and commodities of a timestep in input together with the path of the commodities in the last timestep
    # Try to minimize the overload and the number of path changes
    # Tries to reduce distance from above algo
    # The SRR heuristic is used on an arc-node formulation

    nb_commodities = len(commodity_list)
    nb_nodes = len(graph)
    demand_list = [c[2] for c in commodity_list]
    results_list = [None for commodity_index in range(nb_commodities)]

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes/10)

    # Creating the arc-node formulation
    model, variables, constraints  = arc_node_one_timestep_model(graph, commodity_list, initial_path_list, flow_penalisation=flow_penalisation, verbose=verbose>1)
    initial_path_var, flow_var, overload_var, total_overload_var, delta_var = variables
    delta_constraint_dict, linking_constraint_dict, flow_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = constraints

    model.update()
    model.optimize()
    if verbose : print("Objval = ", model.Objval)
    # Extracting the information necessary for the randomized rounding from the solution of the linear relaxation
    allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)

    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda x : demand_list[x])
    rounding_counter = 0

    # Main loop : one commodity is assigned at each iteration
    while sorted_commodity_indices:
        commodity_index = sorted_commodity_indices.pop()
        origin, destination, demand = commodity_list[commodity_index]
        allocation_graph = allocation_graph_per_origin[origin]
        if verbose:
            print("#####################", len(sorted_commodity_indices), demand, end='   \r')

        #do as if the initial path was not set
        initial_path_used_capacity = 0

        # Finding the path used by the commodity
        remaining_demand = demand - initial_path_used_capacity
        path_list = [initial_path_list[commodity_index]]
        used_capacity_list = [initial_path_used_capacity]
        while remaining_demand > 10**-6:   
            path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, demand)
            if path is None or path_capacity <= 10**-5:
                path, path_capacity = find_fitting_most_capacited_path(allocation_graph, remaining_capacity_graph, origin, destination, -10**10)

            used_capacity = min(path_capacity, remaining_demand)
            path_list.append(path)
            used_capacity_list.append(used_capacity)
            remaining_demand -= used_capacity
            update_graph_capacity(allocation_graph, path, used_capacity)

            if len(path_list) > 1:
                rounding_counter += 1

            # Choose a path for the commodity
            proba_list = np.array(used_capacity_list) / sum(used_capacity_list)
            chosen_path_index = np.random.choice(len(path_list), p=proba_list)
            chosen_path = path_list[chosen_path_index]

        # allcoate the commodity and update the capacities in different graphs
        update_graph_capacity(remaining_capacity_graph, chosen_path, demand)
        results_list[commodity_index] = chosen_path

        # change the linear model to take into account a path fixing
        flow_constraint_dict[origin, origin].RHS -= demand
        flow_constraint_dict[origin, destination].RHS += demand


        if commodity_index in initial_path_var:
            model.addConstr((initial_path_var[commodity_index] == 0))

        for node_index in range(len(chosen_path)-1):
            node, neighbor = chosen_path[node_index], chosen_path[node_index + 1]
            capacity_constraint_dict[node, neighbor].RHS -= demand

        # THIS IS IMPORTANT
        model.update()

        # When the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0

            model.update()
            model.optimize()

            if verbose : print("Objval = ", model.Objval)

            allocation_graph_per_origin, remaining_capacity_graph, initial_path_values = extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list)


    return results_list

def compute_possible_paths_per_commodity(graph, commodity_list, initial_path_list, nb_initial_path_created):
     # Extract the information necessary for the randomized rounding from the solution of the linear relaxation
    shortest_paths_per_origin = {}
    possible_paths_per_commodity = []

    for commodity_index, commodity in enumerate(commodity_list):
        origin, destination, demand = commodity
        initial_path = initial_path_list[commodity_index]

        if origin not in shortest_paths_per_origin:
            shortest_paths_per_origin[origin] = k_shortest_path_all_destination(graph, origin, nb_initial_path_created)

        path_and_cost_list = shortest_paths_per_origin[origin][destination]
        possible_paths_per_commodity.append(set(tuple(remove_cycle_from_path(path)) for path, path_cost in path_and_cost_list))

        if is_correct_path(graph, commodity, initial_path):
            possible_paths_per_commodity[commodity_index].add(tuple(initial_path))

        possible_paths_per_commodity[commodity_index] = [list(path_tuple) for path_tuple in possible_paths_per_commodity[commodity_index]]

    return possible_paths_per_commodity


def SRR_arc_path_one_timestep(graph, commodity_list, initial_path_list, possible_paths_per_commodity=None, nb_initial_path_created=4, nb_path_generations=10**10,
                                actualisation_threshold=None, var_delete_proba=0.3, flow_penalisation=10**-5, verbose=1):
    # Takes the graph and commodities of a timestep in input together with the path of the commodities in the last timestep
    # Try to minimize the overload and the number of path changes
    # The SRR heuristic is used on an arc-path formulation

    nb_nodes = len(graph)
    nb_commodities = len(commodity_list)
    demand_list = [demand for origin, destination, demand in commodity_list]
    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda commodity_index:demand_list[commodity_index])
    results = [None] * nb_commodities

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes/10)
    rounding_counter = actualisation_threshold + 1

    # Compute the initial set of allowed paths for each commodity
    if possible_paths_per_commodity is None:
        possible_paths_per_commodity = compute_possible_paths_per_commodity(graph, commodity_list, initial_path_list, nb_initial_path_created)

    # Creating the arc-path model
    model, variables, constraints = arc_path_one_timestep_model(graph, commodity_list, initial_path_list, possible_paths_per_commodity, flow_penalisation=flow_penalisation, verbose=verbose>1)
    path_and_var_per_commodity, delta_var, overload_var, total_overload_var = variables
    convexity_constraint_dict, capacity_constraint_dict, total_capacity_constraint, delta_constraint_dict = constraints

    while sorted_commodity_indices != []:

        # At the beginning or when the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            if verbose : print("###################")
            rounding_counter = 0
            nb_remaining_path_generations = nb_path_generations

            while True:

                model.update()
                model.optimize()
                if verbose : print(len(sorted_commodity_indices), model.Objval, sum(var.X for var in overload_var.values()))

                if nb_remaining_path_generations == 0:
                    break

                for commodity_index, path_and_var in enumerate(path_and_var_per_commodity):
                    new_path_and_var = []

                    for path, var in path_and_var:
                        if var.Vbasis != 0 and random.random() < var_delete_proba:
                            model.remove(var)
                        else:
                            new_path_and_var.append((path, var))

                    path_and_var_per_commodity[commodity_index] = new_path_and_var

                is_new_path_added = generate_new_paths(graph, commodity_list, model, capacity_constraint_dict, convexity_constraint_dict, path_and_var_per_commodity, flow_penalisation=flow_penalisation)
                nb_remaining_path_generations -= 1

                if is_new_path_added == 0:
                    break

        commodity_index = sorted_commodity_indices.pop()

        # Randomized rounding
        path_and_var = path_and_var_per_commodity[commodity_index]
        proba_list = np.array([max(0, var.X) for path, var in path_and_var])
        chosen_path_index = np.random.choice(len(path_and_var), p=proba_list/sum(proba_list))
        chosen_path, chosen_var = path_and_var[chosen_path_index]

        if proba_list[chosen_path_index] < 1:
            rounding_counter += 1

        # Applying the randomized rounding decisions to the linear formulation
        results[commodity_index] = chosen_path
        model.addConstr(chosen_var == 1)

    model.update()
    model.optimize()

    return results


def Branch_and_Bound_arc_path_one_timestep(graph, commodity_list, initial_path_list, possible_paths_per_commodity=None, nb_initial_path_created=4,
                                            nb_new_binary_var=None, time_limit=None, flow_penalisation=10**-5, nb_threads=0, verbose=1):
    # Takes the graph and commodities of a timestep in input together with the path of the commodities in the last timestep
    # Try to minimize the overload and the number of path changes
    # The Branch and Bound is used on an arc-path formulation with a restricted number of paths for each commodity
    nb_commodities = len(initial_path_list)
    nb_nodes = len(graph)
    demand_list = [commodity[2] for commodity in commodity_list]

    if time_limit is None:
        time_limit = 10**10

    # Compute the initial set of allowed paths for each commodity
    if possible_paths_per_commodity is None:
        possible_paths_per_commodity = compute_possible_paths_per_commodity(graph, commodity_list, initial_path_list, nb_initial_path_created)

    # Creating the arc-path model
    model, variables, constraints = arc_path_one_timestep_model(graph, commodity_list, initial_path_list, possible_paths_per_commodity, flow_penalisation=flow_penalisation, verbose=verbose>1)
    path_and_var_per_commodity, delta_var, overload_var, total_overload_var = variables
    convexity_constraint_dict, capacity_constraint_dict, total_capacity_constraint, delta_constraint_dict = constraints

    model.Params.TimeLimit = time_limit
    model.Params.MIPGap = 10**-2
    model.Params.Threads = nb_threads
    model.Params.MIPFocus = 1

    if nb_new_binary_var is None:
        nb_new_binary_var = nb_commodities

    sorted_commodity_indices = sorted(list(range(nb_commodities)), key=lambda x : demand_list[x])
    results_list = [None]*nb_commodities

    while sorted_commodity_indices:
        if verbose : print(len(sorted_commodity_indices))

        # some variables of the model become binary variables
        var_to_constrain = []
        for i in range(min(nb_new_binary_var, len(sorted_commodity_indices))):
            commodity_index = sorted_commodity_indices.pop()
            var_to_constrain.append(commodity_index)

            for path, var in path_and_var_per_commodity[commodity_index]:
                var.VType = 'B'

        model.update()
        model.optimize()

        # change the linear model to take into account a path fixing
        for commodity_index in var_to_constrain:
            for path, var in path_and_var_per_commodity[commodity_index]:
                if var.X > 0.999:
                    model.addConstr((var == 1))
                    results_list[commodity_index] = path

    return results_list


def SRR_path_combinations(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep=None, nb_initial_path_created=4, actualisation_threshold=None,
                            exact_var_generation=True, flow_penalisation=10**-5, verbose=0):
    # Solver that considers several timestep at a time
    # A path-sequence formulation is used to compute the linear relaxation
    # the column generation part is dealt with in the file mcnf_dynamic_column_generation.py
    # The SRR heuristic is used to compute an integer solution from the linear relaxation

    nb_commodities = len(initial_path_list)
    nb_timesteps = len(instance_list)
    nb_nodes = len(instance_list[0][0])
    demand_list = [c[2] for c in instance_list[0][1]]

    if actualisation_threshold is None:
        actualisation_threshold = int(nb_nodes)

    # Creating the initial set of paths allowed for each commodity at each timestep
    if possible_paths_per_commodity_per_timestep is None:
        if exact_var_generation:
            nb_initial_path_created = 1

        all_possible_paths = [set([tuple(initial_path_list[commodity_index])]) for commodity_index in range(nb_commodities)]

        for graph, commodity_list in instance_list:
            shortest_paths_structure = {}
            for commodity_index, commodity in enumerate(commodity_list):
                origin, destination, demand = commodity

                if origin not in shortest_paths_structure:
                    shortest_paths_structure[origin] = k_shortest_path_all_destination(graph, origin, nb_initial_path_created)
                path_and_cost_list = shortest_paths_structure[origin][destination]

                for path, path_cost in path_and_cost_list:
                    all_possible_paths[commodity_index].add(tuple(remove_cycle_from_path(path)))

        all_possible_paths = [[list(path) for path in path_set] for path_set in all_possible_paths]
        possible_paths_per_commodity_per_timestep = [[[] for commodity_index in range(nb_commodities)] for timestep in range(len(instance_list))]
        for timestep, instance in enumerate(instance_list):
            graph, commodity_list = instance
            for commodity_index, commodity in enumerate(commodity_list):
                 for path in all_possible_paths[commodity_index]:
                     if is_correct_path(graph, commodity, path):
                         possible_paths_per_commodity_per_timestep[timestep][commodity_index].append(path)

    # Creating the path-sequence formulation
    model, model_attributes = create_column_generation_model(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, verbose=0)

    combination_and_var_per_commodity, overload_var, convexity_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = model_attributes

    # Initial resolution of the linear relaxation
    run_column_generation(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, model, model_attributes,
                            exact_var_generation=exact_var_generation, flow_penalisation=flow_penalisation, verbose=verbose)

    sorted_commodity_indices = sorted(list(range(nb_commodities)), key= lambda commodity_index : demand_list[commodity_index]) # commodities are sorted by demand so that the biggest are assigned first and the smallest fills the gaps

    results_list = [[None]*nb_commodities for timestep in range(nb_timesteps)]
    rounding_counter = 0

    # main loop : one commodity is assigned in each iteration
    while sorted_commodity_indices != []:

        # at the beginning or when the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0
            if verbose : print("nb_remaining_commodities = ", len(sorted_commodity_indices),
                                " remaining_demand = ", sum([demand_list[commodity_index] for commodity_index in sorted_commodity_indices]))

            run_column_generation(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, model, model_attributes,
                                changeable_commodities_indices=sorted_commodity_indices, exact_var_generation=exact_var_generation, flow_penalisation=flow_penalisation, verbose=verbose)

        commodity_index = sorted_commodity_indices.pop()

        # Randomized rounding step
        possible_combinations = combination_and_var_per_commodity[commodity_index]
        proba_list = np.array([max(0, var.X) for combination, var in possible_combinations])
        chosen_combination_index = np.random.choice(len(possible_combinations), p=proba_list/sum(proba_list))
        chosen_combination, chosen_var = possible_combinations[chosen_combination_index]

        if True or chosen_var.X < 0.99:
            rounding_counter += 1

        # update the column generation model to account for the path fixing
        model.addConstr((chosen_var == 1))
        for timestep, path in enumerate(chosen_combination):
            results_list[timestep][commodity_index] = path


    model.update()
    model.optimize()

    return results_list


def SRR_path_combinations2(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep=None, nb_initial_path_created=4, actualisation_threshold=None,
                            exact_var_generation=True, rounding_method="round_by_commodity", flow_penalisation=10**-5, verbose=0):
    # Solver that considers several timestep at a time
    # A path-sequence formulation is used to compute the linear relaxation
    # the column generation part is dealt with in the file mcnf_dynamic_column_generation.py
    # The SRR heuristic is used to compute an integer solution from the linear relaxation

    nb_commodities = len(initial_path_list)
    nb_timesteps = len(instance_list)
    nb_nodes = len(instance_list[0][0])
    demand_list = [c[2] for c in instance_list[0][1]]

    if actualisation_threshold is None:
        # actualisation_threshold = int(nb_commodities * 0.2)
        actualisation_threshold = nb_nodes

    # Creating the initial set of paths allowed for each commodity at each timestep
    if possible_paths_per_commodity_per_timestep is None:
        if exact_var_generation:
            nb_initial_path_created = 1

        all_possible_paths = [set([tuple(initial_path_list[commodity_index])]) for commodity_index in range(nb_commodities)]

        for graph, commodity_list in instance_list:
            shortest_paths_structure = {}
            for commodity_index, commodity in enumerate(commodity_list):
                origin, destination, demand = commodity

                if origin not in shortest_paths_structure:
                    shortest_paths_structure[origin] = k_shortest_path_all_destination(graph, origin, nb_initial_path_created)
                path_and_cost_list = shortest_paths_structure[origin][destination]

                for path, path_cost in path_and_cost_list:
                    all_possible_paths[commodity_index].add(tuple(remove_cycle_from_path(path)))

        all_possible_paths = [[list(path) for path in path_set] for path_set in all_possible_paths]
        possible_paths_per_commodity_per_timestep = [[[] for commodity_index in range(nb_commodities)] for timestep in range(len(instance_list))]
        for timestep, instance in enumerate(instance_list):
            graph, commodity_list = instance
            for commodity_index, commodity in enumerate(commodity_list):
                 for path in all_possible_paths[commodity_index]:
                     if is_correct_path(graph, commodity, path):
                         possible_paths_per_commodity_per_timestep[timestep][commodity_index].append(path)

    # Creating the path-sequence formulation
    model, model_attributes = create_column_generation_model(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, verbose=0)

    combination_and_var_per_commodity, overload_var, convexity_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict = model_attributes

    # Initial resolution of the linear relaxation
    run_column_generation(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, model, model_attributes, nb_iterations=20,
                            exact_var_generation=exact_var_generation, flow_penalisation=flow_penalisation, verbose=verbose>1)

    results_list = [[None]*nb_commodities for timestep in range(nb_timesteps)]
    rounding_counter = 0

    # Choosing a rounding order
    sorted_commodity_indices = sorted(list(range(nb_commodities)), key= lambda commodity_index : demand_list[commodity_index]) # commodities are sorted by demand so that the biggest are assigned first and the smallest fills the gaps
    if rounding_method == "round_by_timestep":
        path_to_round_list = [(commodity_index, timestep) for timestep in range(nb_timesteps-1, -1, -1) for commodity_index in sorted_commodity_indices]
    elif rounding_method == "round_by_commodity":
        path_to_round_list = [(commodity_index, timestep) for commodity_index in sorted_commodity_indices for timestep in range(nb_timesteps-1, -1, -1)]
    elif rounding_method == "random_order":
        path_to_round_list = [(commodity_index, timestep) for commodity_index in sorted_commodity_indices for timestep in range(nb_timesteps-1, -1, -1)]
        path_to_round_list.shuffle()
    else:
        assert False, "This rounding method is not implemented, check your spelling or contribute"

    # main loop of the SRR heuristic
    while path_to_round_list:

        # at the beginning or when the solution deviates to much from the the previously computed continuous solution :
        # compute a new continuous solution with the non assigned commodities
        if rounding_counter > actualisation_threshold:
            rounding_counter = 0

            if verbose :
                print("nb_remaining_paths_to_round = ", len(path_to_round_list))

            run_column_generation(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, model, model_attributes, nb_iterations=3,
                                fixed_paths_per_commodity_per_timestep=results_list, exact_var_generation=exact_var_generation, flow_penalisation=flow_penalisation,
                                verbose=verbose>1)

        commodity_index, timestep = path_to_round_list.pop()
        possible_combinations = combination_and_var_per_commodity[commodity_index]

        # Randomized rounding step
        proba_list = np.array([max(0, var.X) for combination, var in possible_combinations])
        chosen_combination_index = np.random.choice(len(possible_combinations), p=proba_list/sum(proba_list))
        chosen_combination, chosen_var = possible_combinations[chosen_combination_index]
        chosen_path = chosen_combination[timestep]

        results_list[timestep][commodity_index] = chosen_path
        rounding_counter += 1

        # update the column generation model to account for the path fixing
        remaining_combinations = []
        for combination, var in possible_combinations:
            if combination[timestep] != chosen_path:
                model.remove(var)
            else:
                remaining_combinations.append((combination, var))

        combination_and_var_per_commodity[commodity_index] = remaining_combinations

    model.update()
    model.optimize()

    return results_list
