import math
import networkx as nx
from ..dynamic_mcnf_paper_code.interface import calcul_paths


def calculate_fstate_shortest_path_without_gs_relaying(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph_only_satellites_with_isls,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        ground_station_satellites_in_range_candidates,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs,
        is_last
):

    # Calculate shortest path distances
    if enable_verbose_logs:
        print("  > Calculating Floyd-Warshall for graph without ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    dist_sat_net_without_gs = nx.floyd_warshall_numpy(sat_net_graph_only_satellites_with_isls)

    # Forwarding state
    fstate = {}

    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)
    with open(output_filename, "w+") as f_out:

        # Satellites to ground stations
        # From the satellites attached to the destination ground station,
        # select the one which promises the shortest path to the destination ground station (getting there + last hop)
        dist_satellite_to_ground_station = {}
        for curr in range(num_satellites):
            for dst_gid in range(num_ground_stations):
                dst_gs_node_id = num_satellites + dst_gid

                # Among the satellites in range of the destination ground station,
                # find the one which promises the shortest distance
                possible_dst_sats = ground_station_satellites_in_range_candidates[dst_gid]
                possibilities = []
                for b in possible_dst_sats:
                    if not math.isinf(dist_sat_net_without_gs[(curr, b[1])]):  # Must be reachable
                        possibilities.append(
                            (
                                dist_sat_net_without_gs[(curr, b[1])] + b[0],
                                b[1]
                            )
                        )
                #possibilities = list(sorted(possibilities))
                #end station must connect to the nearest satellite
                possibilities = list(sorted(ground_station_satellites_in_range_candidates[dst_gid]))

                # By default, if there is no satellite in range for the
                # destination ground station, it will be dropped (indicated by -1)
                next_hop_decision = (-1, -1, -1)
                distance_to_ground_station_m = float("inf")
                if len(possibilities) > 0:
                    dst_sat = possibilities[0][1]
                    distance_to_ground_station_m = possibilities[0][0]

                    # If the current node is not that satellite, determine how to get to the satellite
                    if curr != dst_sat:

                        # Among its neighbors, find the one which promises the
                        # lowest distance to reach the destination satellite
                        best_distance_m = 1000000000000000
                        for neighbor_id in sat_net_graph_only_satellites_with_isls.neighbors(curr):
                            distance_m = (
                                    sat_net_graph_only_satellites_with_isls.edges[(curr, neighbor_id)]["weight"]
                                    +
                                    dist_sat_net_without_gs[(neighbor_id, dst_sat)]
                            )
                            if distance_m < best_distance_m:
                                next_hop_decision = (
                                    neighbor_id,
                                    sat_neighbor_to_if[(curr, neighbor_id)],
                                    sat_neighbor_to_if[(neighbor_id, curr)]
                                )
                                best_distance_m = distance_m

                    else:
                        # This is the destination satellite, as such the next hop is the ground station itself
                        next_hop_decision = (
                            dst_gs_node_id,
                            num_isls_per_sat[dst_sat] + gid_to_sat_gsl_if_idx[dst_gid],
                            0
                        )

                # In any case, save the distance of the satellite to the ground station to re-use
                # when we calculate ground station to ground station forwarding
                dist_satellite_to_ground_station[(curr, dst_gs_node_id)] = distance_to_ground_station_m

                # Write to forwarding state
                if not prev_fstate or prev_fstate[(curr, dst_gs_node_id)] != next_hop_decision:
                    f_out.write("%d,%d,%d,%d,%d\n" % (
                        curr,
                        dst_gs_node_id,
                        next_hop_decision[0],
                        next_hop_decision[1],
                        next_hop_decision[2]
                    ))
                fstate[(curr, dst_gs_node_id)] = next_hop_decision

        # Ground stations to ground stations
        # Choose the source satellite which promises the shortest path
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid

                    # Among the satellites in range of the source ground station,
                    # find the one which promises the shortest distance
                    possible_src_sats = ground_station_satellites_in_range_candidates[src_gid]
                    possibilities = []
                    for a in possible_src_sats:
                        best_distance_offered_m = dist_satellite_to_ground_station[(a[1], dst_gs_node_id)]
                        if not math.isinf(best_distance_offered_m):
                            possibilities.append(
                                (
                                    a[0] + best_distance_offered_m,
                                    a[1]
                                )
                            )
                    #possibilities = sorted(possibilities)
                    #src station must connect to the nearest satellite
                    possibilities = sorted(possible_src_sats)

                    # By default, if there is no satellite in range for one of the
                    # ground stations, it will be dropped (indicated by -1)
                    next_hop_decision = (-1, -1, -1)
                    if len(possibilities) > 0:
                        src_sat_id = possibilities[0][1]
                        next_hop_decision = (
                            src_sat_id,
                            0,
                            num_isls_per_sat[src_sat_id] + gid_to_sat_gsl_if_idx[src_gid]
                        )

                    # Update forwarding state
                    if not prev_fstate or prev_fstate[(src_gs_node_id, dst_gs_node_id)] != next_hop_decision:
                        f_out.write("%d,%d,%d,%d,%d\n" % (
                            src_gs_node_id,
                            dst_gs_node_id,
                            next_hop_decision[0],
                            next_hop_decision[1],
                            next_hop_decision[2]
                        ))
                    fstate[(src_gs_node_id, dst_gs_node_id)] = next_hop_decision
    if is_last:
        with open(output_filename+".temp", "w+") as f_out:
            f_out.write(str(fstate))
    # Finally return result
    return fstate



