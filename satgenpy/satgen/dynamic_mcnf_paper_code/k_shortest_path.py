import heapq as hp
import random
import numpy as np
import time


def k_shortest_path_all_destination(graph, origin, k):
    nb_nodes = len(graph)
    parent_list, distances = dijkstra(graph, origin)
    shortest_path_list = [[] for node in range(nb_nodes)]
    shortest_path_list[origin].append(([origin], 0))


    for node in range(nb_nodes):
        if len(shortest_path_list[node]) == 0 and parent_list[node] is not None:
            compute_shortest_path(graph, shortest_path_list, parent_list, node)

    index_predecessor_shortest_path = [{neighbor : 0 for neighbor in range(nb_nodes) if node in graph[neighbor]} for node in range(nb_nodes)]
    for node in range(nb_nodes):
        if parent_list[node] is not None:
            index_predecessor_shortest_path[node][parent_list[node]] = 1

    for node in range(nb_nodes):
        while parent_list[node] != None and len(shortest_path_list[node]) != k:
            is_new_path_computed = compute_next_shortest_path(graph, shortest_path_list, index_predecessor_shortest_path, node)

            if not is_new_path_computed:
                break

    return shortest_path_list


def k_shortest_path_all_destination_cost_difference(graph, origin, cost_difference):
    nb_nodes = len(graph)
    parent_list, distances = dijkstra(graph, origin)
    shortest_path_list = [[] for node in range(nb_nodes)]
    shortest_path_list[origin].append(([origin], 0))

    for node in range(nb_nodes):
        if len(shortest_path_list[node]) == 0 and parent_list[node] is not None:
            compute_shortest_path(graph, shortest_path_list, parent_list, node)

    index_predecessor_shortest_path = [{neighbor : 0 for neighbor in range(nb_nodes) if node in graph[neighbor]} for node in range(nb_nodes)]
    for node in range(nb_nodes):
        if parent_list[node] is not None:
            index_predecessor_shortest_path[node][parent_list[node]] = 1

    for node in range(nb_nodes):
        while parent_list[node] != None and shortest_path_list[node][-1][1] < shortest_path_list[node][0][1] + cost_difference:
            is_new_path_computed = compute_next_shortest_path(graph, shortest_path_list, index_predecessor_shortest_path, node)

            if not is_new_path_computed:
                break

    return shortest_path_list


def k_shortest_path_algorithm(graph, origin, destination, k):
    nb_nodes = len(graph)
    parent_list, distances = dijkstra(graph, origin)
    shortest_path_list = [[] for node in range(nb_nodes)]
    shortest_path_list[origin].append(([origin], 0))

    for node in range(nb_nodes):
        if len(shortest_path_list[node]) == 0 and parent_list[node] is not None:
            compute_shortest_path(graph, shortest_path_list, parent_list, node)

    index_predecessor_shortest_path = [{neighbor : 0 for neighbor in range(nb_nodes) if node in graph[neighbor]} for node in range(nb_nodes)]
    for node in range(nb_nodes):
        if parent_list[node] is not None:
            index_predecessor_shortest_path[node][parent_list[node]] = 1

    for i in range(k-1):
        compute_next_shortest_path(graph, shortest_path_list, index_predecessor_shortest_path, destination)

    return shortest_path_list[destination]

def compute_shortest_path(graph, shortest_path_list, parent_list, node):
    parent = parent_list[node]
    if len(shortest_path_list[parent]) == 0:
        compute_shortest_path(graph, shortest_path_list, parent_list, parent)

    parent_path, parent_path_cost = shortest_path_list[parent][0]
    shortest_path_list[node].append((parent_path + [node], parent_path_cost + graph[parent][node]))


def compute_next_shortest_path(graph, shortest_path_list, index_predecessor_shortest_path, node):
    chosen_predecessor = None

    for predecessor in index_predecessor_shortest_path[node]:
        predecessor_index = index_predecessor_shortest_path[node][predecessor]

        if predecessor_index is not None:
            if len(shortest_path_list[predecessor]) <= predecessor_index:
                is_new_path_computed = compute_next_shortest_path(graph, shortest_path_list, index_predecessor_shortest_path, predecessor)

                if not is_new_path_computed:
                    continue

            predecessor_path, predecessor_path_cost = shortest_path_list[predecessor][predecessor_index]
            if chosen_predecessor is None or min_length > predecessor_path_cost + graph[predecessor][node]:
                min_length = predecessor_path_cost + graph[predecessor][node]
                chosen_predecessor = predecessor

    if chosen_predecessor is not None:
        predecessor_index = index_predecessor_shortest_path[node][chosen_predecessor]
        predecessor_path, predecessor_path_cost = shortest_path_list[chosen_predecessor][predecessor_index]
        shortest_path_list[node].append((predecessor_path + [node], predecessor_path_cost + graph[chosen_predecessor][node]))
        index_predecessor_shortest_path[node][chosen_predecessor] += 1
        return True

    return False



def dijkstra(graph, intial_node, destination_node=None):
    priority_q = [(0, intial_node, None)]
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

    return parent_list, distances
