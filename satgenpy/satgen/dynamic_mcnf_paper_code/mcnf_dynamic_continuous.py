import heapq as hp
import random
import numpy as np
import time
import gurobipy

from .k_shortest_path import k_shortest_path_all_destination

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


def compute_all_shortest_path(graph, origin_list):
    nb_nodes = len(graph)
    all_shortest_path = {}

    for origin in origin_list:
        parent_list, distances = dijkstra(graph, origin)
        shortest_path_list = [None for node in range(nb_nodes)]
        shortest_path_list[origin] = [origin]

        for node in range(nb_nodes):
            if shortest_path_list[node] is None and parent_list[node] is not None:
                compute_shortest_path(shortest_path_list, parent_list, node)

        all_shortest_path[origin] = [(shortest_path_list[node], distances[node]) for node in range(nb_nodes)]

    return all_shortest_path


def compute_shortest_path(shortest_path_list, parent_list, node):
    parent = parent_list[node]
    if shortest_path_list[parent] is None:
        compute_shortest_path(shortest_path_list, parent_list, parent)

    shortest_path_list[node] = shortest_path_list[parent] + [node]


def is_correct_path(graph, commodity, path_tuple):
    # function that checks if a path_tuple is valid for a commodity in an instance

    origin, destination, demand = commodity
    is_correct =  path_tuple[0] == origin and path_tuple[-1] == destination

    for node_index in range(len(path_tuple)-1):
        node, neighbor = path_tuple[node_index], path_tuple[node_index+1]
        is_correct = is_correct and neighbor in graph[node]
        if not is_correct:
            break

    return is_correct


def decompose_in_path_sequences(path_and_amount_per_timestep):
    # Decomposes a distribution of flow into a combination of path-sequences
    nb_timesteps = len(path_and_amount_per_timestep)
    path_sequence_and_amount = [([path_tuple], amount) for path_tuple, amount in path_and_amount_per_timestep[0]]

    for timestep in range(1, nb_timesteps):
        path_and_amount_dict = {tuple(path_tuple) : amount for path_tuple, amount in path_and_amount_per_timestep[timestep]}
        new_path_sequences_and_amount = []
        temp_path_sequence_and_amount = []

        for path_sequence, sequence_amount in path_sequence_and_amount:
            last_path_tuple = tuple(path_sequence[-1])

            if last_path_tuple in path_and_amount_dict and path_and_amount_dict[last_path_tuple] > 0:
                if sequence_amount <= path_and_amount_dict[last_path_tuple]:
                    new_path_sequences_and_amount.append((path_sequence + [list(last_path_tuple)], sequence_amount))
                    path_and_amount_dict[last_path_tuple] -= sequence_amount
                else:
                    new_path_sequences_and_amount.append((path_sequence + [list(last_path_tuple)], path_and_amount_dict[last_path_tuple]))
                    temp_path_sequence_and_amount.append((path_sequence, sequence_amount - path_and_amount_dict[last_path_tuple]))
                    path_and_amount_dict[last_path_tuple] = 0
            else:
                temp_path_sequence_and_amount.append((path_sequence, sequence_amount))

        path_sequence_and_amount = temp_path_sequence_and_amount

        for path_tuple in path_and_amount_dict:
            amount = path_and_amount_dict[path_tuple]

            while amount > 10**-6:
                path_sequence, sequence_amount = path_sequence_and_amount.pop()

                if sequence_amount <= amount:
                    new_path_sequences_and_amount.append((path_sequence + [list(path_tuple)], sequence_amount))
                    amount -= sequence_amount
                else:
                    new_path_sequences_and_amount.append((path_sequence + [list(path_tuple)], amount))
                    path_sequence_and_amount.append((path_sequence, sequence_amount - amount))
                    amount = 0

        path_sequence_and_amount = new_path_sequences_and_amount

    return path_sequence_and_amount


