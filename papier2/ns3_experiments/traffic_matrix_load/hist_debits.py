import os
import matplotlib.pyplot as plt
import numpy as np
import math

#------------------------------------#
#        PARAMETRES A CHANGER        #
#------------------------------------#
mbps = 10
tps_simu = 20

dim_row = 4
dim_columns = 5

tab_hist_flows = []

def byte_to_megabit(byte):
    return byte/125000

def ns_to_s(ns):
    return ns/10**9

def ns_to_ms(ns):
    return ns/10**6


def get_max(list1, list2):
    print(max(list1))
    max_list1 = max(list1)
    max_list2 = max(list2)
    print("MAX")
    print(max(max_list1, max_list2))
    return max(max_list1, max_list2)



def read_flows_file(file):
    tab_hist_flows = []
    tcp_flows = file.readlines()
    for line in tcp_flows:
        fct_ns = float(line.strip().split(',')[6])
        sent_byte = float(line.strip().split(',')[7])
        on_going = line.strip().split(',')[8]
        avg_rate = byte_to_megabit(sent_byte)/ns_to_s(fct_ns)

        tab_hist_flows.append((avg_rate,on_going))
    return tab_hist_flows

#####
#EXECUTION


    
with open("runs/run_loaded_tm_pairing_10_Mbps_for_20s_with_tcp_algorithm_free_one_only_over_isls/logs_ns3/tcp_flows.csv", "r") as f_tcp_flows, \
     open("runs/run_loaded_tm_pairing_10_Mbps_for_20s_with_tcp_algorithm_free_one_only_over_isls2/logs_ns3/tcp_flows.csv", "r") as f_tcp_flows2, \
     open("runs/run_loaded_tm_pairing_10_Mbps_for_20s_with_tcp_algorithm_free_one_only_over_isls3/logs_ns3/tcp_flows.csv", "r") as f_tcp_flows3:

    tab_flows1 = read_flows_file(f_tcp_flows)
    tab_flows2 = read_flows_file(f_tcp_flows2)
    tab_flows3 = read_flows_file(f_tcp_flows3)
    
    print("length")
    print(len(tab_flows1))
    print("ISLS - AVG Rate")
    #for i in range (len(tab_flows1)):
     #       print(tab_flows1[i][0])
    print(list(zip(*tab_flows1))[0])

    print("ISLS 2 - AVG Rate")
    #for i in range (len(tab_flows2)):        
     #       print(tab_flows2[i][0])
    print(list(zip(*tab_flows2))[0])

    print("ISLS 3 - AVG Rate")
    #for i in range (len(tab_flows2)):        
     #       print(tab_flows2[i][0])
    print(list(zip(*tab_flows3))[0])
    
   
    width = 0.25      
    print(len(list(zip(*tab_flows1))[0]))   
    x = np.arange(len(list(zip(*tab_flows1))[0]))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    b1 = ax.bar(x-width, height=list(zip(*tab_flows1))[0], width=width, label='Shortest Path', align="center")
    b2 = ax.bar(x, height=list(zip(*tab_flows2))[0], width=width, label='MCNF',align="center")
    b3 = ax.bar(x+width, height=list(zip(*tab_flows3))[0], width=width, label='Optimized',align="center")

    fig.suptitle("Histogram - Simulation "+str(mbps)+" Mps "+str(tps_simu)+" s")
    #plt.xticks(x, util_fractions)
    plt.xlabel("TCP Flow ID")
    plt.ylabel("Average Rate")
    plt.legend()

    #ax.set_ylim([0, math.ceil(get_max(list(zip(*tab_flows1))[0], list(zip(*tab_flows2))[0]))])

    plt.show()
