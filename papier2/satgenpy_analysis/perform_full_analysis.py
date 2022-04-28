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

import exputil
import time
import sys
import os

local_shell = exputil.LocalShell()
max_num_processes = 6

# Check that no screen is running
if local_shell.count_screens() != 0:
    print("There is a screen already running. "
          "Please kill all screens before running this analysis script (killall screen).")
    exit(1)

# Re-create data directory
#local_shell.remove_force_recursive("data")
if not "data" in [obj for obj in os.listdir('.') if os.path.isdir(obj)]:
	local_shell.make_full_dir("data")
if not "command_logs" in [obj for obj in os.listdir('data') if os.path.isdir(obj)]:
	local_shell.make_full_dir("data/command_logs")

# Where to store all commands
commands_to_run = []

# Manual
params=sys.argv[1:]
print("Generating commands for manually selected endpoints pair (printing of routes and RTT over time)...")
if len(params)>1:
	nom_fic = '_'.join([params[0].lstrip('main_').rstrip('.py')]+params[3:-1])#main_kuiper_630.py 200 50 isls_none ground_stations_paris_moscow_grid algorithm_free_one_only_gs_relays ${num_threads}
	pas=params[2]
	duree=params[1]
	with open("../satellite_networks_state/commodites.temp", "r") as f:
		list_comms=eval(f.readline())
	for (src,dst,_) in list_comms:
		nompartiel_log = "_".join([params[0].lstrip('main_').rstrip('.py'),str(src),"to",str(dst)])+".log"
		commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
						"../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
						"{} "
						" {} {} {} {} "
						"> ../papier2/satgenpy_analysis/data/command_logs/manual_{} 2>&1".format(nom_fic,pas,duree,src,dst,nompartiel_log))
		commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
						"../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
						"{} "
						" {} {} {} {} "
						"> ../papier2/satgenpy_analysis/data/command_logs/manual_graphical_{} 2>&1".format(nom_fic,pas,duree,src,dst,nompartiel_log))


else:
	#Moskva-(Moscow) to Dallas-Fort-Worth with only ISLs on Telesat
	commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
		                   "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
		                   "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
		                   " 5000 20 363 381 "
		                   "> ../papier2/satgenpy_analysis/data/command_logs/manual_telesat_isls_372_to_411.log 2>&1")
	commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
		                   "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
		                   "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
		                   " 5000 20 363 381 "
		                   "> ../papier2/satgenpy_analysis/data/command_logs/manual_graphical_telesat_isls_372_to_411.log 2>&1")

	#Moskva-(Moscow) to Dallas-Fort-Worth with only ISLs on Telesat
	commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
		                   "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
		                   "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
		                   " 5000 20 372 411 "
		                   "> ../papier2/satgenpy_analysis/data/command_logs/manual_telesat_isls_372_to_411.log 2>&1")
	commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
		                   "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
		                   "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
		                   " 5000 20 372 411 "
		                   "> ../papier2/satgenpy_analysis/data/command_logs/manual_graphical_telesat_isls_372_to_411.log 2>&1")

# Constellation comparison
print("Generating commands for constellation comparison...")
for satgenpy_generated_constellation in [
	"telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2b",
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2c"
]:
    for duration_s in [26]:
        list_update_interval_ms = [2000]

        # Path
        for update_interval_ms in list_update_interval_ms:
            commands_to_run.append(
                "cd ../../satgenpy; "
                "python -m satgen.post_analysis.main_analyze_path "
                "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/%s %d %d "
                "> ../papier2/satgenpy_analysis/data/command_logs/constellation_comp_path_%s_%dms_for_%ds.log "
                "2>&1" % (
                    satgenpy_generated_constellation, update_interval_ms, duration_s,
                    satgenpy_generated_constellation, update_interval_ms, duration_s
                )
            )

        # RTT
        for update_interval_ms in list_update_interval_ms:
            commands_to_run.append(
                "cd ../../satgenpy; "
                "python -m satgen.post_analysis.main_analyze_rtt "
                "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/%s %d %d "
                "> ../papier2/satgenpy_analysis/data/command_logs/constellation_comp_rtt_%s_%dms_for_%ds.log "
                "2>&1" % (
                    satgenpy_generated_constellation, update_interval_ms, duration_s,
                    satgenpy_generated_constellation, update_interval_ms, duration_s
                )
            )

        # Time step path
        commands_to_run.append(
            "cd ../../satgenpy; "
            "python -m satgen.post_analysis.main_analyze_time_step_path "
            "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/%s %s %d "
            "> ../papier2/satgenpy_analysis/data/command_logs/constellation_comp_time_step_path_%s_%ds.log "
            "2>&1" % (
                satgenpy_generated_constellation,
                ",".join(list(map(lambda x: str(x), list_update_interval_ms))),
                duration_s,
                satgenpy_generated_constellation,
                duration_s
            )
        )

# Run the commands
print("Running commands (at most %d in parallel)..." % max_num_processes)
for i in range(len(commands_to_run)):
    print("Starting command %d out of %d: %s" % (i + 1, len(commands_to_run), commands_to_run[i]))
    local_shell.detached_exec(commands_to_run[i])
    while local_shell.count_screens() >= max_num_processes:
        time.sleep(2)

# Awaiting final completion before exiting
print("Waiting completion of the last %d..." % max_num_processes)
while local_shell.count_screens() > 0:
    time.sleep(2)
print("Finished.")