def arc_path_model(instance_list, initial_path_list, possible_paths_per_commodity_per_timestep, flow_penalisation=0, verbose=1):
    # Linear formulation that solve the linear relaxation of the dynamic problem with a compact formulation
    nb_commodities = len(initial_path_list)
    nb_timesteps = len(instance_list)
    nb_nodes = len(instance_list[0][0])
    demand_list = [c[2] for c in instance_list[0][1]]
    arc_list = [(timestep, node, neighbor) for timestep in range(nb_timesteps) for node in range(nb_nodes) for neighbor in instance_list[timestep][0][node]]

    # Create optimization model
    model = gurobipy.Model('netflow')
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.Params.OutputFlag = verbose
    model.Params.Method = 2

    # Create variables
    path_and_var_per_commodity_per_timestep = [[[(path_tuple, model.addVar(obj=flow_penalisation * (len(path_tuple)-1))) for path_tuple in possible_paths] for possible_paths in possible_paths_per_commodity] for possible_paths_per_commodity in possible_paths_per_commodity_per_timestep]
    delta_var_dict = {}
    overload_var_dict = model.addVars(arc_list, name="lambda")
    total_overload_var_dict = model.addVars(nb_timesteps, obj=1)
    print("variables created")

    # Convexity constraints :
    convexity_constraint_dict = model.addConstrs((sum(var for path_tuple, var in path_and_var_per_commodity_per_timestep[timestep][commodity_index]) == 1 for commodity_index in range(nb_commodities) for timestep in range(nb_timesteps)), "convexity")
    print("Convexity constraints created")

    # Creating capacity constraint
    capacity_constraint_dict = {}
    total_capacity_constraint_dict = {}
    for timestep, path_and_var_per_commodity in enumerate(path_and_var_per_commodity_per_timestep):
        graph, commodity_list = instance_list[timestep]
        edge_use_dict = {(node, neighbor): gurobipy.LinExpr(0) for node in range(nb_nodes) for neighbor in graph[node]}

        for commodity_index, path_and_var in enumerate(path_and_var_per_commodity):
            for path_tuple, var in path_and_var:
                for node_index in range(len(path_tuple)-1):
                    edge_use_dict[(path_tuple[node_index], path_tuple[node_index+1])] += var * demand_list[commodity_index]

        for node in range(nb_nodes):
            for neighbor in graph[node]:
                capacity_constraint_dict[timestep, node, neighbor] = model.addConstr(edge_use_dict[node, neighbor] - overload_var_dict[timestep, node, neighbor] <= graph[node][neighbor])

        total_capacity_constraint_dict[timestep] = model.addConstr((overload_var_dict.sum(timestep, '*', '*') - total_overload_var_dict[timestep] <= sum(demand_list)*0.01))

    print("Capacity constraints created")

    # Creating constraints to know when a commodity changes its path
    delta_constraint_dict = {}
    for timestep in range(nb_timesteps):
        for commodity_index in range(nb_commodities):
            for path_tuple, var in path_and_var_per_commodity_per_timestep[timestep][commodity_index]:

                if timestep == 0:
                    previous_path_value = path_tuple == initial_path_list[commodity_index]
                else:
                    previous_path_value = 0
                    for path2, var2 in path_and_var_per_commodity_per_timestep[timestep-1][commodity_index]:
                        if path2 == path_tuple:
                            previous_path_value = var2
                            break

                delta_var = model.addVar(obj=1)
                delta_var_dict[timestep, commodity_index, tuple(path_tuple)] = delta_var
                delta_constraint_dict[timestep, commodity_index, tuple(path_tuple)] = model.addConstr((var - previous_path_value - delta_var <= 0))

    print("Delta constraints created")

    return model, (path_and_var_per_commodity_per_timestep, overload_var_dict, total_overload_var_dict, delta_var_dict), (convexity_constraint_dict, delta_constraint_dict, capacity_constraint_dict, total_capacity_constraint_dict)


