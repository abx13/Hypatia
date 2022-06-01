graines=(1 10 11)
for graine in ${graines[@]}; do
	echo graine: $graine
	sed -i 's/random.seed([0-9]*)/random.seed('${graine}')/' ./ns3_experiments/traffic_matrix_load/step_1_generate_runs2.py
	./paper2.sh
	destdir="sauvegardes/svgde_$(date +'%F-%H%M')_${graine}"
	mkdir $destdir
	cp -R -t $destdir ns3_experiments/traffic_matrix_load/runs/run*
	#cp -R -t $destdir satellite_networks_state/gen_data/*
	cd ns3_experiments/traffic_matrix_load || exit 1
	python runs_results.py > ../../${destdir}/seed${graine}.txt
	cd ../.. || exit 1
done
