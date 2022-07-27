"""
README

"""

import os
import matplotlib.pyplot as plt
import numpy as np
import math

#------------------------------------#
#        PARAMETERS TO MODIFY        #
#------------------------------------#
mbps = 10
tps_simu = 120
timestep_ms = 10000
nb_cities = 100
tab_isls = ["isls", "isls2", "isls3", "isls4", "isls5", "isls6"]
nb_algo_SP = 3
nb_algo_MCNF = 3
constellation = "telesat_1015"

#------------------------------------#

#Clear file
file = 'hop_count.txt'


#Function to count hops in paths
def read_hop_file(file):
    path_at_0 = file.readlines()[0].strip().split(',')
    hop_count = path_at_0[1].split('-')
    number_sat = len(hop_count)-2
    return number_sat

#####
#EXECUTION

#Creating tabs
tab_hopcount = []
for _ in range(len(tab_isls)):
    tab_hopcount.append([])

tab_reduc_SP = []
for _ in range(nb_algo_SP - 1):
    tab_reduc_SP.append([])

tab_reduc_MCNF = []
for _ in range(nb_algo_MCNF - 1):
    tab_reduc_MCNF.append([])


#Getting the correct files
doss = "../../satgenpy_analysis/data/"
interdoss1 = str(constellation)+"_isls_plus_grid_ground_stations_top_"+str(nb_cities)+"_algorithm_free_one_only_over_"
interdoss2 = '/'+str(timestep_ms)+"ms_for_"+str(tps_simu)+"s/manual/data/"

#Calculting hop counts
for i in range (len(tab_isls)) :
    net = sorted(os.listdir(doss+interdoss1+tab_isls[i]+interdoss2))
    for networkx in net:
        if "path" in networkx:
            with open(doss+interdoss1+tab_isls[i]+interdoss2+networkx, "r") as f_hop_count :
                tab_hopcount[i].append(read_hop_file(f_hop_count))
                
                
#Reduction rates
for j in range (nb_cities) : 
    tab_reduc_SP[0].append((tab_hopcount[2][j] - tab_hopcount[0][j]) / tab_hopcount[0][j])
    tab_reduc_SP[1].append((tab_hopcount[4][j] - tab_hopcount[0][j]) / tab_hopcount[0][j])
    tab_reduc_MCNF[0].append((tab_hopcount[3][j] - tab_hopcount[1][j]) / tab_hopcount[1][j])
    tab_reduc_MCNF[1].append((tab_hopcount[5][j] - tab_hopcount[1][j]) / tab_hopcount[1][j])

#Averages
avg_reduc_SP3 = sum(tab_reduc_SP[0])/len(tab_reduc_SP[0])
avg_reduc_SP5 = sum(tab_reduc_SP[1])/len(tab_reduc_SP[1])
avg_reduc_MCNF3 = sum(tab_reduc_MCNF[0])/len(tab_reduc_MCNF[0])
avg_reduc_MCNF5 = sum(tab_reduc_MCNF[1])/len(tab_reduc_MCNF[1])


#write in a file the results :
file = 'hop_count.txt'
with open(file,'a') as fhopcount :
    fhopcount.write("".join("AVERAGE DIFFERENCE SP 3: {:.2f}%\n".format(avg_reduc_SP3*100)))
    fhopcount.write("".join("AVERAGE DIFFERENCE SP 5 {:.2f}%\n".format(avg_reduc_SP5*100)))
    fhopcount.write("".join("AVERAGE DIFFERENCE MCNF 3: {:.2f}%\n".format(avg_reduc_MCNF3*100)))
    fhopcount.write("".join("AVERAGE DIFFERENCE MCNF 5: {:.2f}%\n\n".format(avg_reduc_MCNF5*100)))

    fhopcount.write("".join("ID"+'\t'+"ISLS"+'\t'+"ISLS2"+'\t'+"ISLS3"+'\t'+"ISLS4"+'\t'+"ISLS5"+'\t'+"ISLS6"+'\t'+"ISLS3/ISLS"+'\t'+"ISLS5/ISLS"+'\t'+"ISLS4/ISLS2"+'\t'+"ISLS6/ISLS2"+"\n"))
    #fhopcount.write("".join(str(j)+'\t'+str(tab_hopcount[0][j])+'\t\t'+str(tab_hopcount[1][j])+'\t\t'+str(tab_hopcount[2][j])+'\t\t'+str(tab_hopcount[3][j])+str(tab_hopcount[4][j])+str(tab_hopcount[5][j])+str(tab_reduc_SP[0][j])+'\t\t'+str(tab_reduc_SP[1][j])+'\t\t'+str(tab_reduc_MCNF[0][j])+'\t\t'+str(tab_reduc_MCNF[1][j])+"\n" for j in range (nb_cities)))

    fhopcount.write("".join(str(j)+'\t' \
                    +str(tab_hopcount[0][j])+'\t\t' \
                    +str(tab_hopcount[1][j])+'\t\t' \
                    +str(tab_hopcount[2][j])+'\t\t' \
                    +str(tab_hopcount[3][j])+'\t\t' \
                    +str(tab_hopcount[4][j])+'\t\t' \
                    +str(tab_hopcount[5][j])+'\t\t' \
                    +"{:.2f}\t\t{:.2f}\t\t{:.2f}\t\t{:.2f}\n" \
                    .format(tab_reduc_SP[0][j], tab_reduc_SP[1][j], tab_reduc_MCNF[0][j], tab_reduc_MCNF[1][j]) \
                    for j in range (nb_cities)))

print("Hop_Count Results written in file : hop_count.txt")




    

            
            