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

local_shell = exputil.LocalShell()
max_num_processes = 6

# Check that no screen is running
if local_shell.count_screens() != 0:
    print("There is a screen already running. "
          "Please kill all screens before running this analysis script (killall screen).")
    exit(1)

# Re-create data directory
local_shell.remove_force_recursive("data")
local_shell.make_full_dir("data")
local_shell.make_full_dir("data/command_logs")

# Where to store all commands
commands_to_run = []

# Manual
print("Generating commands for manually selected endpoints pair (printing of routes and RTT over time)...")

commands_to_run = []

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

#New-York-Newark to Toronto with only ISLs on Telesat 
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 360 407"
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_telesat_isls_360_to_407.log 2>&1")
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 360 407"
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_graphical_telesat_isls_360_to_407.log 2>&1")

#Ankara to Chengdu with only ISLs on Telesat 
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 430 392 "
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_telesat_isls_430_to_392.log 2>&1")
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 430 392 "
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_graphical_telesat_isls_430_to_392.log 2>&1")

#Paris to Boston with only ISLs on Telesat 
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 375 439 "
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_telesat_isls_375_to_439.log 2>&1")
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 375 439 "
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_graphical_telesat_isls_375_to_439.log 2>&1")

# Barcelona to Chittagong with only ISLs on Telesat
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 420 433 "
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_telesat_isls_420_to_433.log 2>&1")
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 420 433 "
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_graphical_telesat_isls_420_to_433.log 2>&1")

# Santiago to Bangalore with only ISLs on Telesat
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 401 379 "
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_telesat_isls_401_to_379.log 2>&1")
commands_to_run.append("cd ../../satgenpy; python -m satgen.post_analysis.main_print_graphical_routes_and_rtt "
                       "../papier2/satgenpy_analysis/data ../papier2/satellite_networks_state/gen_data/"
                       "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2 "
                       "5000 20 401 379 "
                       "> ../papier2/satgenpy_analysis/data/command_logs/manual_graphical_telesat_isls_401_to_379.log 2>&1")

# Constellation comparison
print("Generating commands for constellation comparison...")
for satgenpy_generated_constellation in [
    "telesat_1015_isls_plus_grid_ground_stations_top_100_algorithm_free_one_only_over_isls2"
]:
    for duration_s in [20]:
        list_update_interval_ms = [5000]

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
