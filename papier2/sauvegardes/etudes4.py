"""
README
makes computations on pingmesh data
print
"""
import os
import os, sys
import matplotlib.pyplot as plt
import numpy as np

FIC_RES="fichier_resultats_pings"
RECIPROQUE=False #""" considérer les chemins A->B et B->A comme la même mesure """
dico={'isls':{},'isls2':{},'isls2b':{},'isls2c':{}, 'isls2d':{}, 'isls2e':{}}


def nom_algo(algo):
	if algo=='isls':
		return 'Shortest path'
	if algo=='isls2':
		return 'UMCF'
	return algo  


def add_dico(cle, n1, n2, t, debitISL, val):
	if (n1,n2, t) in dico[cle]:
		if debitISL in dico[cle][(n1,n2,t)]:
			dico[cle][(n1,n2,t)][debitISL].append(val)
		else:
			dico[cle][(n1,n2,t)][debitISL]=[val]
	else:
		dico[cle][(n1,n2,t)]={debitISL:[val]}

#cmap=plt.get_cmap('rainbow')
#dico_couleurs={cle:cmap(i/len(dico)) for i,cle in enumerate(dico.keys())}


def retrouveLogsBrutRecursif(chemin_initial=".",exclure={'tcp'}):#,'2022-05-06'}):
	trouves=[]
	aChercher=[chemin_initial]
	while aChercher:
		nom=aChercher.pop()
		if "logs_ns3" in nom:
			trouves.append(nom)
		else:
			for glob in os.listdir(nom):
				x=os.path.join(nom,glob)  
				if os.path.isdir(x) and all([not motif in x for motif in exclure]):
					aChercher.append(x)
	return trouves


def repartiteurLogBrut(dossier, reciproque=RECIPROQUE):
	chemin_pingmesh="pingmesh.csv"
	algos=('isls2d', 'isls2e', 'isls2b', 'isls2c', 'isls2', 'isls')
	for algo in algos:
		if algo in dossier:
			cle=algo
			break 
	y=os.path.join(dossier,"udp_bursts_outgoing.csv")
	x=os.path.join(dossier,chemin_pingmesh)
	################# get commodities for current simulation
	if not (os.path.isfile(y) and os.path.isfile(x)):
		#print(x,dossier,"pas de donnees")
		return
	commodites=set()

	with open(y,'r') as fic:
		for line in fic:
			donnees=eval(line)
			src,dst=donnees[1:3]
			commodites.add((src,dst))	

	################ add data in main dict
	debitISL=dossier.split("pairing_")[1].split('_')[0]
	with open(x, "r") as fic:
		for line in fic:
			data_split = line.strip().split(',')
			reply_arrived_str = data_split[-1]
			if reply_arrived_str != "YES":
				#there is no data
				continue
			from_node_id, to_node_id, j, sendRequestTimestamps, replyTimestamps, receiveReplyTimestamps, \
                        latency_to_there_ns, latency_from_there_ns, rtt_ns = eval(','.join(data_split[:-1]))
			
			n1,n2=from_node_id, to_node_id
			# select ping pairs. To study only pings on commodities,
			# the test should be like "if (n1,n2) not in commodites: continue""
			if (n1,n2) not in commodites:# and cle!="isls":
				continue
			
			if reciproque:
				n1,n2=min(n1,n2),max(n1,n2)
				add_dico(cle, n1, n2, round(sendRequestTimestamps*1e-9), debitISL, latency_to_there_ns*1e-9)
				add_dico(cle, n1, n2, round(replyTimestamps*1e-9), debitISL, latency_from_there_ns*1e-9)
			else:
				add_dico(cle, n1, n2, round(sendRequestTimestamps*1e-9), debitISL, latency_to_there_ns*1e-9)
				add_dico(cle, n2, n1, round(replyTimestamps*1e-9), debitISL, latency_from_there_ns*1e-9)


