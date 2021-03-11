from pypdevs.simulator import Simulator
from coupledModel import CellSpace


sim = Simulator(CellSpace())
sim.setVerbose()
sim.setTerminationTime(2000)
sim.setClassicDEVS()
sim.simulate()
