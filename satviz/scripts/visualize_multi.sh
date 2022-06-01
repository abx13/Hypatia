fics=$(find ~/Documents/projetACS/hypatia/papier2/sauvegardes/ -type f -name isl_utilization.csv)

for fic in $fics; do 
	python visualize_utilization.py $fic
done
