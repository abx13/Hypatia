# The MIT License (MIT)
#
# Copyright (c) 2020 ETH Zurich
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
  

#### README ##############################
# liste_arguments : constellation_file duration[s] timestep[ms] isls? Ground_stations? algorithm number_of_threads
# constellation_file : choose main_telesat_1015.py or main_kuiper_630.py . Edit other constellations in ./satellite_network_state and configure ./ns3_experiments/traffic_matrix_load/step_1_generate_runs2
# duration : any int 
# timestep : any int (so that duration%timestep == 0)
# isls : only "isls_plus_grid" was used
# GS : use ground_stations_top_100 or adapt ./ns3_experiments/traffic_matrix_load/step_1_generate_runs2 and other files
# algorithm : algorithm_free_one_only_over_isls (shortest path) or algorithm_free_one_only_over_isls2 (mcnf) or algorithm_free_one_only_over_isls2b (mcnf taking distances into account)
# threads number : adapt it to your computer
# 

# liste_debitISL : liste_debitISL[i] is related to liste_arguements[i]. Can be any number.
# other parameters : setup ./ns3_experiments/traffic_matrix_load/step_1_generate_runs2 especially `reference_rate` variable 

##########################################

liste_arguments=("main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2b 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2c 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2b 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2c 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2b 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2c 4")
liste_arguments=("main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4" \
		"main_telesat_1015.py 26 2000 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4")

#with default ~1Mb/s x 100 commodities,
#2Mb/s ISL throughput => strong overload in UDP
#4Mb/s ISL throughput => overload in shortest path
#10Mb/s ISL throughput => network oversized, no overload
liste_debitISL=("2" "2" "2" "2"\
	 		"4" "4" "4" "4"\
	 		"10" "10" "10" "10")
#values in Mb/s
liste_debitISL=("2" "4" "6" "8" "10"\
				"2" "4" "6" "8" "10")

if (( ${#liste_debitISL[@]} != ${#liste_arguments[@]} )); then
	echo liste_debitISL ${#liste_debitISL[@]} and liste_arguments ${#liste_arguments[@]} must have the same size
	exit 1
fi

for ((i=0; i<${#liste_arguments[@]}; ++i )) ; do
	debitISL="${liste_debitISL[$i]}"
	read -a arguments <<< "${liste_arguments[$i]}"
	
	#save debitISL in a simple place for graph generation. Used by mcnf
	echo $debitISL > satellite_networks_state/debitISL.temp
	
	### Create routing tables and generate constellation
	cd ns3_experiments || exit 1
	cd traffic_matrix_load || exit 1
	python step_1_generate_runs2.py $debitISL ${arguments[*]} || exit 1
	cd ../.. || exit 1

	### SATGENPY ANALYSIS
	# analysis  of path and rtt based on networkx.
	# edit variables 'satgenpy_generated_constellation', 'duration_s' 
	# and 'list_update_interval_ms' in perform_full_analysis according to `liste_arguments`
	cd satgenpy_analysis || exit 1
	#python perform_full_analysis.py ${arguments[*]} || exit 1
	cd .. || exit 1

	# NS-3 EXPERIMENTS
	cd ns3_experiments || exit 1
	cd traffic_matrix_load || exit 1
	python step_2_run.py 0 $debitISL ${arguments[1]} ${arguments[5]} || exit 1
	cd ..
	cd .. || exit 1

	unset debitISL
	unset arguments
done;

# global simulation plots
# not very interesting for network, 
# but gives an overview of simulation performance (goodput_rate vs slowdown and goodput vs runtime)
# results in hypatia/papier2/ns3_experiments/traffic_matrix_load/pdf
cd ns3_experiments || exit 1
cd traffic_matrix_load || exit 1
# python step_3_generate_plots.py || exit 1


# below scripts help to analyse simulation results. 
echo " "
echo " run logs analysis "
# python runs_logs.py #run when logs option is enabled in ns3 .properties files
#echo " run ping analysis "
#python runs_mesh.py #run when mesh option is enabled in ns3 .properties (see hypatia/paper/ns3_simulation/a_b example. look for "pingmesh" in step1_generate_runs.py and template files)
echo "final results"
python runs_results.py #total results. Determine which is the best algo at a glance
cd ..
cd .. || exit 1
