#[tcp_flow_id],[now_in_ns],[progress_byte/cwnd_byte/rtt_ns]
"""
README
Plot results obtained when enabling logs in the ns3 simulation 
to see which commodity is involved, refer to hypatia/papier2/satellite_networks_state/input_data/commodites.txt
visualizations of the path can be found in the pdf files hypatia/papier2/satgenpy_analysis/data/*/*/manual/pdf
"""
import os
import matplotlib.pyplot as plt

#------------------------------------#
#        PARAMETRES A CHANGER        #
#------------------------------------#
graine = 11
date = "2022-06-23-2024"
mbps = 5
tps_simu = 120
#------------------------------------#



#Dossiers
doss_graine = "sauvegardes/svgde_"
interdoss="/logs_ns3/"

#couleurs différentes pour chaque algo
colours=['g','b']
fig,axes=plt.subplots(3,1, figsize=(16,9), dpi=80, facecolor="w", edgecolor='k')
label=['Plus court chemin', 'MCNF']
i=0


dossiers=sorted([runsdoss for doss in os.listdir("../../"+doss_graine+date+"_"+str(graine))  if os.path.isdir(runsdoss:= "../../"+doss_graine+date+"_"+str(graine)+"/"+doss) and str(tps_simu) in doss and str(mbps) in doss])

for doss in dossiers:
    #print(doss)
    fics=sorted([fic for fic in os.listdir("../../"+doss_graine+date+"_"+str(graine)+"/"+doss+interdoss) if os.path.isfile("../../"+doss_graine+date+"_"+str(graine)+"/"+doss+interdoss+fic) and "tcp_flow_" in fic])
    if fics:
        commodity=fics[0].split('_')[2]
        #print(commodity)
        with open(doss+interdoss+"tcp_flow_"+commodity+"_cwnd.csv","r") as fcwnd,\
            open(doss+interdoss+"tcp_flow_"+commodity+"_progress.csv","r") as fprog,\
            open(doss+interdoss+"tcp_flow_"+commodity+"_rtt.csv","r") as frtt:
            cwnds=fcwnd.readlines()
            progres=fprog.readlines()
            rtts=frtt.readlines()

        t_cwnds=[int(line.split(',')[1])/10**9 for line in cwnds]
        data_cwnds=[int(line.strip().split(',')[-1]) for line in cwnds]
        fig.suptitle('commodity id:'+cwnds[0].split(',')[0]+" from "+doss)
        #axes[0].title('cwnds id'+cwnds[0].split(',')[0]+" "+doss)
        axes[0].set_xlabel("temps simu(s)")
        axes[0].set_ylabel("cwnd (bytes)")
        axes[0].plot(t_cwnds,data_cwnds,colours[i], label=label[i])
        axes[0].legend(loc="upper left")

        t_rtts=[int(line.split(',')[1])/10**9 for line in rtts]
        data_rtts=[int(line.strip().split(',')[-1])/10**6 for line in rtts]
        #axes[1].title('RTTs id'+cwnds[0].split(',')[0]+" "+doss)
        axes[1].set_xlabel("temps simu(s)")
        axes[1].set_ylabel("rtts (ms)")
        axes[1].plot(t_rtts,data_rtts,colours[i], label=label[i])
        axes[1].legend(loc="upper left")

        t_prgs=[int(line.split(',')[1])/10**9 for line in progres]
        data_prgs=[int(line.strip().split(',')[-1]) for line in progres]
        #axes[2].title('progres id'+cwnds[0].split(',')[0]+" "+doss)
        axes[2].set_xlabel("temps simu(s)")
        axes[2].set_ylabel("progres (bytes)")
        axes[2].plot(t_prgs,data_prgs,colours[i], label=label[i])
        axes[2].legend(loc="upper left")
        
        i+=1


plt.show()