def calculate_fstate_shortest_path_without_gs_relaying2(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph_only_satellites_with_isls,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        ground_station_satellites_in_range_candidates,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs,
        is_last,
        version
):
    #get the commodity list

    with open("commodites.temp","r") as fcomm:
        commodity_list=eval(fcomm.read())
        if enable_verbose_logs:
            print('lecture commodites') 
    with open("debitISL.temp","r") as fISL:
        debitISL=eval(fISL.readline())
        if enable_verbose_logs:
            print("debit lien ISL:",debitISL,"Mb/s")
    # Calculate shortest path distances
    if enable_verbose_logs:
        print("  > Calculating mcnf for graph without ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    total_net_graph=sat_net_graph_only_satellites_with_isls.copy()
    #add ground stations to graph
    total_net_graph.add_nodes_from([num_satellites + dst_gid for dst_gid in range(num_ground_stations)])
    #add possible edges to the graph. 

    # TODO /!\
    # the ground station can only be connected to one satellite. 
    # This will not be a problem here because a ground station only communicates with only one other station.
    # /!\ 
    for groundStationId in range(num_ground_stations):
        if ground_station_satellites_in_range_candidates[groundStationId]:
            distanceSatGS,satid = sorted(ground_station_satellites_in_range_candidates[groundStationId])[0]
            total_net_graph.add_edge(satid, num_satellites+groundStationId, weight = distanceSatGS)
        #for distanceSatGS,satid in sorted(ground_station_satellites_in_range_candidates[groundStationId]):
        #	total_net_graph.add_edge(satid, num_satellites+groundStationId, weight = 10000000)#distanceSatGS

    #compute optimal path
    if version=='a':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep")
    elif version=='b':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorter")
    elif version=='c':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorterc")
    elif version=='d':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorterd")
    elif version=='e':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shortere")
    else:
        raise Exception("Erreur de version d'algorithme")
    # Forwarding state : by default, interfaces down and empty routing table
    if prev_fstate:
        fstate=prev_fstate.copy()
    else:
        fstate = {(cur,dst):(-1,-1,-1) for cur in range(num_satellites+num_ground_stations) for dst in range(num_satellites,num_satellites+num_ground_stations) if cur !=dst}

    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)
    
    for i,path in enumerate(list_paths):
            if path:
                #src ground station to first sat
                src_id = path[0]
                dst_gs_node_id = path[-1]
                next_hop_decision=(path[1], 0, num_isls_per_sat[path[1]] + gid_to_sat_gsl_if_idx[src_id-num_satellites])
                fstate[(src_id, dst_gs_node_id)] = next_hop_decision
                
                #last sat to dst ground station
                next_hop_decision = (dst_gs_node_id,num_isls_per_sat[path[-2]] + gid_to_sat_gsl_if_idx[dst_gs_node_id-num_satellites],0)
                fstate[(path[-2], dst_gs_node_id)] = next_hop_decision
                
                #interfaces between satellites
                for k in range(1,len(path)-2):
                    curr,neighbor_id=path[k],path[k+1]
                    next_hop_decision = (neighbor_id,sat_neighbor_to_if[(curr, neighbor_id)],sat_neighbor_to_if[(neighbor_id, curr)])
                    fstate[(curr, dst_gs_node_id)] = next_hop_decision
    
    with open(output_filename, "w+") as f_out:
        for cle in fstate:
            if not prev_fstate or cle not in prev_fstate or prev_fstate[cle] != fstate[cle]:
                    f_out.write("{},{},{},{},{}\n".format(*cle, *fstate[cle]))
                    
    if is_last:
        with open(output_filename+".temp", "w+") as f_out:
            f_out.write(str(fstate))
            
    # Finally return result
    return fstate

