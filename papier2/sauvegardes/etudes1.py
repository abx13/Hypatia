import os, sys
import matplotlib.pyplot as plt
import numpy as np
import scipy.optimize as opt

dico={'isls':{},'isls2':{},'isls2b':{},'isls2c':{}, 'isls2d':{}, 'isls2e':{}}
#cmap=plt.get_cmap('rainbow')
#dico_couleurs={cle:cmap(i/len(dico)) for i,cle in enumerate(dico.keys())}
couleurs=['tab:blue', "tab:orange", "tab:green", "tab:red", "tab:purple", 'tab:brown', 'tab:pink', 'tab:gray', "tab:olive", 'tab:cyan']
dico_couleurs={algo:couleur for algo,couleur in zip(dico.keys(),couleurs)}
ALPHA=0.2
nbvaleurs=0
def analyse(file):
	""" remplir le dictionnaire avec les valeurs des simulations """
	with open(file,"r") as f:
		for line in f:
			if 'udp' not in line:
				continue
			if "pas de donnees" in line:
				continue
			nomfic=file
			if '/' in nomfic:
				nomfic=nomfic.split('/')[-1]
			seed=int(nomfic.strip(".seedtxt"))
			isl=float(line.split('Mbps')[0].split('_')[-2])
			ratio=eval(line.split("qtes: ")[-1].split('Mb')[0])
			algo = line.split("one_only_over_")[1].split(" ,")[0]
			if seed in dico[algo]:
				dico[algo][seed].append((isl,ratio))
			else:
				dico[algo][seed]=[(isl,ratio)]
		

tous=os.listdir('.')
for glob in tous:
	if glob.startswith("seed"):
		analyse(glob)
	elif os.path.isdir(glob):
		subglobs=os.listdir(glob)
		for subglob in subglobs:
			if subglob.startswith("seed"):
				analyse('/'.join([glob,subglob]))


def optimise_data(x, y):
	# This is the function we are trying to fit to the data.
	def func(x, a, b, c):
		return a * np.exp(-b * x) + c
	# The actual curve fitting happens here
	optimizedParameters, pcov = opt.curve_fit(func, x, y)
	# Use the optimized parameters to plot the best fit
	return func, optimizedParameters, pcov
	
for i,(algo,val) in enumerate([elt for elt in dico.items() if elt[0]=='isls' or elt[0]=='isls2']):
	valeurs_algo={}
	for seed,listexy in val.items():
		x=[listexy[i][0] for i in range(len(listexy))]
		y=[listexy[i][1] for i in range(len(listexy))]
		plt.plot(x,y,color=dico_couleurs[algo],marker="*", linestyle='', alpha=ALPHA)
		nbvaleurs+=len(listexy)
		for xy in listexy:
			x,y=xy
			if x in valeurs_algo:
				valeurs_algo[x].append(y)
			else:
				valeurs_algo[x]=[y]
	X=sorted(valeurs_algo.keys())
	moy=np.array([np.mean(valeurs_algo[x]) for x in X])
	std=np.array([np.std(valeurs_algo[x]) for x in X])
	foptim,args_optim, pcov=optimise_data(np.array(X),moy)
	Xfit=np.linspace(X[0],X[-1],100)
	Yfit=foptim(Xfit,*args_optim)
	perr = np.sqrt(np.diag(pcov))
	#plt.fill_between(Xfit, foptim(Xfit,*(args_optim-perr)), foptim(Xfit,*(args_optim+perr)),color=dico_couleurs[algo], alpha=ALPHA)
	#moy=np.array([np.mean(valeurs_algo[x]) for x in X])
	#std=np.array([np.std(valeurs_algo[x]) for x in X])
	if algo=='isls':
		nom_algo='Shortest path'
	elif algo=='isls2':
		nom_algo='UMCF'
	if (pcov==float('inf')).any():
		#covariance matrix could not be estimated, curve won't fit well
		plt.errorbar(X, moy, 2*std, color=dico_couleurs[algo], label=nom_algo)
	else:
		#plot the 95% intervall of confidence
		plt.plot(Xfit, Yfit, color=dico_couleurs[algo], label=nom_algo)
		plt.errorbar(X, moy, 2*std, ls='', color=dico_couleurs[algo])
plt.legend()

plt.xlabel('ISL (Mb/s)')
plt.ylabel('ratio arrived/sent')	



#plt.legend()
nomfic="comparisonv1"
if len(sys.argv) > 1:
	nomfic+=' '.join(sys.argv[1:])
plt.savefig(nomfic+".png")
plt.show()
#print("nbvaleurs:",nbvaleurs/len(dico), "par courbe en moyenne")
			
