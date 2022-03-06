#generates a file with commodities and cities
# can be used to write "perform_full_analysis.py"
with open("ground_stations_cities_sorted_by_estimated_2025_pop_top_100.basic.txt", "r") as f:
	villes=f.readlines()

with open("../commodites.temp") as f:
	coms=f.readlines()

coms=eval(coms[0])
#for telesat_1015 (27*13=351 satellites
dico_villes={int(ligne.split(",")[0])+351 : ligne.split(",")[1] for ligne in villes}

with open("results.txt", "w") as f:
	for com in coms:
		f.write("{} to {} with only ISLs on Telesat 1000 100 {} {}".format(dico_villes[com[0]],dico_villes[com[1]],com[0],com[1]))