def calculate_fstate_shortest_path_without_gs_relaying3(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph_only_satellites_with_isls,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        ground_station_satellites_in_range_candidates,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs,
        is_last
):
    #file commodity
    with open("commodites.temp","r") as fcomm:
        commodity_list=eval(fcomm.read())
        if enable_verbose_logs:
            print('lecture commodites') 
    with open("debitISL.temp","r") as fISL:
        debitISL=eval(fISL.readline())
        if enable_verbose_logs:
            print("debit lien ISL:",debitISL,"Mb/s")
    
    #Clear file satellites possibilities for ech GS : 
    file = 'possibilities.txt'
    with open(file,'w') as fpossibilities :
        print("OK : file of possibilities test is empty") 
    
    file = 'test-commodity.txt'
    with open(file,'w') as fdictcomm :
        print("OK : file of commodity test is empty")

    # Calculate shortest path distances
    if enable_verbose_logs:
        print("  > Calculating Floyd-Warshall for graph without ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    dist_sat_net_without_gs = nx.floyd_warshall_numpy(sat_net_graph_only_satellites_with_isls)

    # Forwarding state
    fstate = {}
    dist_satellite_to_ground_station = {}
    src_to_dst = {}
    commodity = {}
    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)

    # create commodity dictionary
    for c in commodity_list : 
        commodity[c[0]] = c[1]
    file = 'test-commodity.txt'
    with open(file,'a') as fdictcomm :
        fdictcomm.write("".join(str(k)+' '+str(v)+"\n" for k, v in commodity.items()))

    # create possibilites dictionary
    for gs_id in range(num_ground_stations):
        dst_gs_node_id = num_satellites + gs_id

        # Among the satellites in range of the destination ground station,
        # find the one which promises the shortest distance
        possibilities = list(sorted(ground_station_satellites_in_range_candidates[gs_id]))

        if len(possibilities) > 0:
            dist_satellite_to_ground_station[dst_gs_node_id]=[]
            for i in range(3) :
                dst_sat = possibilities[i][1]
                distance_to_ground_station_m = possibilities[i][0]
                dist_satellite_to_ground_station[dst_gs_node_id].append(
                    (
                        dst_sat,
                        distance_to_ground_station_m
                    )
                )
        #write in a file the 3 closest satellites for each GS :
        file = 'possibilities.txt'
        with open(file,'a') as fpossibilities :
            fpossibilities.write("".join(str(dst_gs_node_id)+' '+str(item[0])+' '+str(item[1])+"\n" for item in dist_satellite_to_ground_station[dst_gs_node_id]))
    
    #Writing the fstate
    with open('src_to_dst.txt', "w+") as f_out:
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid
                    #for each combination of source and destination, find the shortest path between
                    # different source and destination satellite if in commodity list
                    best_find = False
                    neighbor_find = False
                    if commodity[src_gs_node_id] == dst_gs_node_id : 
                        for i in range(len(dist_satellite_to_ground_station[src_gs_node_id])) :
                            for j in range(len(dist_satellite_to_ground_station[dst_gs_node_id])) :
                                #case 1 satellite - GSL only
                                if dist_satellite_to_ground_station[src_gs_node_id][i][0] == dist_satellite_to_ground_station[dst_gs_node_id][j][0] and best_find == False :
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][0]
                                    )
                                    best_find = True
                                    break

                                #case 2 satellite - direct neighbor
                                elif dist_satellite_to_ground_station[dst_gs_node_id][j][0] in sat_net_graph_only_satellites_with_isls.neighbors(dist_satellite_to_ground_station[src_gs_node_id][i][0]) and best_find == False : 
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][0]
                                    )
                                    neighbor_find = True


                                #original case
                                elif best_find == False and neighbor_find == False : 
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][0][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][0][0]
                                    )

                        # Write to src to dst : file with best first and last satellite for each src and dest
                        f_out.write("%d,%d,%d,%d\n" % (
                            src_to_dst_gs_sat[0],
                            src_to_dst_gs_sat[1],
                            src_to_dst_gs_sat[2],
                            src_to_dst_gs_sat[3]
                        ))
                        src_to_dst[(src_to_dst_gs_sat[0], src_to_dst_gs_sat[1])] = (src_to_dst_gs_sat[2],src_to_dst_gs_sat[3])
        # Keeping the best dest sat  found for the commodity, and finding the best path between the closest sat
        # of the source GS
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid
                    best_find = False
                    neighbor_find = False
                    if commodity[src_gs_node_id] != dst_gs_node_id :
                        dst_sat = src_to_dst[(commodity[dst_gs_node_id],dst_gs_node_id)][1]
                        for i in range(len(dist_satellite_to_ground_station[src_gs_node_id])) :
                            #case 1 satellite - GSL only
                            if dist_satellite_to_ground_station[src_gs_node_id][i][0] == dst_sat and best_find == False :
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                    dst_sat
                                )
                                best_find = True
                                break

                            #case 2 satellite - direct neighbor
                            elif dst_sat in sat_net_graph_only_satellites_with_isls.neighbors(dist_satellite_to_ground_station[src_gs_node_id][i][0]) and best_find == False : 
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                    dst_sat
                                )
                                neighbor_find = True


                            #original case
                            elif best_find == False and neighbor_find == False : 
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][0][0],
                                    dst_sat
                                )
                # Write to src to dst : file with best first and last satellite for each src and dest
                f_out.write("%d,%d,%d,%d\n" % (
                    src_to_dst_gs_sat[0],
                    src_to_dst_gs_sat[1],
                    src_to_dst_gs_sat[2],
                    src_to_dst_gs_sat[3]
                ))
                src_to_dst[(src_to_dst_gs_sat[0], src_to_dst_gs_sat[1])] = (src_to_dst_gs_sat[2],src_to_dst_gs_sat[3])

    with open(output_filename, "w+") as f_out:
        
    # Satellites to ground stations
    # From the satellites attached to the destination ground station,
    # select the one which promises the shortest path to the destination ground station (getting there + last hop)
        for curr in range(num_satellites):
            for dst_gid in range(num_ground_stations):
                dst_gs_node_id = num_satellites + dst_gid

                find_good = False
                curr_src = False
                neighbor_find = False

                for src_gid in [x for x in range(num_ground_stations) if x != dst_gid] :
                    src_gs_node_id = num_satellites + src_gid 
                    src_sat = src_to_dst[(src_gs_node_id, dst_gs_node_id)][0]
                    dst_sat = src_to_dst[(src_gs_node_id, dst_gs_node_id)][1]

                    if curr == dst_sat and find_good == False : 
                        # This is the destination satellite, as such the next hop is the ground station itself
                        next_hop_decision = (
                            dst_gs_node_id,
                            num_isls_per_sat[dst_sat] + gid_to_sat_gsl_if_idx[dst_gid],
                            0
                        )
                        find_good = True  

                    elif curr == src_sat and find_good == False and curr_src == False:
                        curr_src = True    
                        best_distance_m = 1000000000000000
                        for neighbor_id in sat_net_graph_only_satellites_with_isls.neighbors(curr):
                            distance_m = (
                                    sat_net_graph_only_satellites_with_isls.edges[(curr, neighbor_id)]["weight"]
                                    +
                                    dist_sat_net_without_gs[(neighbor_id, dst_sat)]
                            )
                            if distance_m < best_distance_m:
                                next_hop_decision = (
                                    neighbor_id,
                                    sat_neighbor_to_if[(curr, neighbor_id)],
                                    sat_neighbor_to_if[(neighbor_id, curr)]
                                )
                                best_distance_m = distance_m

                    # If the current node is not that satellite, determine how to get to the satellite
                    elif src_sat != dst_sat and find_good == False and curr_src == False :
                        #case 1 satellite - direct neighbor
                        if curr in sat_net_graph_only_satellites_with_isls.neighbors(dst_sat): 
                            neighbor_id = dst_sat
                            next_hop_decision = (
                                neighbor_id,
                                sat_neighbor_to_if[(curr, neighbor_id)],
                                sat_neighbor_to_if[(neighbor_id, curr)]
                            ) 
                            neighbor_find = True

                        #original case
                        elif neighbor_find == False and find_good == False and curr_src == False : 
                            best_distance_m = 1000000000000000
                            for neighbor_id in sat_net_graph_only_satellites_with_isls.neighbors(curr):
                                distance_m = (
                                        sat_net_graph_only_satellites_with_isls.edges[(curr, neighbor_id)]["weight"]
                                        +
                                        dist_sat_net_without_gs[(neighbor_id, dst_sat)]
                                )
                                if distance_m < best_distance_m:
                                    next_hop_decision = (
                                        neighbor_id,
                                        sat_neighbor_to_if[(curr, neighbor_id)],
                                        sat_neighbor_to_if[(neighbor_id, curr)] 
                                    )
                                    best_distance_m = distance_m
                                
                # Write to forwarding state
                if not prev_fstate or prev_fstate[(curr, dst_gs_node_id)] != next_hop_decision:
                    f_out.write("%d,%d,%d,%d,%d\n" % (
                        curr,
                        dst_gs_node_id,
                        next_hop_decision[0],
                        next_hop_decision[1],
                        next_hop_decision[2]
                    ))
                fstate[(curr, dst_gs_node_id)] = next_hop_decision

        # Ground stations to ground stations
        # Choose the source satellite which promises the shortest path      
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid

                    src_sat_id = src_to_dst[(src_gs_node_id, dst_gs_node_id)][0]
                    next_hop_decision = (
                        src_sat_id,
                        0,
                        num_isls_per_sat[src_sat_id] + gid_to_sat_gsl_if_idx[src_gid]
                    )

                    # Update forwarding state
                    if not prev_fstate or prev_fstate[(src_gs_node_id, dst_gs_node_id)] != next_hop_decision:
                        f_out.write("%d,%d,%d,%d,%d\n" % (
                            src_gs_node_id,
                            dst_gs_node_id,
                            next_hop_decision[0],
                            next_hop_decision[1],
                            next_hop_decision[2]
                        ))
                    fstate[(src_gs_node_id, dst_gs_node_id)] = next_hop_decision
    if is_last:
        with open(output_filename+".temp", "w+") as f_out:
            f_out.write(str(fstate))
    # Finally return result
    return fstate

