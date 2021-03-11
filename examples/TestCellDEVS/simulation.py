from pypdevs.simulator import Simulator
from coupledModel import CellSpace


# Cell devs doesn't work
sim = Simulator(CellSpace())
sim.cell = True
sim.cell_file = "celltrace"
sim.cell_multifile = False
sim.setVerbose()
sim.setTerminationTime(2000)
sim.setClassicDEVS()
sim.simulate()
