# ns-3 experiments

Given that you have generated the constellation dynamic state data over time in 
`satgenpy`, here you can run the ns-3 experiments used in the paper.


## Traffic matrix load

**Explanation**

A traffic matrix, which is a random reciprocal permutation pairing,
is used to load the network. Entries in the traffic matrix correspond
to long-living TCP flows.


**Parameters**
ns3 parameters are set by step1_generate_runs2.py which uses arguments and deduces some parameters. 
General statistics are collected during the simulation, and more specific ones from the commodity 91 (Buenos-Aires to Chongqing).
Currently, templates ending by `2.properties` in templates are used for tcp and udp protocols.

**Results**
raw results are collected in runs/....
After getting them you can use
- results.py -> used to compare routing algorithms
- logs.py -> used to analyse TCP behaviour in commodity 91 (use `tcp_flow_enable_logging_for_tcp_flow_ids = set([list_of_commodities_indices])` in template)
- mesh.py -> used to get rtt measurements at regular timesteps. (see paper/ns3_experiments/a_b to edit templates and step1_generate_runs.py). Unlike in logs, ns3 performs pings at regular timesteps, this is not an RTT estimation

results can be visualized in satviz