def arc_node_one_timestep_model(graph, commodity_list, initial_path_list, allowed_overflow=None, flow_penalisation=0, verbose=1):
    # Creates an arc-node formulation for one time-step of the dynamic unsplittable flow problem

    nb_nodes = len(graph)
    nb_commodities = len(commodity_list)
    demand_list = [commodity[2] for commodity in commodity_list]

    if allowed_overflow is None:
         allowed_overflow = sum(demand_list)*0.01

    # we aggregate the commodities by origin : this create a super commodity
    # this process does not change the results of the continuous solver
    super_commodity_dict = {}
    commodity_indices_by_origin = {}
    for commodity_index, commodity in enumerate(commodity_list):
        origin, destination, demand = commodity

        if origin not in super_commodity_dict:
            super_commodity_dict[origin] = {}
            commodity_indices_by_origin[origin] = []

        if destination not in super_commodity_dict[origin]:
            super_commodity_dict[origin][destination] = 0

        super_commodity_dict[origin][destination] += demand
        commodity_indices_by_origin[origin].append(commodity_index)

    arc_list = [(node, neighbor) for node in range(nb_nodes) for neighbor in graph[node]]
    super_commodity_list = list(super_commodity_dict.keys())

    valid_initial_path_commodity_list = [commodity_index for commodity_index in range(nb_commodities) if is_correct_path(graph, commodity_list[commodity_index], initial_path_list[commodity_index])]

    # Create optimization model
    model = gurobipy.Model('netflow')
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.Params.OutputFlag = verbose>1

    # Create variables
    initial_path_var = model.addVars(valid_initial_path_commodity_list, ub=1, name="initial_path") # variables deciding whether the initial path is used
    delta_var = model.addVars(valid_initial_path_commodity_list, obj=1, name="delta") # variables counting the path changes
    flow_var = model.addVars(super_commodity_list, arc_list, obj=flow_penalisation, name="flow_var") # flow variables
    overload_var = model.addVars(arc_list, name="overload")
    total_overload_var = model.addVar(obj=1)
    if verbose:
        print("variables created")

    # constraints enabling the delta_var to count the path changes
    delta_constraint_dict = model.addConstrs((1 - initial_path_var[commodity_index] - delta_var[commodity_index] <= 0) for commodity_index in valid_initial_path_commodity_list)
    if verbose:
        print("Delta constraints created")

    # linking the initial_path_var to the other flow variables
    linking_constraint_dict = {}
    for origin in commodity_indices_by_origin:
        edge_use_dict = {arc: [] for arc in arc_list}

        for commodity_index in commodity_indices_by_origin[origin]:
            initial_path = initial_path_list[commodity_index]
            if is_correct_path(graph, commodity_list[commodity_index], initial_path):
                for node_index in range(len(initial_path)-1):
                    arc = (initial_path[node_index], initial_path[node_index+1])
                    edge_use_dict[arc].append(commodity_index)

        for node, neighbor in arc_list:
            if edge_use_dict[node, neighbor] != []:
                linking_constraint_dict[origin, node, neighbor] = model.addConstr((sum(initial_path_var[commodity_index] * demand_list[commodity_index] for commodity_index in edge_use_dict[node, neighbor]) - flow_var[origin, node, neighbor] <= 0))
    if verbose:
        print("Linking constraints created")

    # Flow conservation constraints
    flow_constraint_dict = {}
    for origin in super_commodity_dict:
        for node in range(nb_nodes):

            rhs = 0

            if node == origin:
                rhs += sum(super_commodity_dict[origin].values())

            if node in super_commodity_dict[origin]:
                rhs += -super_commodity_dict[origin][node]

            flow_constraint_dict[origin, node] = model.addConstr((flow_var.sum(origin,node,'*') - flow_var.sum(origin,'*',node) == rhs), "flow{}_{}".format(origin, node))
    if verbose:
        print("Flow conservation constraints created")

    # Capacity constraints
    capacity_constraint_dict = model.addConstrs((flow_var.sum('*', node, neighbor) - overload_var[node, neighbor] <= graph[node][neighbor][0] for node, neighbor in arc_list), "capacity")
    total_capacity_constraint = model.addConstr((overload_var.sum() - total_overload_var <= allowed_overflow), "capacity_tot")
    if verbose:
        print("Capacity constraints created")

    return model, (initial_path_var, flow_var, overload_var, total_overload_var, delta_var), (delta_constraint_dict, linking_constraint_dict, flow_constraint_dict, capacity_constraint_dict, total_capacity_constraint)


