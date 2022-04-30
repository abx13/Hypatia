## Démarrage rapide

Changement d'algorithme appliqué aux couches de Telesat

étapes:
 + Installer hypatia comme prévu avec `hypatia_install_dependencies.sh` et `hypatia_build.sh` à la racine du projet. 
 + Les calculs de MultiCommodity Network Flow ont besoin de Gurobi. Gurobi propose des licenses académiques. Gurobipy ne suffit pas, il faut télécharger la librairie Gurobi Optimizer, et activer les fonctionnalités avec une license Gurobi.
 + configurer paper2.sh selon les spécifications du test à mener. 
	 + paper2.sh renvoie aussi vers d'autres fichiers pour certains modifier certains aspects de la simulation.
 + récupérer les résultats
	+ dans satgenpy_analysis/data pour les tests networkX
	+ dans ns3_experiments/traffic_matrix_load/runs pour les résultats des simulations ns3.
	+ éventuellement, lancer des scripts du dossier satviz pour des objets 3D
	
## Résumé de hypatia: 
+ hypatia/ns3+sat+sim contient le simulateur ns3 + des modules spécifiques dans contrib
	+ le fichier principal est hypatia/ns3+sat+sim/simulator/scratch/main_satnet/main_satnet.cc
+ hypatia/paper contient les précédentes simulations menées précédemment par Simon snkas
+ hypatia/paper2 contient les scripts de configuration de la topologie et de ns3, ainsi que les résultats lorsque le script paper2.sh a été correctement executé
+ hypatia/satgenpy contient la génération des constellations, du routage, et des outils d'analyse.
+ hypatia/satviz permet de générer les visualisations 3D avec Cesium
	+ À noter pour césium: il faut créer un compte sur https://cesium.com/ion/signup/tokens pour récupérer un token
	+  copier le token dans hypatia/satviz/static_html/top.html
	+  modifier les fichiers à analyser des scripts de hypatia/satviz/scripts et les exécuter
	+  ouvrir les fichiers générés dans hypatia/satviz/viz_output.
		+  dans certains cas, Firefox refuse par défaut de télécharger le javascript permettant de visualiser. Solution temporaire: ouvrir la console dans "outils de développement" : une erreur est levée sur le fichier https://cesiumjs.org/releases/1.57/Build/Cesium/Cesium.js Il suffit d'accepter de le télécharger malgré les risques de sécurité (partage du jeton cesium)


