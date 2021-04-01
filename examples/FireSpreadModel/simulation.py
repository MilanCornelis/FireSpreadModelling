from pypdevs.simulator import Simulator
from coupledModel import CellSpace
import ConfigParser

x = 11
y = 11

config = ConfigParser.ConfigParser()
config.read("settings.txt")
burn_x = int(config.get("myvars", "burn_x"))
burn_y = int(config.get("myvars", "burn_y"))
temperature = int(config.get("myvars", "temperature"))
wind_speed = int(config.get("myvars", "wind_speed"))
wind_dir = int(config.get("myvars", "wind_dir"))

sim = Simulator(CellSpace(x, y, burn_x, burn_y, temperature))
sim.setTerminationTime(250)
sim.setCell(x, y, cell_file="./simout/celltrace", multifile=False)
sim.simulate()
print("Simulation finished")
