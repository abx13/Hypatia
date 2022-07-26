"""
README

"""

import os
import matplotlib.pyplot as plt
import numpy as np
import math

#------------------------------------#
#        PARAMETRES A CHANGER        #
#------------------------------------#
mbps = 10
tps_simu = 20
timestep_ms = 2000
nb_cities = 100
tab_isls = ["isls", "isls2", "isls3"]
nb_algo_SP = 2
nb_algo_MCNF = 2
constellation = "telesat_1015"

#------------------------------------#

#clear file
file = 'hop_count.txt'
with open(file,'w') as fhopcount :
    print("")

def read_hop_file(file):
    path_at_0 = file.readlines()[0].strip().split(',')
    hop_count = path_at_0[1].split('-')
    number_sat = len(hop_count)-2
    return number_sat

#####
#EXECUTION

#creating tabs
#tab_init = [0 for i in range (nb_cities)]
#tab_hopcount = [tab_init for i in range (len(tab_isls))]
tab_hopcount = []
for _ in range(len(tab_isls)):
    tab_hopcount.append([])

tab_init = [0 for i in range (nb_cities)]
tab_reduc_SP = [tab_init for i in range (nb_algo_MCNF - 1)]

tab_init = [0 for i in range (nb_cities)]
tab_reduc_MCNF = [tab_init for i in range (nb_algo_MCNF - 1)]



doss = "../../satgenpy_analysis/data/"
interdoss1 = str(constellation)+"_isls_plus_grid_ground_stations_top_"+str(nb_cities)+"_algorithm_free_one_only_over_"
interdoss2 = '/'+str(timestep_ms)+"ms_for_"+str(tps_simu)+"s/manual/data/"
#getting all the folders from satgenpy_analysis/data/
#net = sorted([runsdoss for networkx in os.listdir("../../"+doss) if os.path.isdir(runsdoss:= "../../"+doss) ])



for i in range (len(tab_isls)) :
    net = sorted(os.listdir(doss+interdoss1+tab_isls[i]+interdoss2))
    for networkx in net:
        if "path" in networkx:
            with open(doss+interdoss1+tab_isls[i]+interdoss2+networkx, "r") as f_hop_count :
                tab_hopcount[i].append(read_hop_file(f_hop_count))
                
                

for j in range (nb_cities) : 
    tab_reduc_SP[0][j] = (tab_hopcount[2][j] - tab_hopcount[0][j]) / tab_hopcount[0][j]
    tab_reduc_MCNF[0][j] = (tab_hopcount[1][j] - tab_hopcount[0][j]) / tab_hopcount[0][j]

avg_reduc_SP = sum(tab_reduc_SP[0])/len(tab_reduc_SP[0])
avg_reduc_MCNF = sum(tab_reduc_MCNF[0])/len(tab_reduc_MCNF[0])


#write in a file the 3 closest satellites for each GS :
file = 'hop_count.txt'
with open(file,'a') as fhopcount :
    fhopcount.write("".join("AVERAGE REDUCTION SP : "+ str(avg_reduc_SP)+"\n"))
    #fhopcount.write("".join("AVERAGE REDUCTION MCNF : "+ str(avg_reduc_MCNF+"\n\n")))

    fhopcount.write("".join("ID"+'\t'+"ISLS"+'\t'+"ISLS2"+'\t'+"ISLS3"+'\t'+"ReducISLS-ISLS3"+"\n"))
    fhopcount.write("".join(str(i)+'\t'+str(tab_hopcount[0][i])+'\t\t'+str(tab_hopcount[1][i])+'\t\t'+str(tab_hopcount[2][i])+'\t\t'+str(tab_reduc_SP[0][i])+"\n" for i in range (nb_cities)))

    #fhopcount.write("".join("ID"+'\t'+"ISLS"+'\t'+"ISLS 2"+'\t'+" ISLS 3"+'\t'+"ISLS 4"+"Reduc ISLS-ISLS3"+'\t'+"Reduc ISLS2-ISLS4"+"\n"))
    #fhopcount.write("".join(str(i)+'\t'+str(tab_hopcount[0][i])+'\t'+str(tab_hopcount[1][i])+'\t'+str(tab_hopcount[2][i])+'\t'+str(tab_hopcount[3][i])+str(tab_reduc_SP[0][i])+'\t'+str(tab_reduc_MCNF[1][i])+"\n" for i in range (nb_cities)))






    

            
            