#Etude par commodités
def enregistreur_logs(reciproque=RECIPROQUE):
	for algo,dic in dico.items():
		lignes=[]
		ratios={}
		nb_mesures={}
		lignes.append('src/dst  [débitISL: moyenne, mesures, ecart-type] ..\n')
		for srcdst,di in dic.items():
			caracs=''
			for isl,vals in di.items():
				caracs+=f'\t  {isl}: {np.mean(vals):.2f}, {len(vals)}, {np.std(vals):.2f}'
				if not isl in nb_mesures:
					nb_mesures[isl]=0
					ratios[isl]=[]
				ratios[isl].append(np.mean(vals))
				nb_mesures[isl]+=len(vals)
			lignes.append('{},{} {}\n'.format(*srcdst,caracs))
		if reciproque:
			methode='aller-retour'
		else:
			methode='simple'
		caracs=''
		for isl in sorted(ratios.keys(),key=lambda x:int(x)):
			vals=ratios[isl]
			caracs+=f'\t  {isl}Mb/s: moyenne des rapports {np.mean(vals):.2f}, écart-type de {np.std(vals):.2f} pour {len(vals)} mesures répétées {nb_mesures[isl]/len(vals):.1f} fois chacune\n'
			
		lignes.insert(0, f"global: {len(dic)} débits {methode} mesurés\n"
						f"{caracs}")

		with open("{}_{}.txt".format(FIC_RES,algo),"w") as f:
			f.writelines(lignes)
		print(algo)
		print(lignes[0])


#Etude par sources
def affiche_logs_sources(reciproque=RECIPROQUE):
	fig, this_ax = plt.subplots()
	#fig.suptitle("Comparison of the median pings per source")
	assert RECIPROQUE==False
	cmaps = [plt.get_cmap('Oranges'), plt.get_cmap('Purples')]
	for i_algo,(algo,dic) in enumerate([elt for elt in dico.items() if elt[0]=='isls' or elt[0]=='isls2']):
		lignes=[]
		ratios={}
		nb_mesures={}
		quantiles=[0.05,0.5]
		lignes.append('src  [débitISL: mesures, moy, ecart-type ] ..\n')
		#lignes.append(f'src  [débitISL: mesures, quantiles {quantiles}] ..\n')
		sources={}

		""" to study statistics on time evolution
		for srcdst in dic.keys():
			if (src:=srcdst[0]) not in sources:
				sources[src]={}
			t=srcdst[2]
			for isl,vals in dic[srcdst].items():
				if isl not in sources[src]:
					sources[src][isl]={}
				if t not in sources[src][isl]:
					sources[src][isl][t]=[]
				for val in vals:
					sources[src][isl][t].append(val)
		for src, d in sources.items():
			for isl, sd in d.items():
				temp_l=[]
				for t, l in sd.items():
					print(f"{src}, {isl}, {t}, {round(np.mean(l),3)}, {round(np.std(l),3)}, {len(l)}")
					temp_l.append(np.median(l))
				d[isl]=temp_l"""
		for srcdst in dic.keys():
			if (src:=srcdst[0]) not in sources:
				sources[src]={}
			for isl,vals in dic[srcdst].items():
				if isl not in sources[src]:
					sources[src][isl]=[]
				for val in vals:
					sources[src][isl].append(val)

		x,y=[],{}
		for src in sorted(sources):
			caracs=''
			for isl in sources[src]:	
				vals=sources[src][isl]	
				#caracs+=('\t  {}: {}, '+','.join(['{:.2f}']*len(quantiles))).format(isl,len(vals),*np.quantile(vals,quantiles))
				caracs+=('\t  {}: {}, '+','.join(['{:.2f}']*len(quantiles))).format(isl,len(vals),np.mean(vals), np.std(vals))
				if not isl in y:
					y[isl]=[]
				y[isl].append(np.median(vals))
				#print(algo, len(vals))
			lignes.append('{} {}\n'.format(src,caracs))
			x.append(src)
		
		colors=cmaps[i_algo](np.linspace(1,0,len(y),endpoint=False))
		for nb,isl in enumerate(sorted(y, key= lambda val:int(val))):
			this_ax.step(range(len(y[isl])),sorted(y[isl]), where='mid', color=colors[nb], marker=("2" if algo=='isls' else " "), label=f"{nom_algo(algo)}@ISL {isl}Mb/s")
			#axs[i_algo%2,i_algo//2].step(x, y[isl], where='mid', label=isl)

		this_ax.legend()
		with open("{}_{}_sources.txt".format(FIC_RES,algo),"w") as f:
			f.writelines(lignes)	
	fig.text(0.5, 0.01, 'sorted source stations', ha='center')
	fig.text(0.01, 0.5, 'median measured latency', va='center', rotation='vertical')	
	fig.tight_layout()
	
	nomfic="comparisonv4b"
	if len(sys.argv) > 1:
		nomfic+=' '.join(sys.argv[1:])
	#plt.savefig(nomfic+".png")
	plt.show()	


dossiers=retrouveLogsBrutRecursif()
for i,dos in enumerate(dossiers):
	print(f"repartition données: {i}/{len(dossiers)}")
	repartiteurLogBrut(dos)
#enregistreur_logs()
affiche_logs_sources()