def calculate_fstate_shortest_path_without_gs_relaying4(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph_only_satellites_with_isls,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        ground_station_satellites_in_range_candidates,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs,
        is_last,
        version
):
    #get the commodity list

    with open("commodites.temp","r") as fcomm:
        commodity_list=eval(fcomm.read())
        if enable_verbose_logs:
            print('lecture commodites') 
    with open("debitISL.temp","r") as fISL:
        debitISL=eval(fISL.readline())
        if enable_verbose_logs:
            print("debit lien ISL:",debitISL,"Mb/s")
    # Calculate shortest path distances
    if enable_verbose_logs:
        print("  > Calculating mcnf for graph without ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    total_net_graph=sat_net_graph_only_satellites_with_isls.copy()
    #add ground stations to graph
    total_net_graph.add_nodes_from([num_satellites + dst_gid for dst_gid in range(num_ground_stations)])
    #add possible edges to the graph. 
    
    # Forwarding state
    dist_satellite_to_ground_station = {}
    src_to_dst = {}
    commodity = {}
    # create commodity dictionary
    for c in commodity_list : 
        commodity[c[0]] = c[1]

     # create possibilites dictionary
    for gs_id in range(num_ground_stations):
        dst_gs_node_id = num_satellites + gs_id

        # Among the satellites in range of the destination ground station,
        # find the one which promises the shortest distance
        possibilities = list(sorted(ground_station_satellites_in_range_candidates[gs_id]))

        if len(possibilities) > 0:
            dist_satellite_to_ground_station[dst_gs_node_id]=[]
            for i in range(3) :
                dst_sat = possibilities[i][1]
                distance_to_ground_station_m = possibilities[i][0]
                dist_satellite_to_ground_station[dst_gs_node_id].append(
                    (
                        dst_sat,
                        distance_to_ground_station_m
                    )
                )
        #write in a file the 3 closest satellites for each GS :
        file = 'possibilities.txt'
        with open(file,'a') as fpossibilities :
            fpossibilities.write("".join(str(dst_gs_node_id)+' '+str(item[0])+' '+str(item[1])+"\n" for item in dist_satellite_to_ground_station[dst_gs_node_id]))
    
    #Writing the fstate
    with open('src_to_dst.txt', "w+") as f_out:
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid
                    #for each combination of source and destination, find the shortest path between
                    # different source and destination satellite if in commodity list
                    best_find = False
                    neighbor_find = False
                    if commodity[src_gs_node_id] == dst_gs_node_id : 
                        for i in range(len(dist_satellite_to_ground_station[src_gs_node_id])) :
                            for j in range(len(dist_satellite_to_ground_station[dst_gs_node_id])) :
                                #case 1 satellite - GSL only
                                if dist_satellite_to_ground_station[src_gs_node_id][i][0] == dist_satellite_to_ground_station[dst_gs_node_id][j][0] and best_find == False :
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][0],
                                        dist_satellite_to_ground_station[src_gs_node_id][i][1],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][1]  
                                    )
                                    best_find = True
                                    break

                                #case 2 satellite - direct neighbor
                                elif dist_satellite_to_ground_station[dst_gs_node_id][j][0] in sat_net_graph_only_satellites_with_isls.neighbors(dist_satellite_to_ground_station[src_gs_node_id][i][0]) and best_find == False : 
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][0],
                                        dist_satellite_to_ground_station[src_gs_node_id][i][1],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][1] 
                                    )
                                    neighbor_find = True


                                #original case
                                elif best_find == False and neighbor_find == False : 
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][0][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][0][0],
                                        dist_satellite_to_ground_station[src_gs_node_id][0][1],
                                        dist_satellite_to_ground_station[dst_gs_node_id][0][1] 
                                    )

                        # Write to src to dst : file with best first and last satellite for each src and dest
                        f_out.write("%d,%d,%d,%d\n" % (
                            src_to_dst_gs_sat[0],
                            src_to_dst_gs_sat[1],
                            src_to_dst_gs_sat[2],
                            src_to_dst_gs_sat[3]
                        ))
                        src_to_dst[(src_to_dst_gs_sat[0], src_to_dst_gs_sat[1])] = (src_to_dst_gs_sat[2],src_to_dst_gs_sat[3],src_to_dst_gs_sat[4],src_to_dst_gs_sat[5])
        # Keeping the best dest sat  found for the commodity, and finding the best path between the closest sat
        # of the source GS
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid
                    best_find = False
                    neighbor_find = False
                    if commodity[src_gs_node_id] != dst_gs_node_id :
                        dst_sat = src_to_dst[(commodity[dst_gs_node_id],dst_gs_node_id)][1]
                        dst_sat_dist = src_to_dst[(commodity[dst_gs_node_id],dst_gs_node_id)][3]
                        for i in range(len(dist_satellite_to_ground_station[src_gs_node_id])) :
                            #case 1 satellite - GSL only
                            if dist_satellite_to_ground_station[src_gs_node_id][i][0] == dst_sat and best_find == False :
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                    dst_sat,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][1],
                                    dst_sat_dist
                                )
                                best_find = True
                                break

                            #case 2 satellite - direct neighbor
                            elif dst_sat in sat_net_graph_only_satellites_with_isls.neighbors(dist_satellite_to_ground_station[src_gs_node_id][i][0]) and best_find == False : 
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                    dst_sat,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][1],
                                    dst_sat_dist
                                )
                                neighbor_find = True


                            #original case
                            elif best_find == False and neighbor_find == False : 
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][0][0],
                                    dst_sat,
                                    dist_satellite_to_ground_station[src_gs_node_id][0][1],
                                    dst_sat_dist
                                )
                # Write to src to dst : file with best first and last satellite for each src and dest
                f_out.write("%d,%d,%d,%d\n" % (
                    src_to_dst_gs_sat[0],
                    src_to_dst_gs_sat[1],
                    src_to_dst_gs_sat[2],
                    src_to_dst_gs_sat[3]
                ))
                src_to_dst[(src_to_dst_gs_sat[0], src_to_dst_gs_sat[1])] = (src_to_dst_gs_sat[2],src_to_dst_gs_sat[3],src_to_dst_gs_sat[4],src_to_dst_gs_sat[5])
    i = 0
    for k, v in src_to_dst.items() : 
        #distanceSatGS,satid = sorted(ground_station_satellites_in_range_candidates[groundStationId])[0]
        if i == num_ground_stations :
            break
        else : 
            total_net_graph.add_edge(v[0], k[0], weight = v[2])
        i += 1
        #for distanceSatGS,satid in sorted(ground_station_satellites_in_range_candidates[groundStationId]):
        #	total_net_graph.add_edge(satid, num_satellites+groundStationId, weight = 10000000)#distanceSatGS

    #compute optimal path
    if version=='a':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep")
    elif version=='b':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorter")
    elif version=='c':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorterc")
    elif version=='d':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorterd")
    elif version=='e':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shortere")
    else:
        raise Exception("Erreur de version d'algorithme")
    # Forwarding state : by default, interfaces down and empty routing table
    if prev_fstate:
        fstate=prev_fstate.copy()
    else:
        fstate = {(cur,dst):(-1,-1,-1) for cur in range(num_satellites+num_ground_stations) for dst in range(num_satellites,num_satellites+num_ground_stations) if cur !=dst}

    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)
    
    for i,path in enumerate(list_paths):
            if path:
                #src ground station to first sat
                src_id = path[0]
                dst_gs_node_id = path[-1]
                next_hop_decision=(path[1], 0, num_isls_per_sat[path[1]] + gid_to_sat_gsl_if_idx[src_id-num_satellites])
                fstate[(src_id, dst_gs_node_id)] = next_hop_decision
                
                #last sat to dst ground station
                next_hop_decision = (dst_gs_node_id,num_isls_per_sat[path[-2]] + gid_to_sat_gsl_if_idx[dst_gs_node_id-num_satellites],0)
                fstate[(path[-2], dst_gs_node_id)] = next_hop_decision
                
                #interfaces between satellites
                for k in range(1,len(path)-2):
                    curr,neighbor_id=path[k],path[k+1]
                    next_hop_decision = (neighbor_id,sat_neighbor_to_if[(curr, neighbor_id)],sat_neighbor_to_if[(neighbor_id, curr)])
                    fstate[(curr, dst_gs_node_id)] = next_hop_decision
    
    with open(output_filename, "w+") as f_out:
        for cle in fstate:
            if not prev_fstate or cle not in prev_fstate or prev_fstate[cle] != fstate[cle]:
                    f_out.write("{},{},{},{},{}\n".format(*cle, *fstate[cle]))
                    
    if is_last:
        with open(output_filename+".temp", "w+") as f_out:
            f_out.write(str(fstate))
            
    # Finally return result
    return fstate

