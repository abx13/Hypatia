"""
README
print raw results from ns3 simulation runs. 
For each simulation, calculates the sum of the results of all commodities.
"""
import os
import os, sys
import matplotlib.pyplot as plt
import numpy as np

FIC_RES="fichier_resultats"
RECIPROQUE=False #""" considérer les chemins A->B et B->A comme la même mesure """
dico={'isls':{},'isls2':{},'isls2b':{},'isls2c':{}, 'isls2d':{}, 'isls2e':{}}
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
	chemin_udp="udp_bursts_incoming.csv","udp_bursts_outgoing.csv"
	algos=('isls2d', 'isls2e', 'isls2b', 'isls2c', 'isls2', 'isls')
	for algo in algos:
		if algo in dossier:
			cle=algo
			break 
	x=os.path.join(dossier,chemin_udp[0])
	y=os.path.join(dossier,chemin_udp[1])
	if not (os.path.isfile(x) and os.path.isfile(y)):
		print(x,dossier,"pas de donnees")
		return
	debitISL=dossier.split("pairing_")[1].split('_')[0]
	with open(x, "r") as infic,\
	open(y, "r") as outfic:
		outlines=outfic.readlines()
		inlines=infic.readlines()
		for i,inline in enumerate(inlines):
			resi=eval(inline)
			reso=eval(outlines[i])
			#qteem=reso[10]/125000
			#qterec=resi[10]/125000
			ratio=resi[10]/reso[10]
			n1,n2=resi[1],resi[2]
			if reciproque:
				n1,n2=min(n1,n2),max(n1,n2)
			if (n1,n2) in dico[cle]:
				if debitISL in dico[cle][(n1,n2)]:
					dico[cle][(n1,n2)][debitISL].append(ratio)
				else:
					dico[cle][(n1,n2)][debitISL]=[ratio]
			else:
				dico[cle][(n1,n2)]={debitISL:[ratio]}
		
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
	fig, axs = plt.subplots(2, 3, sharex=True, sharey=True)
	fig.suptitle("plots for differents algos")
	assert RECIPROQUE==False
	for i_algo,(algo,dic) in enumerate(dico.items()):
		lignes=[]
		ratios={}
		nb_mesures={}
		quantiles=[0.05,0.5]
		lignes.append(f'src  [débitISL: mesures, quantiles {quantiles}] ..\n')
		sources={}

		for srcdst in dic.keys():
			if (src:=srcdst[0]) not in sources:
				sources[src]={}
			for isl,vals in dic[srcdst].items():
				if isl not in sources[src]:
					sources[src][isl]=[]
				sources[src][isl].append(np.mean(vals))
		x,y=[],{}
		for src in sorted(sources):
			caracs=''
			for isl in sources[src]:	
				vals=sources[src][isl]	
				caracs+=('\t  {}: {}, '+','.join(['{:.2f}']*len(quantiles))).format(isl,len(vals),*np.quantile(vals,quantiles))
				if not isl in y:
					y[isl]=[]
				y[isl].append(np.median(vals))
			lignes.append('{} {}\n'.format(src,caracs))
			x.append(src)
		for isl in sorted(y):
			axs[i_algo%2,i_algo//2].step(range(len(y[isl])),sorted(y[isl]), where='mid', label=isl)
			#axs[i_algo%2,i_algo//2].step(x, y[isl], where='mid', label=isl)
		axs[i_algo%2,i_algo//2].set_title(f'algorithme: {algo}')
		axs[i_algo%2,i_algo//2].legend()
		#with open("{}_{}_sources.txt".format(FIC_RES,algo),"w") as f:
		#	f.writelines(lignes)	
	fig.text(0.5, 0.01, 'id station source', ha='center')
	fig.text(0.01, 0.5, 'ratio reçu/envoyé median', va='center', rotation='vertical')	
	fig.tight_layout()
	
	nomfic="comparisonv3"
	if len(sys.argv) > 1:
		nomfic+=' '.join(sys.argv[1:])
	plt.savefig(nomfic+".png")
	plt.show()	


dossiers=retrouveLogsBrutRecursif()
#print(dossiers)
for dos in dossiers:
	repartiteurLogBrut(dos)
enregistreur_logs()
affiche_logs_sources()