def extract_allocation_from_model(model, graph, capacity_constraint_dict, flow_var, overload_var, initial_path_var, initial_path_list, commodity_list):
    # Extracts useful information from the solution of an arc-node formulation
    nb_nodes = len(graph)
    overload_values = model.getAttr('x', overload_var)
    remaining_capacity_graph = [{neighbor : capacity_constraint_dict[node, neighbor].RHS + overload_values[node, neighbor] for neighbor in graph[node]} for node in range(nb_nodes)]

    allocation_graph_per_origin = {}
    flow_values = model.getAttr('x', flow_var)
    for origin, node, neighbor in flow_values:
        if origin not in allocation_graph_per_origin:
            allocation_graph_per_origin[origin] = [{} for node in range(nb_nodes)]
        allocation_graph_per_origin[origin][node][neighbor] = [flow_values[origin, node, neighbor],graph[node][neighbor][1]]

    initial_path_values = model.getAttr('x', initial_path_var)

    for commodity_index in initial_path_values:
        initial_path = initial_path_list[commodity_index]
        value = initial_path_values[commodity_index]
        origin, destination, demand = commodity_list[commodity_index]

        for node_index in range(len(initial_path)-1):
            node, neighbor = initial_path[node_index], initial_path[node_index + 1]
            allocation_graph_per_origin[origin][node][neighbor][0] -= demand * value

    return allocation_graph_per_origin, remaining_capacity_graph, initial_path_values


def arc_path_one_timestep_model(graph, commodity_list, initial_path_list, possible_paths_per_commodity, allowed_overflow=None, flow_penalisation=0, verbose=1):
    # Creates an arc-node formulation for one time-step of the dynamic unsplittable flow problem

    nb_nodes = len(graph)
    nb_commodities = len(commodity_list)
    demand_list = [demand for origin, destination, demand in commodity_list]
    arc_list = [(node, neighbor) for node in range(nb_nodes) for neighbor in graph[node]]
    tuple_list = [(commodity_index, path_index) for commodity_index, possible_paths in enumerate(possible_paths_per_commodity) for path_index, path_tuple in enumerate(possible_paths)]

    path_cost_list = [(len(path_tuple) - 1) * flow_penalisation for commodity_index, possible_paths in enumerate(possible_paths_per_commodity) for path_index, path_tuple in enumerate(possible_paths)]

    if allowed_overflow is None:
        allowed_overflow = sum(demand_list) * 0.01

    # Create optimization model
    model = gurobipy.Model('netflow')
    model.modelSense = gurobipy.GRB.MINIMIZE
    model.Params.OutputFlag = verbose

    path_var = model.addVars(tuple_list, obj=path_cost_list, name="path_choice") # Variables choosing which path is used
    delta_var = model.addVars(nb_commodities, obj=1, name="delta") # variables counting the path changes
    overload_var = model.addVars(arc_list,  obj=0, name="overload")
    total_overload_var = model.addVar(obj=1, name="total_overload")
    if verbose:
        print("Variables created")

    path_and_var_per_commodity = [[(path_tuple, path_var[commodity_index, path_index]) for path_index, path_tuple in enumerate(possible_paths_per_commodity[commodity_index])] for commodity_index in range(nb_commodities)]

    delta_constraint_dict = {}
    for commodity_index, initial_path in enumerate(initial_path_list):
        if initial_path in possible_paths_per_commodity[commodity_index]:
            initial_path_index = possible_paths_per_commodity[commodity_index].index(initial_path)
            delta_constraint_dict[commodity_index] = model.addConstr(1 - path_var[commodity_index, initial_path_index] - delta_var[commodity_index]<= 0)
    if verbose:
        print("Delta constraints created")

    convexity_constraint_dict = model.addConstrs((path_var.sum(commodity_index, "*") == 1 for commodity_index in range(nb_commodities)))
    if verbose:
        print("Convexity constraints created")

    edge_var_sum_dict = {arc : 0 for arc in arc_list}
    for commodity_index, demand in enumerate(demand_list):
        for path_tuple, var in path_and_var_per_commodity[commodity_index]:
            for node_index in range(len(path_tuple)-1):
                arc = (path_tuple[node_index], path_tuple[node_index+1])
                edge_var_sum_dict[arc] += var * demand

    capacity_constraint_dict = model.addConstrs((edge_var_sum_dict[arc] - overload_var[arc] <= graph[arc[0]][arc[1]] for arc in arc_list))
    total_capacity_constraint = model.addConstr(overload_var.sum() - total_overload_var <= allowed_overflow)
    if verbose:
        print("Capacity constraints created")

    return model, (path_and_var_per_commodity, delta_var, overload_var, total_overload_var), (convexity_constraint_dict, capacity_constraint_dict, total_capacity_constraint, delta_constraint_dict)


