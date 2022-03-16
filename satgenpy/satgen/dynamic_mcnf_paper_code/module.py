import os

modules_non_pointes=["multiprocessing"]
def depointe():
	""" enlever les '.' dans from .xxx import yyy -> on obtient from xxx import yyy"""
	for fic in (liste_fic:=os.listdir(".")):
		if os.path.isfile(fic) and not fic.startswith("_") and not fic.startswith('.'):
			with open(fic,"r") as fin:
				lignes=fin.readlines()
			with open(fic,'w') as fout:
				for i in range(len(lignes)):
					ligne=lignes[i]
					if ligne.startswith("from"):
						mots=ligne.split()
						mots[1]=mots[1].strip('.')
						lignes[i]=" ".join(mots)+"\n"
				fout.writelines(lignes)

def pointe():
	""" ajouter des '.' dans from xxx import yyy -> on obtient from .xxx import yyy"""
	for fic in (liste_fic:=os.listdir(".")):
		if os.path.isfile(fic) and not fic.startswith("_") and not fic.startswith('.'):
			with open(fic,"r") as fin:
				lignes=fin.readlines()
			with open(fic,'w') as fout:
				for i in range(len(lignes)):
					ligne=lignes[i]
					if ligne.startswith("from"):
						mots=ligne.split()
						if mots[1] not in modules_non_pointes:
							mots[1]="."+mots[1]
						lignes[i]=" ".join(mots)+"\n"
				fout.writelines(lignes)
						