def calculate_fstate_shortest_path_without_gs_relaying5(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph_only_satellites_with_isls,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        ground_station_satellites_in_range_candidates,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs,
        is_last
):
    #file commodity
    with open("commodites.temp","r") as fcomm:
        commodity_list=eval(fcomm.read())
        if enable_verbose_logs:
            print('lecture commodites') 
    with open("debitISL.temp","r") as fISL:
        debitISL=eval(fISL.readline())
        if enable_verbose_logs:
            print("debit lien ISL:",debitISL,"Mb/s")
    
    #Clear file satellites possibilities for ech GS : 
    file = 'possibilities.txt'
    with open(file,'w') as fpossibilities :
        print("OK : file of possibilities test is empty") 
    
    file = 'test-commodity.txt'
    with open(file,'w') as fdictcomm :
        print("OK : file of commodity test is empty")

    # Calculate shortest path distances
    if enable_verbose_logs:
        print("  > Calculating Floyd-Warshall for graph without ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    dist_sat_net_without_gs = nx.floyd_warshall_numpy(sat_net_graph_only_satellites_with_isls)

    # Forwarding state
    fstate = {}
    dist_satellite_to_ground_station = {}
    src_to_dst = {}
    commodity = {}
    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)

    # create commodity dictionary
    for c in commodity_list : 
        commodity[c[0]] = c[1]
    file = 'test-commodity.txt'
    with open(file,'a') as fdictcomm :
        fdictcomm.write("".join(str(k)+' '+str(v)+"\n" for k, v in commodity.items()))

    # create possibilites dictionary
    for gs_id in range(num_ground_stations):
        dst_gs_node_id = num_satellites + gs_id

        # Among the satellites in range of the destination ground station,
        # find the one which promises the shortest distance
        possibilities = list(sorted(ground_station_satellites_in_range_candidates[gs_id]))

        if len(possibilities) > 0:
            dist_satellite_to_ground_station[dst_gs_node_id]=[]
            for i in range(5) :
                dst_sat = possibilities[i][1]
                distance_to_ground_station_m = possibilities[i][0]
                dist_satellite_to_ground_station[dst_gs_node_id].append(
                    (
                        dst_sat,
                        distance_to_ground_station_m
                    )
                )
        #write in a file the 3 closest satellites for each GS :
        file = 'possibilities.txt'
        with open(file,'a') as fpossibilities :
            fpossibilities.write("".join(str(dst_gs_node_id)+' '+str(item[0])+' '+str(item[1])+"\n" for item in dist_satellite_to_ground_station[dst_gs_node_id]))
    
    #Writing the fstate
    with open('src_to_dst.txt', "w+") as f_out:
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid
                    #for each combination of source and destination, find the shortest path between
                    # different source and destination satellite if in commodity list
                    best_find = False
                    neighbor_find = False
                    if commodity[src_gs_node_id] == dst_gs_node_id : 
                        for i in range(len(dist_satellite_to_ground_station[src_gs_node_id])) :
                            for j in range(len(dist_satellite_to_ground_station[dst_gs_node_id])) :
                                #case 1 satellite - GSL only
                                if dist_satellite_to_ground_station[src_gs_node_id][i][0] == dist_satellite_to_ground_station[dst_gs_node_id][j][0] and best_find == False :
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][0]
                                    )
                                    best_find = True
                                    break

                                #case 2 satellite - direct neighbor
                                elif dist_satellite_to_ground_station[dst_gs_node_id][j][0] in sat_net_graph_only_satellites_with_isls.neighbors(dist_satellite_to_ground_station[src_gs_node_id][i][0]) and best_find == False : 
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][0]
                                    )
                                    neighbor_find = True


                                #original case
                                elif best_find == False and neighbor_find == False : 
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][0][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][0][0]
                                    )

                        # Write to src to dst : file with best first and last satellite for each src and dest
                        f_out.write("%d,%d,%d,%d\n" % (
                            src_to_dst_gs_sat[0],
                            src_to_dst_gs_sat[1],
                            src_to_dst_gs_sat[2],
                            src_to_dst_gs_sat[3]
                        ))
                        src_to_dst[(src_to_dst_gs_sat[0], src_to_dst_gs_sat[1])] = (src_to_dst_gs_sat[2],src_to_dst_gs_sat[3])
        # Keeping the best dest sat  found for the commodity, and finding the best path between the closest sat
        # of the source GS
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid
                    best_find = False
                    neighbor_find = False
                    if commodity[src_gs_node_id] != dst_gs_node_id :
                        dst_sat = src_to_dst[(commodity[dst_gs_node_id],dst_gs_node_id)][1]
                        for i in range(len(dist_satellite_to_ground_station[src_gs_node_id])) :
                            #case 1 satellite - GSL only
                            if dist_satellite_to_ground_station[src_gs_node_id][i][0] == dst_sat and best_find == False :
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                    dst_sat
                                )
                                best_find = True
                                break

                            #case 2 satellite - direct neighbor
                            elif dst_sat in sat_net_graph_only_satellites_with_isls.neighbors(dist_satellite_to_ground_station[src_gs_node_id][i][0]) and best_find == False : 
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                    dst_sat
                                )
                                neighbor_find = True


                            #original case
                            elif best_find == False and neighbor_find == False : 
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][0][0],
                                    dst_sat
                                )
                # Write to src to dst : file with best first and last satellite for each src and dest
                f_out.write("%d,%d,%d,%d\n" % (
                    src_to_dst_gs_sat[0],
                    src_to_dst_gs_sat[1],
                    src_to_dst_gs_sat[2],
                    src_to_dst_gs_sat[3]
                ))
                src_to_dst[(src_to_dst_gs_sat[0], src_to_dst_gs_sat[1])] = (src_to_dst_gs_sat[2],src_to_dst_gs_sat[3])

    with open(output_filename, "w+") as f_out:
        
    # Satellites to ground stations
    # From the satellites attached to the destination ground station,
    # select the one which promises the shortest path to the destination ground station (getting there + last hop)
        for curr in range(num_satellites):
            for dst_gid in range(num_ground_stations):
                dst_gs_node_id = num_satellites + dst_gid

                find_good = False
                curr_src = False
                neighbor_find = False

                for src_gid in [x for x in range(num_ground_stations) if x != dst_gid] :
                    src_gs_node_id = num_satellites + src_gid 
                    src_sat = src_to_dst[(src_gs_node_id, dst_gs_node_id)][0]
                    dst_sat = src_to_dst[(src_gs_node_id, dst_gs_node_id)][1]

                    if curr == dst_sat and find_good == False : 
                        # This is the destination satellite, as such the next hop is the ground station itself
                        next_hop_decision = (
                            dst_gs_node_id,
                            num_isls_per_sat[dst_sat] + gid_to_sat_gsl_if_idx[dst_gid],
                            0
                        )
                        find_good = True  

                    elif curr == src_sat and find_good == False and curr_src == False:
                        curr_src = True    
                        best_distance_m = 1000000000000000
                        for neighbor_id in sat_net_graph_only_satellites_with_isls.neighbors(curr):
                            distance_m = (
                                    sat_net_graph_only_satellites_with_isls.edges[(curr, neighbor_id)]["weight"]
                                    +
                                    dist_sat_net_without_gs[(neighbor_id, dst_sat)]
                            )
                            if distance_m < best_distance_m:
                                next_hop_decision = (
                                    neighbor_id,
                                    sat_neighbor_to_if[(curr, neighbor_id)],
                                    sat_neighbor_to_if[(neighbor_id, curr)]
                                )
                                best_distance_m = distance_m

                    # If the current node is not that satellite, determine how to get to the satellite
                    elif src_sat != dst_sat and find_good == False and curr_src == False :
                        #case 1 satellite - direct neighbor
                        if curr in sat_net_graph_only_satellites_with_isls.neighbors(dst_sat): 
                            neighbor_id = dst_sat
                            next_hop_decision = (
                                neighbor_id,
                                sat_neighbor_to_if[(curr, neighbor_id)],
                                sat_neighbor_to_if[(neighbor_id, curr)]
                            ) 
                            neighbor_find = True

                        #original case
                        elif neighbor_find == False and find_good == False and curr_src == False : 
                            best_distance_m = 1000000000000000
                            for neighbor_id in sat_net_graph_only_satellites_with_isls.neighbors(curr):
                                distance_m = (
                                        sat_net_graph_only_satellites_with_isls.edges[(curr, neighbor_id)]["weight"]
                                        +
                                        dist_sat_net_without_gs[(neighbor_id, dst_sat)]
                                )
                                if distance_m < best_distance_m:
                                    next_hop_decision = (
                                        neighbor_id,
                                        sat_neighbor_to_if[(curr, neighbor_id)],
                                        sat_neighbor_to_if[(neighbor_id, curr)] 
                                    )
                                    best_distance_m = distance_m
                                
                # Write to forwarding state
                if not prev_fstate or prev_fstate[(curr, dst_gs_node_id)] != next_hop_decision:
                    f_out.write("%d,%d,%d,%d,%d\n" % (
                        curr,
                        dst_gs_node_id,
                        next_hop_decision[0],
                        next_hop_decision[1],
                        next_hop_decision[2]
                    ))
                fstate[(curr, dst_gs_node_id)] = next_hop_decision

        # Ground stations to ground stations
        # Choose the source satellite which promises the shortest path      
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid

                    src_sat_id = src_to_dst[(src_gs_node_id, dst_gs_node_id)][0]
                    next_hop_decision = (
                        src_sat_id,
                        0,
                        num_isls_per_sat[src_sat_id] + gid_to_sat_gsl_if_idx[src_gid]
                    )

                    # Update forwarding state
                    if not prev_fstate or prev_fstate[(src_gs_node_id, dst_gs_node_id)] != next_hop_decision:
                        f_out.write("%d,%d,%d,%d,%d\n" % (
                            src_gs_node_id,
                            dst_gs_node_id,
                            next_hop_decision[0],
                            next_hop_decision[1],
                            next_hop_decision[2]
                        ))
                    fstate[(src_gs_node_id, dst_gs_node_id)] = next_hop_decision
    if is_last:
        with open(output_filename+".temp", "w+") as f_out:
            f_out.write(str(fstate))
    # Finally return result
    return fstate

