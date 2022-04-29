import os, sys
import matplotlib.pyplot as plt


dico={'isls':[],'isls2':[],'isls2b':[],'isls2c':[]}

def analyse(file):
	with open(file,"r") as f:
		for line in f:
			if 'udp' not in line:
				continue

			isl=float(line.split('Mbps')[0].split('_')[-2])
			print("ISL:",isl)
			ratio=eval(line.split("qtes: ")[-1].split('Mb')[0])
			algo = line.split("one_only_over_")[1].split(" ,")[0]
			print(file,algo,isl,ratio)
			dico[algo].append((isl,ratio))
			
			

tous=os.listdir('.')
for glob in tous:
	if glob.startswith("seed"):
		analyse(glob)
	elif os.path.isdir(glob):
		subglobs=os.listdir(glob)
		for subglob in subglobs:
			if subglob.startswith("seed"):
				analyse('/'.join([glob,subglob]))

for cle,val in dico.items():
	val.sort()
	x=[val[i][0] for i in range(len(val))]
	y=[val[i][1] for i in range(len(val))]
	plt.plot(x,y,'-*',label=cle)
plt.xlabel('ISL (Mb/s)')
plt.ylabel('ratio arrived/sent')
plt.legend()
nomfic="comparison"
if len(sys.argv) > 1:
	nomfic+=' '.join(sys.argv[1:])
plt.savefig(nomfic+".png")
plt.show()

			
