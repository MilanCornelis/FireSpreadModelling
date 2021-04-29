from pypdevs.simulator import Simulator
from coupledModel import CellSpace
import ConfigParser
import os


def clear_simout():
    print("Clearing folder")
    folder = "./simout/"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))

x = 51
y = 51

config = ConfigParser.ConfigParser()
config.read("settings.txt")
burn_x = int(config.get("myvars", "burn_x"))
burn_y = int(config.get("myvars", "burn_y"))
temperature = int(config.get("myvars", "temperature"))
wind_speed = int(config.get("myvars", "wind_speed"))
wind_dir = int(config.get("myvars", "wind_dir"))

# Clear the simout folder
clear_simout()

print("Simulation started")
sim = Simulator(CellSpace(x, y, burn_x, burn_y, temperature, wind_dir, wind_speed))
sim.setTerminationTime(100)
#sim.setCell(x, y, cell_file="./simout/celltrace", multifile=False)
sim.setCell(x, y, cell_file="./simout/celltrace-%05d", multifile=True)
sim.simulate()
print("Simulation finished")