def calculate_fstate_shortest_path_without_gs_relaying6(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph_only_satellites_with_isls,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        ground_station_satellites_in_range_candidates,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs,
        is_last,
        version
):
    #get the commodity list

    with open("commodites.temp","r") as fcomm:
        commodity_list=eval(fcomm.read())
        if enable_verbose_logs:
            print('lecture commodites') 
    with open("debitISL.temp","r") as fISL:
        debitISL=eval(fISL.readline())
        if enable_verbose_logs:
            print("debit lien ISL:",debitISL,"Mb/s")
    # Calculate shortest path distances
    if enable_verbose_logs:
        print("  > Calculating mcnf for graph without ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    total_net_graph=sat_net_graph_only_satellites_with_isls.copy()
    #add ground stations to graph
    total_net_graph.add_nodes_from([num_satellites + dst_gid for dst_gid in range(num_ground_stations)])
    #add possible edges to the graph. 
    
    # Forwarding state
    dist_satellite_to_ground_station = {}
    src_to_dst = {}
    commodity = {}
    # create commodity dictionary
    for c in commodity_list : 
        commodity[c[0]] = c[1]

     # create possibilites dictionary
    for gs_id in range(num_ground_stations):
        dst_gs_node_id = num_satellites + gs_id

        # Among the satellites in range of the destination ground station,
        # find the one which promises the shortest distance
        possibilities = list(sorted(ground_station_satellites_in_range_candidates[gs_id]))

        if len(possibilities) > 0:
            dist_satellite_to_ground_station[dst_gs_node_id]=[]
            for i in range(5) :
                dst_sat = possibilities[i][1]
                distance_to_ground_station_m = possibilities[i][0]
                dist_satellite_to_ground_station[dst_gs_node_id].append(
                    (
                        dst_sat,
                        distance_to_ground_station_m
                    )
                )
        #write in a file the 5 closest satellites for each GS :
        file = 'possibilities.txt'
        with open(file,'a') as fpossibilities :
            fpossibilities.write("".join(str(dst_gs_node_id)+' '+str(item[0])+' '+str(item[1])+"\n" for item in dist_satellite_to_ground_station[dst_gs_node_id]))
    
    #Writing the fstate
    with open('src_to_dst.txt', "w+") as f_out:
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid
                    #for each combination of source and destination, find the shortest path between
                    # different source and destination satellite if in commodity list
                    best_find = False
                    neighbor_find = False
                    if commodity[src_gs_node_id] == dst_gs_node_id : 
                        for i in range(len(dist_satellite_to_ground_station[src_gs_node_id])) :
                            for j in range(len(dist_satellite_to_ground_station[dst_gs_node_id])) :
                                #case 1 satellite - GSL only
                                if dist_satellite_to_ground_station[src_gs_node_id][i][0] == dist_satellite_to_ground_station[dst_gs_node_id][j][0] and best_find == False :
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][0],
                                        dist_satellite_to_ground_station[src_gs_node_id][i][1],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][1]  
                                    )
                                    best_find = True
                                    break

                                #case 2 satellite - direct neighbor
                                elif dist_satellite_to_ground_station[dst_gs_node_id][j][0] in sat_net_graph_only_satellites_with_isls.neighbors(dist_satellite_to_ground_station[src_gs_node_id][i][0]) and best_find == False : 
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][0],
                                        dist_satellite_to_ground_station[src_gs_node_id][i][1],
                                        dist_satellite_to_ground_station[dst_gs_node_id][j][1] 
                                    )
                                    neighbor_find = True


                                #original case
                                elif best_find == False and neighbor_find == False : 
                                    src_to_dst_gs_sat = (
                                        src_gs_node_id,
                                        dst_gs_node_id,
                                        dist_satellite_to_ground_station[src_gs_node_id][0][0],
                                        dist_satellite_to_ground_station[dst_gs_node_id][0][0],
                                        dist_satellite_to_ground_station[src_gs_node_id][0][1],
                                        dist_satellite_to_ground_station[dst_gs_node_id][0][1] 
                                    )

                        # Write to src to dst : file with best first and last satellite for each src and dest
                        f_out.write("%d,%d,%d,%d\n" % (
                            src_to_dst_gs_sat[0],
                            src_to_dst_gs_sat[1],
                            src_to_dst_gs_sat[2],
                            src_to_dst_gs_sat[3]
                        ))
                        src_to_dst[(src_to_dst_gs_sat[0], src_to_dst_gs_sat[1])] = (src_to_dst_gs_sat[2],src_to_dst_gs_sat[3],src_to_dst_gs_sat[4],src_to_dst_gs_sat[5])
        # Keeping the best dest sat  found for the commodity, and finding the best path between the closest sat
        # of the source GS
        for src_gid in range(num_ground_stations):
            for dst_gid in range(num_ground_stations):
                if src_gid != dst_gid:
                    src_gs_node_id = num_satellites + src_gid
                    dst_gs_node_id = num_satellites + dst_gid
                    best_find = False
                    neighbor_find = False
                    if commodity[src_gs_node_id] != dst_gs_node_id :
                        dst_sat = src_to_dst[(commodity[dst_gs_node_id],dst_gs_node_id)][1]
                        dst_sat_dist = src_to_dst[(commodity[dst_gs_node_id],dst_gs_node_id)][3]
                        for i in range(len(dist_satellite_to_ground_station[src_gs_node_id])) :
                            #case 1 satellite - GSL only
                            if dist_satellite_to_ground_station[src_gs_node_id][i][0] == dst_sat and best_find == False :
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                    dst_sat,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][1],
                                    dst_sat_dist
                                )
                                best_find = True
                                break

                            #case 2 satellite - direct neighbor
                            elif dst_sat in sat_net_graph_only_satellites_with_isls.neighbors(dist_satellite_to_ground_station[src_gs_node_id][i][0]) and best_find == False : 
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][0],
                                    dst_sat,
                                    dist_satellite_to_ground_station[src_gs_node_id][i][1],
                                    dst_sat_dist
                                )
                                neighbor_find = True


                            #original case
                            elif best_find == False and neighbor_find == False : 
                                src_to_dst_gs_sat = (
                                    src_gs_node_id,
                                    dst_gs_node_id,
                                    dist_satellite_to_ground_station[src_gs_node_id][0][0],
                                    dst_sat,
                                    dist_satellite_to_ground_station[src_gs_node_id][0][1],
                                    dst_sat_dist
                                )
                # Write to src to dst : file with best first and last satellite for each src and dest
                f_out.write("%d,%d,%d,%d\n" % (
                    src_to_dst_gs_sat[0],
                    src_to_dst_gs_sat[1],
                    src_to_dst_gs_sat[2],
                    src_to_dst_gs_sat[3]
                ))
                src_to_dst[(src_to_dst_gs_sat[0], src_to_dst_gs_sat[1])] = (src_to_dst_gs_sat[2],src_to_dst_gs_sat[3],src_to_dst_gs_sat[4],src_to_dst_gs_sat[5])
    i = 0
    for k, v in src_to_dst.items() : 
        #distanceSatGS,satid = sorted(ground_station_satellites_in_range_candidates[groundStationId])[0]
        if i == num_ground_stations :
            break
        else : 
            total_net_graph.add_edge(v[0], k[0], weight = v[2])
        i += 1
        #for distanceSatGS,satid in sorted(ground_station_satellites_in_range_candidates[groundStationId]):
        #	total_net_graph.add_edge(satid, num_satellites+groundStationId, weight = 10000000)#distanceSatGS

    #compute optimal path
    if version=='a':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep")
    elif version=='b':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorter")
    elif version=='c':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorterc")
    elif version=='d':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shorterd")
    elif version=='e':
        list_paths = calcul_paths(total_net_graph, prev_fstate, commodity_list, debitISL, "SRR_arc_node_one_timestep_shortere")
    else:
        raise Exception("Erreur de version d'algorithme")
    # Forwarding state : by default, interfaces down and empty routing table
    if prev_fstate:
        fstate=prev_fstate.copy()
    else:
        fstate = {(cur,dst):(-1,-1,-1) for cur in range(num_satellites+num_ground_stations) for dst in range(num_satellites,num_satellites+num_ground_stations) if cur !=dst}

    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)
    
    for i,path in enumerate(list_paths):
            if path:
                #src ground station to first sat
                src_id = path[0]
                dst_gs_node_id = path[-1]
                next_hop_decision=(path[1], 0, num_isls_per_sat[path[1]] + gid_to_sat_gsl_if_idx[src_id-num_satellites])
                fstate[(src_id, dst_gs_node_id)] = next_hop_decision
                
                #last sat to dst ground station
                next_hop_decision = (dst_gs_node_id,num_isls_per_sat[path[-2]] + gid_to_sat_gsl_if_idx[dst_gs_node_id-num_satellites],0)
                fstate[(path[-2], dst_gs_node_id)] = next_hop_decision
                
                #interfaces between satellites
                for k in range(1,len(path)-2):
                    curr,neighbor_id=path[k],path[k+1]
                    next_hop_decision = (neighbor_id,sat_neighbor_to_if[(curr, neighbor_id)],sat_neighbor_to_if[(neighbor_id, curr)])
                    fstate[(curr, dst_gs_node_id)] = next_hop_decision
    
    with open(output_filename, "w+") as f_out:
        for cle in fstate:
            if not prev_fstate or cle not in prev_fstate or prev_fstate[cle] != fstate[cle]:
                    f_out.write("{},{},{},{},{}\n".format(*cle, *fstate[cle]))
                    
    if is_last:
        with open(output_filename+".temp", "w+") as f_out:
            f_out.write(str(fstate))
            
    # Finally return result
    return fstate

