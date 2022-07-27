"""
README
print raw results from ns3 simulation runs. 
For each simulation, calculates the sum of the results of all commodities.
"""
import os
#------------------------------------#
#        PARAMETRES A CHANGER        #
#------------------------------------#
mbps = 10
tps_simu = "_20"
#------------------------------------#

chemin_tcp="/logs_ns3/tcp_flows.csv"
chemin_udp="/logs_ns3/udp_bursts_incoming.csv","/logs_ns3/udp_bursts_outgoing.csv"
dossiers=sorted([runsdoss for doss in os.listdir("runs") if os.path.isdir(runsdoss:="runs/"+doss) and tps_simu in doss])

for doss in dossiers:
	qte,nbpkt,i=0,0,0
	if "udp" in doss:
		nbpktrec,nbpktem=0,0
		qterec,qteem=0,0
		if not (os.path.isfile(doss+chemin_udp[0]) and os.path.isfile(doss+chemin_udp[1])):
			print(doss,"pas de donnees")
			continue
		with open(doss+chemin_udp[0], "r") as infic,\
		open(doss+chemin_udp[1], "r") as outfic:
			outlines=outfic.readlines()
			inlines=infic.readlines()
			for i,inline in enumerate(inlines):
				resi=eval(inline)
				reso=eval(outlines[i])
				nbpktrec+=resi[8]
				nbpktem+=reso[8]
				qteem+=reso[10]/125000
				qterec+=resi[10]/125000
		print(doss,", [recus/emis] qtes: {:.2f}/{:.2f}Mb nb: {}/{}".format(qterec,qteem,nbpktrec,nbpktem))

		file = 'results_udp_'+str(mbps)+'_Mbps_for_'+str(tps_simu)+'s.txt'
		with open(file,'a') as fresudp :
			fresudp.write(" ".join("[recus/emis] qtes: {:.2f}/{:.2f}Mb nb: {}/{} \n".format(qterec,qteem,nbpktrec,nbpktem)))
	else:
		if not os.path.isfile(doss+chemin_tcp):
			print(doss,"pas de donnees")
			continue
		with open(doss+chemin_tcp, "r") as fic:
			finished=0
			for line in fic:
				res=line.split(',')
				qte+=int(res[7])/125000
				i+=1
				finished+=(res[8]=="YES")
		print(doss,", qte transmise: {:.2f}Mb, finis: {}/{}".format(qte,finished,i))
