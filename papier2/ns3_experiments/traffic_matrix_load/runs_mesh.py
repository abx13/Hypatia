"""
README
When enabling mesh in ns3 simulation
plot rtts from ping measurements
"""
import os
import matplotlib.pyplot as plt
chemin_ping="/logs_ns3/pingmesh.csv"
dossiers=sorted([runsdoss for doss in os.listdir("runs") if os.path.isdir(runsdoss:="runs/"+doss)])
for doss in dossiers:
	t=[]
	rtts=[]
	nbperdus=0
	if "tcp" in doss and os.path.isfile(doss+chemin_ping):
		print(doss)
		with open(doss+chemin_ping, "r") as pngfic:
# from_node_id, to_node_id, j, sendRequestTimestamps[j], replyTimestamps[j], receiveReplyTimestamps[j], latency_to_there_ns, latency_from_there_ns, rtt_ns, reply_arrived_str.c_str()
			for line in pngfic:
				datas=line.strip().split(',')
				t.append(int(datas[3])/(10**9))
				rtts.append(int(datas[8])/(10**6)*(datas[-1]=="YES"))
				nbperdus+=(datas[-1]!="YES")
		#plt.title(doss)
		plt.plot(t,rtts,label=doss)
		print("nb perdus : {}/{}".format(nbperdus,len(t)))
		#print("temps",t)
		#print('rtts',rtts)
		
plt.title("Evolution du RTT")
plt.xlabel("temps sim(s)")
plt.ylabel("rtt mesuré (ms)")
plt.legend()
plt.show()
	
