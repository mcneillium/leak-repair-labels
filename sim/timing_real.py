"""Feasibility only: time one week of L-TOWN_Real.inp in WNTR's pressure-driven simulator,
once with no leak and once with a single test leak. No night flow is computed and nothing is scored."""
import sys
import time

import wntr

INP = sys.argv[1]
WEEK = 7 * 24 * 3600

start = time.time()
wn = wntr.network.WaterNetworkModel(INP)
print(f"Load: {time.time() - start:.1f} s")
print("Junctions:", wn.num_junctions, "Pipes:", wn.num_pipes, "Patterns:", len(wn.pattern_name_list))

for label, leak in (("no leak", False), ("one test leak", True)):
    wn = wntr.network.WaterNetworkModel(INP)
    wn.options.time.duration = WEEK
    wn.options.hydraulic.demand_model = "PDD"
    if leak:
        junction = wn.get_node(wn.junction_name_list[100])
        junction.add_leak(wn, area=0.0005, start_time=3 * 24 * 3600, end_time=WEEK)
    start = time.time()
    results = wntr.sim.WNTRSimulator(wn).run_sim()
    took = time.time() - start
    print(f"WNTR simulator, 7 days, {label}: {took:.1f} s; time steps {len(results.link['flowrate'])}")
