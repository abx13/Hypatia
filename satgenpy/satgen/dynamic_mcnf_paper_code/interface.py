import networkx as nx
from .mcnf_dynamic import SRR_arc_node_one_timestep, SRR_arc_node_one_timestep_shorter

def graph2nx(graphf):
	#use for tests only, the weight attribute may be the bandwidth, not the distance as expected to run Floyd-Warshall
	g=nx.Graph()
	g.add_nodes_from([i for i in range(len(graphf))])
	for node,neighs in enumerate(graphf):
		g.add_edges_from([(node,neigh,{"weight":neighs[neigh]}) for neigh in neighs])
	return g
	
def nx2graph(graphnx, debitISL, verif=False): 
	#converts networkx graph to graph suitable with Francois's algos
	if verif:
		for i in graphnx.nodes:
			assert type(i)==int
			for j in graphnx[i]:
				assert type(j)==int
	g=[{} for _ in graphnx.nodes]
	for u,v,data in graphnx.edges(data=True):
		#satellite links are bidirectionnal
		#to make an inversible conversion, set g[u][v],g[v][u] =  data['weight'],data['weight']
		#in Francois's algo, all we care about is bandwidth
		g[u][v]=[debitISL,data['weight']]#rate in Mb/s
		g[v][u]=[debitISL,data['weight']]
	return g

def fstate2sol(fstate,list_commodities):
	#converts network solution to a solution as computed by Francois's algo
	results_list = [None for _ in list_commodities]
	if fstate is None:#fstate can be initialised with None
		return results_list
	for idcomm,com in enumerate(list_commodities):
		src,dest,_=com
		temp_list=[]
		curr=src
		while curr!=dest and (curr,dest) in fstate and fstate[(curr,dest)]:
			nxt,if_src,if_nxt = fstate[(curr,dest)]
			temp_list.append(curr)
			curr=nxt
		if curr==dest:
			results_list[idcomm]=temp_list
	return results_list

def sol2fstate(solutions,sat_neighbor_to_if,num_isls_per_sat,gid_to_sat_gsl_if_idx,num_ground_stations):
	#converts Francois's algo output to a network solution
	fstate={}
	for chemin in solutions:
		dest=chemin[-1]
		fstate[(chemin[0],dest)]=(chemin[2],0,num_isls_per_sat[chemin[2]] + gid_to_sat_gsl_if_idx[dest-num_ground_stations])
		fstate[(chemin[-2],dest)]=(dest,num_isls_per_sat[chemin[-2]] + gid_to_sat_gsl_if_idx[dest-num_ground_stations],0)
		for k in range(1,len(chemin)-1):
			fstate[(chemin[k],dest)]= (
								chemin[k+1],
								sat_neighbor_to_if[(chemin[k], chemin[k+1])],
								sat_neighbor_to_if[(chemin[k+1], chemin[k])])
	return fstate
	

def elimineLiensImpossibles(graph,commodites):
	commodites_simplifiees=[]#commodities
	diff_commodites=[]#ids of unused commodities
	communicabilite=nx.algorithms.communicability_alg.communicability(graph)
	for idcomm,com in enumerate(commodites):
		src,dst,_=com
		if communicabilite[src][dst]:
			commodites_simplifiees.append(com)
		else:
			diff_commodites.append(idcomm)
	return diff_commodites,commodites_simplifiees

def calcul_paths(graph,prev_fstate,commodity_list, debitISL, algo):
	#select computable commodities and create diff
	diff_commodites,commodites_simplifiees=elimineLiensImpossibles(graph,commodity_list)
	
	#create initial path list 
	init_path_list=fstate2sol(prev_fstate,commodity_list)
	init_path_list_simplifie=[]
	curr_id_diff=0
	for idcom,comm in enumerate(commodity_list):
		if curr_id_diff<len(diff_commodites) and idcom==diff_commodites[curr_id_diff]:#there is no possible way, forget commodity
			curr_id_diff+=1
		elif init_path_list[idcom]:#the commodity will be kept, there was a path previously computed
			init_path_list_simplifie.append(init_path_list[idcom])
		else:#this is a new commodity, compute shortest path
			init_path_list_simplifie.append(nx.shortest_path(graph, src:=comm[0], dst:=comm[1]))
	#convert graph
	total_net_graph_differentformat=nx2graph(graph, debitISL)
	#compute new paths
	if algo=="SRR_arc_node_one_timestep":
		list_paths = SRR_arc_node_one_timestep(total_net_graph_differentformat, commodites_simplifiees, init_path_list_simplifie)
	elif algo=="SRR_arc_node_one_timestep_shorter":
		list_paths = SRR_arc_node_one_timestep_shorter(total_net_graph_differentformat, commodites_simplifiees, init_path_list_simplifie)
	#add empty solutions
	for idcom in diff_commodites:
		list_paths.insert(idcom,[])
	return list_paths
	


