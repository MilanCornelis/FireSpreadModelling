from pypdevs.simulator import Simulator
from coupledModel import CellSpace


# Cell devs doesn't work
sim = Simulator(CellSpace())

#sim.setVerbose()
sim.setTerminationTime(2000)
#sim.setClassicDEVS()
sim.setCell(True, 0, 0, cell_file="celltrace", multifile=False)
sim.simulate()
