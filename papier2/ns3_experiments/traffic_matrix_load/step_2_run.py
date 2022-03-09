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
import sys
local_shell = exputil.LocalShell()

# Clear old runs
#local_shell.perfect_exec("rm -rf runs/*/logs_ns3")

# Get workload identifier from argument
num_machines = 1
args = sys.argv[1:]
if len(args) != 4 or int(args[0]) < 0 or int(args[0]) >= num_machines:
    raise ValueError("Need to have have first argument in range [0, %d) to pick workload" % num_machines)
workload_id = int(args[0])

# One-by-one run all experiments (such that they don't interfere with each other)
unique_id = 0

# Retrieve values from the config
data_rate_megabit_per_s = float(args[1])
duration_s = float(args[2])

for protocol_chosen in ["tcp", "udp"]:

	if (unique_id % num_machines) == workload_id:

		# Prepare run directory
		run_dir = "runs/run_loaded_tm_pairing_%d_Mbps_for_%ds_with_%s_%s" % (
			data_rate_megabit_per_s, duration_s, protocol_chosen, args[3]
		)
		logs_ns3_dir = run_dir + "/logs_ns3"
		local_shell.remove_force_recursive(logs_ns3_dir)
		local_shell.make_full_dir(logs_ns3_dir)

		# Perform run
		local_shell.perfect_exec(
			"cd ../../../ns3-sat-sim/simulator; "
			"./waf --run=\"main_satnet "
			"--run_dir='../../papier2/ns3_experiments/traffic_matrix_load/" + run_dir + "'\""
			" 2>&1 | tee '../../papier2/ns3_experiments/traffic_matrix_load/" + logs_ns3_dir + "/console.txt'",
			output_redirect=exputil.OutputRedirect.CONSOLE
		)

	unique_id += 1
