"""
README
Write isl_utilization.csv : void TopologySatelliteNetwork::CollectUtilizationStatistics() in 
/hypatia/ns3-sat-sim/simulator/contrib/satellite-network/model/topology-satellite-network.cc
 
Modify the isls_tracking_interval_ns in 
/hypatia/papier2/ns3_experiments/traffic_matrix_load/templates/template_config_ns3_tcp2.properties  

[from node],[to node],[start_time],[end_time],[utilization]
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import math

#utilization rates are divided into 5 categories (0, 0-0.25, 0.25-0.5, 0.5-0.75, 0.75-1)
def id_util(util):
    if (util == 0):
        id_util = 0
           
    elif(util > 0 and util <=0.25):
        id_util = 1
            
    elif(util > 0.25 and util <=0.5):
        id_util = 2
            
    elif(util > 0.5 and util <=0.75):
        id_util = 3

    elif(util > 0.75 and util <=1):
        id_util = 4

    return id_util

def get_max(list1, list2):
    max_list1 = []
    max_list2 = []
    for i in range (dim_row):
        max_list1.append(max(list1[i]))
        max_list2.append(max(list1[i]))
    return max( [max(max_list1), max(max_list2) ])



#------------------------------------#
#        PARAMETRES A CHANGER        #
#------------------------------------#
mbps = 10
tps_simu = 20

#------------------------------------# 

dim_row = 4
dim_columns = 5

time_fractions = [(0,int(tps_simu/4)), (int(tps_simu/4),int(tps_simu/4)*2), (int(tps_simu/4)*2,int(tps_simu/4)*3), (int(tps_simu/4)*3,int(tps_simu))]
util_fractions = ['0','0-0.25','0.25-0.5', '0.5-0.75', '0.75-1']

def read_util_file(file):
    i=0
    tab_hist_util = [[0 for x in range(dim_columns)] for i in range(dim_row)]
    isl_util = file.readlines()
    for line in isl_util:
        start_time = int(line.strip().split(',')[2])/10**9
        end_time = int(line.strip().split(',')[3])/10**9
        util = float(line.strip().split(',')[4])
        id_ut = id_util(util)
        if(i==0 or i==1 or i==2):
            print(start_time)
            print(end_time)
            print(util)
            print(id_ut)
        #counting the number of occurrencies of the same utilization rate by timestep (2s)
        if (start_time >= 0 and start_time < int(tps_simu/4)):
            tab_hist_util[0][id_ut] += 1
            if(i==0 or i==1 or i==2):
                print(tab_hist_util[0][id_ut])
        elif(start_time >= int(tps_simu/4) and start_time < int(tps_simu/4)*2):
            tab_hist_util[1][id_ut] += 1
            if(i==0 or i==1 or i==2):
                print(tab_hist_util[0][id_ut])
        elif(start_time >= int(tps_simu/4)*2 and start_time < int(tps_simu/4)*3):
            tab_hist_util[2][id_ut] += 1
            if(i==0 or i==1 or i==2):
                print(tab_hist_util[0][id_ut])
        elif(start_time >= int(tps_simu/4)*3 and start_time < int(tps_simu)):
            tab_hist_util[3][id_ut] += 1
            if(i==0 or i==1 or i==2):
                print(tab_hist_util[0][id_ut])
        i+=1
    return tab_hist_util

#####
#EXECUTION

print(int(tps_simu/4))
print(int(tps_simu/4)*2)
print(int(tps_simu/4)*3)
print(int(tps_simu))
    
with open("runs/run_loaded_tm_pairing_"+str(mbps)+"_Mbps_for_"+str(tps_simu)+"s_with_tcp_algorithm_free_one_only_over_isls/logs_ns3/isl_utilization.csv", "r") as f_isl_util, \
     open("runs/run_loaded_tm_pairing_"+str(mbps)+"_Mbps_for_"+str(tps_simu)+"s_with_tcp_algorithm_free_one_only_over_isls2/logs_ns3/isl_utilization.csv", "r") as f_isl_util2, \
     open("runs/run_loaded_tm_pairing_"+str(mbps)+"_Mbps_for_"+str(tps_simu)+"s_with_tcp_algorithm_free_one_only_over_isls3/logs_ns3/isl_utilization.csv", "r") as f_isl_util3:

    tab_util1 = read_util_file(f_isl_util)
    tab_util2 = read_util_file(f_isl_util2)
    tab_util3 = read_util_file(f_isl_util3)

    print("ISLS - Utilization")
    for i in range (dim_row):
            print(tab_util1[i])

    print("ISLS 2 - Utilization")
    for i in range (dim_row):        
            print(tab_util2[i])

    print("ISLS 3 - Utilization")
    for i in range (dim_row):        
            print(tab_util3[i])

    for i in range (dim_row): 
        width = 0.25 
        x = np.arange(len(util_fractions))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        b1 = ax.bar(x-width, height=tab_util1[i], width=width, label='Shortest Path', align="center")
        b2 = ax.bar(x, height=tab_util2[i], width=width, label='MCNF',align="center")
        b3 = ax.bar(x+width, height=tab_util3[i], width=width, label='Optimized',align="center")

        fig.suptitle("Histogram - Simulation "+str(mbps)+" Mps "+str(tps_simu)+" s - from "+str(time_fractions[i][0])+"s to "+str(time_fractions[i][1])+"s")
        plt.xticks(x, util_fractions)

        plt.legend()

        ax.set_ylim([0, math.ceil(get_max(tab_util1, tab_util2)/1000)*1000])

        plt.show()







    

            
            