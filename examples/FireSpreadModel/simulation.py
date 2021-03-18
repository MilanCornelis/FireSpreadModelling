from pypdevs.simulator import Simulator
from coupledModel import CellSpace

x = 11
y = 11
burn_x = 8
burn_y = 5
temperature = 100
sim = Simulator(CellSpace(x, y, burn_x, burn_y, temperature))

sim.setTerminationTime(100)
sim.setCell(x, y, cell_file="./simout/celltrace", multifile=False)
sim.simulate()
