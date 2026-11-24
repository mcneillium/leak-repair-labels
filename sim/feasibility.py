"""Feasibility only: can L-TOWN.inp be loaded and simulated with a leak added, and how long does it take?

No result of the study is computed here.
"""
import sys
import time
from pathlib import Path

import wntr

inp = Path(sys.argv[1])
wn = wntr.network.WaterNetworkModel(str(inp))
print("Junctions:", wn.num_junctions, "Pipes:", wn.num_pipes, "Tanks:", wn.num_tanks, "Reservoirs:", wn.num_reservoirs, "Pumps:", wn.num_pumps)
print("Hydraulic step (s):", wn.options.time.hydraulic_timestep, "Duration (h):", wn.options.time.duration / 3600)
print("Demand patterns:", len(wn.pattern_name_list), "Pattern step (s):", wn.options.time.pattern_timestep)

for days in (1, 7):
    wn = wntr.network.WaterNetworkModel(str(inp))
    wn.options.time.duration = days * 24 * 3600
    start = time.time()
    results = wntr.sim.EpanetSimulator(wn).run_sim()
    took = time.time() - start
    flow = results.link["flowrate"]
    print(f"EPANET, {days} day(s): {took:.1f} s; time steps {len(flow)}")

wn = wntr.network.WaterNetworkModel(str(inp))
wn.options.time.duration = 2 * 24 * 3600
wn.options.hydraulic.demand_model = "PDD"
junction = wn.get_node(wn.junction_name_list[100])
junction.add_leak(wn, area=0.0005, start_time=24 * 3600, end_time=2 * 24 * 3600)
start = time.time()
results = wntr.sim.WNTRSimulator(wn).run_sim()
took = time.time() - start
leak = results.node["leak_demand"][junction.name]
print(f"WNTR simulator with one leak, 2 days: {took:.1f} s; leak flow before {leak.iloc[:200].max()*3600:.2f} m3/h, after start {leak.iloc[-10:].mean()*3600:.2f} m3/h")
