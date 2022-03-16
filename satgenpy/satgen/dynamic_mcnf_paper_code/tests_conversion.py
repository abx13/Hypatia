""" avant tout, utiliser depointe dans module.py lancer pointe après utilisation"""
from .interface import *
import networkx as nx

def testgraphs(num_satellites,num_ground_stations):
	edges = [(x,y,100*x/(y+1)) for x in range(num_satellites) for y in range(num_ground_stations) if (y==x+1 or y==x-1 or y==2*x or x==2*y)]#[src, dst, poids]
	edges+=[(x,x+num_satellites,5) for x in range(num_ground_stations-1)]+[(x+num_satellites,x,5) for x in range(num_ground_stations-1)]

	sat_net_graph_only_isls = nx.Graph()
	sat_net_graph_only_gsls = nx.Graph()
	sat_net_graph_complete = nx.Graph()

	# Nodes
	ground_station_satellites_in_range = []
	for i in range(num_satellites):
		sat_net_graph_only_isls.add_node(i)
		sat_net_graph_only_gsls.add_node(i)
		sat_net_graph_complete.add_node(i)
	for i in range(num_satellites, num_satellites + num_ground_stations):
		sat_net_graph_only_gsls.add_node(i)
		sat_net_graph_complete.add_node(i)
		ground_station_satellites_in_range.append([])

	# Edges
	num_isls_per_sat = [0] * num_satellites
	sat_neighbor_to_if = {}
	for e in edges:
		if e[0] < num_satellites and e[1] < num_satellites:
			sat_net_graph_only_isls.add_edge(
				e[0], e[1], weight=e[2]
			)
			sat_net_graph_complete.add_edge(
				e[0], e[1], weight=e[2]
			)
			sat_neighbor_to_if[(e[0], e[1])] = num_isls_per_sat[e[0]]
			sat_neighbor_to_if[(e[1], e[0])] = num_isls_per_sat[e[1]]
			num_isls_per_sat[e[0]] += 1
			num_isls_per_sat[e[1]] += 1
		if e[0] >= num_satellites or e[1] >= num_satellites:
			sat_net_graph_only_gsls.add_edge(
				e[0], e[1], weight=e[2]
			)
			sat_net_graph_complete.add_edge(
				e[0], e[1], weight=e[2]
			)
			ground_station_satellites_in_range[max(e[0], e[1]) - num_satellites].append(
				(e[2], min(e[0], e[1]))
			)

	# GS relays only does not have ISLs
	num_isls_per_sat_for_only_gs_relays = [0] * num_satellites

	# Finally, GID to the satellite GSL interface index it communicates to on each satellite
	gid_to_sat_gsl_if_idx = list(range(num_ground_stations))
	return sat_net_graph_complete, sat_neighbor_to_if,num_isls_per_sat,gid_to_sat_gsl_if_idx,num_ground_stations

def test_interface():
	if __name__!="__main__":
		return
	
	num_satellites=30
	num_ground_stations=20
	commodites=[((x+3)%num_ground_stations,(x+1)%num_ground_stations, 0.5*(x+1)) for x in range(num_satellites,num_satellites+num_ground_stations)]

	sat_net_graph_complete, sat_neighbor_to_if,num_isls_per_sat,gid_to_sat_gsl_if_idx,num_ground_stations = testgraphs(num_satellites,num_ground_stations)

	results_list=calcul_paths(sat_net_graph_complete,prev_fstate:={},commodites,1000000000)
	#results_list = SRR_arc_node_one_timestep(graph, commodites, init_path)
	print(results_list)

#init_path=[[] for _ in range(len(commodites))]
#prev_fstate=sol2fstate(init_path,sat_neighbor_to_if,num_isls_per_sat,gid_to_sat_gsl_if_idx,num_ground_stations)
#calcul_paths(graph,prev_fstate,commodity_list)
test_interface()