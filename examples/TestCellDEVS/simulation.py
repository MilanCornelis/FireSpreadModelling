from pypdevs.simulator import Simulator
from coupledModel import CellSpace


sim = Simulator(CellSpace())

sim.setTerminationTime(50)
sim.setCell(2, 2, cell_file="./simout/celltrace", multifile=False)
sim.simulate()
