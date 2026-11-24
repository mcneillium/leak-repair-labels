"""Feasibility only: time a 7-day WNTR run with two leaks, and a 7-day EPANET run with one emitter."""
import sys
import time

import wntr

INP = sys.argv[1]

wn = wntr.network.WaterNetworkModel(INP)
wn.options.time.duration = 7 * 24 * 3600
wn.options.hydraulic.demand_model = "PDD"
for i, start_day in ((100, 2), (400, 4)):
    j = wn.get_node(wn.junction_name_list[i])
    j.add_leak(wn, area=0.0005, start_time=start_day * 24 * 3600, end_time=7 * 24 * 3600)
start = time.time()
wntr.sim.WNTRSimulator(wn).run_sim()
print(f"WNTR simulator, 7 days, two leaks: {time.time() - start:.1f} s")

wn = wntr.network.WaterNetworkModel(INP)
wn.options.time.duration = 7 * 24 * 3600
wn.get_node(wn.junction_name_list[100]).emitter_coefficient = 0.0005
start = time.time()
res = wntr.sim.EpanetSimulator(wn).run_sim()
print(f"EPANET, 7 days, one emitter (fixed all week): {time.time() - start:.1f} s")
