"ce script permet de faire la moyenne sur les différents fichiers csv obtenus"
"pour différentes graines "

import os

graines = [1, 10, 11]

date = "2002-06-14-2242"

avg_cwnd = 0
avg_rtt = 0
avg_progress = 0

mbps = 5
tps_simu = 240

commodity = "91"

i=0

destdir="sauvegardes/svgde_"+date+"_"
doss = "/run_loaded_tm_pairing_"+mbps+"_Mbps_for_"+tps_simu+"s_with_tcp_algorithm_free_one_only_over_isls/logs_ns3"


with open(destdir+str(graines[0])+doss+"tcp_flow_"+commodity+"_cwnd.csv","r") as fcwnd0,\
     open(destdir+str(graines[1])+doss+"tcp_flow_"+commodity+"_cwnd.csv","r") as fcwnd1,\
     open(destdir+str(graines[2])+doss+"tcp_flow_"+commodity+"_cwnd.csv","r") as fcwnd2,\

     open(destdir+str(graines[0])+doss+"tcp_flow_"+commodity+"_progress.csv","r") as fprog0,\
     open(destdir+str(graines[1])+doss+"tcp_flow_"+commodity+"_progress.csv","r") as fprog1,\
     open(destdir+str(graines[2])+doss+"tcp_flow_"+commodity+"_progress.csv","r") as fprog2,\
     
     open(destdir+str(graines[0])+doss+"tcp_flow_"+commodity+"_rtt.csv","r") as frtt0,\
     open(destdir+str(graines[1])+doss+"tcp_flow_"+commodity+"_rtt.csv","r") as frtt1,\
     open(destdir+str(graines[2])+doss+"tcp_flow_"+commodity+"_rtt.csv","r") as frtt2:

    
    avg_cwnd += 
    cwnds=fcwnd.readlines()
    progres=fprog.readlines()
    rtts=frtt.readlines()

