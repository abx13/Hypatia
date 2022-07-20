#generates a file with commodities and cities
with open("ground_stations_cities_sorted_by_estimated_2025_pop_top_200.basic.txt", "r") as f:
	villes=f.readlines()

with open("../commodites.temp") as f:
	coms=f.readlines()

coms=eval(coms[0])
#for telesat_1015 (27*13=351 satellites
dico_villes={int(ligne.split(",")[0])+351 : ligne.split(",")[1] for ligne in villes}

with open("commodites.txt", "w") as f:
	for idcom,com in enumerate(coms):
		f.write("id {} : from {} ({}) to {} ({})\n".format(idcom,dico_villes[com[0]],com[0],dico_villes[com[1]],com[1]))