def calculate_fstate_shortest_path_with_gs_relaying(
        output_dynamic_state_dir,
        time_since_epoch_ns,
        num_satellites,
        num_ground_stations,
        sat_net_graph,
        num_isls_per_sat,
        gid_to_sat_gsl_if_idx,
        sat_neighbor_to_if,
        prev_fstate,
        enable_verbose_logs
):

    # Calculate shortest paths
    if enable_verbose_logs:
        print("  > Calculating Floyd-Warshall for graph including ground-station relays")
    # (Note: Numpy has a deprecation warning here because of how networkx uses matrices)
    dist_sat_net = nx.floyd_warshall_numpy(sat_net_graph)

    # Forwarding state
    fstate = {}

    # Now write state to file for complete graph
    output_filename = output_dynamic_state_dir + "/fstate_" + str(time_since_epoch_ns) + ".txt"
    if enable_verbose_logs:
        print("  > Writing forwarding state to: " + output_filename)
    with open(output_filename, "w+") as f_out:

        # Satellites and ground stations to ground stations
        for current_node_id in range(num_satellites + num_ground_stations):
            for dst_gid in range(num_ground_stations):
                dst_gs_node_id = num_satellites + dst_gid

                # Cannot forward to itself
                if current_node_id != dst_gs_node_id:

                    # Among its neighbors, find the one which promises the
                    # lowest distance to reach the destination satellite
                    next_hop_decision = (-1, -1, -1)
                    best_distance_m = 1000000000000000
                    for neighbor_id in sat_net_graph.neighbors(current_node_id):

                        # Any neighbor must be reachable
                        if math.isinf(dist_sat_net[(current_node_id, neighbor_id)]):
                            raise ValueError("Neighbor cannot be unreachable")

                        # Calculate distance = next-hop + distance the next hop node promises
                        distance_m = (
                            sat_net_graph.edges[(current_node_id, neighbor_id)]["weight"]
                            +
                            dist_sat_net[(neighbor_id, dst_gs_node_id)]
                        )
                        if (
                                not math.isinf(dist_sat_net[(neighbor_id, dst_gs_node_id)])
                                and
                                distance_m < best_distance_m
                        ):

                            # Check node identifiers to determine what are the
                            # correct interface identifiers
                            if current_node_id >= num_satellites and neighbor_id < num_satellites:  # GS to sat.
                                my_if = 0
                                next_hop_if = (
                                    num_isls_per_sat[neighbor_id]
                                    +
                                    gid_to_sat_gsl_if_idx[current_node_id - num_satellites]
                                )

                            elif current_node_id < num_satellites and neighbor_id >= num_satellites:  # Sat. to GS
                                my_if = (
                                    num_isls_per_sat[current_node_id]
                                    +
                                    gid_to_sat_gsl_if_idx[neighbor_id - num_satellites]
                                )
                                next_hop_if = 0

                            elif current_node_id < num_satellites and neighbor_id < num_satellites:  # Sat. to sat.
                                my_if = sat_neighbor_to_if[(current_node_id, neighbor_id)]
                                next_hop_if = sat_neighbor_to_if[(neighbor_id, current_node_id)]

                            else:  # GS to GS
                                raise ValueError("GS-to-GS link cannot exist")

                            # Write the next-hop decision
                            next_hop_decision = (
                                neighbor_id,  # Next-hop node identifier
                                my_if,        # My outgoing interface id
                                next_hop_if   # Next-hop incoming interface id
                            )

                            # Update best distance found
                            best_distance_m = distance_m

                    # Write to forwarding state
                    if not prev_fstate or prev_fstate[(current_node_id, dst_gs_node_id)] != next_hop_decision:
                        f_out.write("%d,%d,%d,%d,%d\n" % (
                            current_node_id,
                            dst_gs_node_id,
                            next_hop_decision[0],
                            next_hop_decision[1],
                            next_hop_decision[2]
                        ))
                    fstate[(current_node_id, dst_gs_node_id)] = next_hop_decision

    # Finally return result
    return fstate
