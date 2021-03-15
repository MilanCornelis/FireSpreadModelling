from pypdevs.simulator import Simulator
from coupledModel import CellSpace


# Cell devs doesn't work
sim = Simulator(CellSpace())

sim.setVerbose()
#sim.setTerminationTime(2000)
#sim.setClassicDEVS()
sim.setCell(1, 1, cell_file="celltrace-%05d", multifile=False)
sim.simulate()