def generate_new_paths(graph, commodity_list, model, capacity_constraint_dict, convexity_constraint_dict, path_and_var_per_commodity, flow_penalisation=0):
    # Generates new paths in a column generation fashion for an arc-path formulation
    nb_nodes = len(graph)
    nb_commodities = len(commodity_list)
    origin_list = list(set(commodity[0] for commodity in commodity_list))
    is_new_path_added = False

    capacity_dual_val_graph = [{neighbor : -capacity_constraint_dict[node, neighbor].Pi + flow_penalisation for neighbor in graph[node]} for node in range(nb_nodes)]
    convexity_dual_val_list = [convexity_constraint_dict[commodity_index].Pi for commodity_index in range(nb_commodities)]
    all_shortest_paths = compute_all_shortest_path(capacity_dual_val_graph, origin_list)

    for commodity_index, commodity in enumerate(commodity_list):
        origin, destination, demand = commodity
        new_path, path_cost = all_shortest_paths[origin][destination]
        reduced_cost = path_cost * demand - convexity_dual_val_list[commodity_index]

        if reduced_cost < -10**-5:
            is_new_path_added = True
            column = gurobipy.Column()
            column.addTerms(1, convexity_constraint_dict[commodity_index])

            for node_index in range(len(new_path) - 1):
                arc = (new_path[node_index], new_path[node_index+1])
                column.addTerms(demand, capacity_constraint_dict[arc])

            new_var = model.addVar(obj=(len(new_path)-1) * flow_penalisation, column=column)
            path_and_var_per_commodity[commodity_index].append((new_path, new_var))

    return is_new_path_added


def compute_possible_paths_per_commodity(graph, commodity_list, initial_path_list, nb_initial_path_created):
    shortest_paths_per_origin = {}
    possible_paths_per_commodity = []

    for commodity_index, commodity in enumerate(commodity_list):
        origin, destination, demand = commodity
        initial_path = initial_path_list[commodity_index]

        if origin not in shortest_paths_per_origin:
            shortest_paths_per_origin[origin] = k_shortest_path_all_destination(graph, origin, nb_initial_path_created)

        path_and_cost_list = shortest_paths_per_origin[origin][destination]
        possible_paths_per_commodity.append(set(tuple(remove_cycle_from_path(path_tuple)) for path_tuple, path_cost in path_and_cost_list))

        if is_correct_path(graph, commodity, initial_path):
            possible_paths_per_commodity[commodity_index].add(tuple(initial_path))

        possible_paths_per_commodity[commodity_index] = [list(path_tuple) for path_tuple in possible_paths_per_commodity[commodity_index]]

    return possible_paths_per_commodity


def remove_cycle_from_path(path_tuple):
    # Create a path where the cycles present in the input path have been removed
    is_in_path = set()
    new_path = []

    for node in path_tuple:
        if node in is_in_path:
            while new_path[-1] != node:
                node_to_remove = new_path.pop()
                is_in_path.remove(node_to_remove)

        else:
            is_in_path.add(node)
            new_path.append(node)

    return new_path


if __name__ == "__main__":
    pass
