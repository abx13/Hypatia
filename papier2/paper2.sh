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
# timestep : any int
# isls : only "isls_plus_grid" was used
# GS : use ground_stations_top_100 or adapt ./ns3_experiments/traffic_matrix_load/step_1_generate_runs2 and other files
# algorithm : algorithm_free_one_only_over_isls (shortest path) or algorithm_free_one_only_over_isls2 (mcnf)
# threads number : adapt it to your computer
# 
##########################################

liste_arguments=("main_telesat_1015.py 22 500 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls 4" \
		"main_telesat_1015.py 22 500 isls_plus_grid ground_stations_top_100 algorithm_free_one_only_over_isls2 4")
liste_debitISL=("20" "20") #Mb/s

for ((i=0; i<${#liste_arguments[@]}; ++i )) ; do
	debitISL="${liste_debitISL[$i]}"
	read -a arguments <<< "${liste_arguments[$i]}"
	echo $debitISL > satellite_networks_state/debitISL.temp
	cd ns3_experiments || exit 1
	# ns-3: Traffic matrix load
	cd traffic_matrix_load || exit 1
	python step_1_generate_runs2.py $debitISL ${arguments[*]} || exit 1
	cd ../.. || exit 1

	### SATGENPY ANALYSIS
	# analysis  of path and rtt based on networkx. edit
	#  variables 'satgenpy_generated_constellation', 'duration_s' 
	# and 'list_update_interval_ms' in perform_full_analysis
	cd satgenpy_analysis || exit 1
	python perform_full_analysis.py ${arguments[*]} || exit 1
	cd .. || exit 1

	# reprise NS-3 EXPERIMENTS
	cd ns3_experiments || exit 1
	cd traffic_matrix_load || exit 1
	python step_2_run.py 0 $debitISL ${arguments[1]} ${arguments[5]} || exit 1
	cd ..
	cd .. || exit 1

	## Figures
	#not used in matrix_load
	#cd figures || exit 1
	#python plot_all.py || exit 1
	#python generate_pngs.py || exit 1
	#cd .. || exit 1
	unset debitISL
	unset arguments
done;
cd ns3_experiments || exit 1
cd traffic_matrix_load || exit 1
python step_3_generate_plots.py || exit 1
cd ..
cd .. || exit 1
