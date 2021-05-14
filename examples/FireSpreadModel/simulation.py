from pypdevs.simulator import Simulator
from coupledModel import CellSpace
import numpy as np
import ConfigParser, os
import threading, time, sys
import matplotlib.pyplot as plt


def visualize():
    time.sleep(1)
    folder = "./examples/FireSpreadModel/simout/"
    files = []
    new_file = True

    fig, ax = plt.subplots()
    while new_file:
        for filename in os.listdir(folder):
            if new_file:
                new_file = False
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) and filename not in files:
                    new_file = True
                    files.append(filename)
                    f = open(file_path, 'r')
                    rows = f.read().split('\n')
                    rows = rows[0:len(rows) - 1]
                    data = []
                    for row in rows:
                        values = []
                        split_data = row.split(' ')
                        split_data = split_data[:len(split_data) - 1]
                        for i in split_data:
                            values.append(int(i))
                        data.append(values)

                    data = np.array(data)

                    plt.cla()
                    ax.imshow(data, vmin=100.0, vmax=6000.0)
                    ax.invert_yaxis()
                    fig.show()
                    plt.pause(0.01)
            except Exception as e:
                print("Failed: %s. Reason: %s" % (file_path, e))

    sys.exit()


def clear_simout():
    print("Clearing folder")
    folder = "./examples/FireSpreadModel/simout/"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


def simulate():
    x = 51
    y = 51

    config = ConfigParser.ConfigParser()
    config.read("./examples/FireSpreadModel/settings.txt")
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
    # sim.setCell(x, y, cell_file="./simout/celltrace", multifile=False)
    sim.setCell(x, y, cell_file="./examples/FireSpreadModel/simout/celltrace-%05d", multifile=True)
    sim.simulate()
    print("Simulation finished")


if __name__ == "__main__":
    vis_thread = threading.Thread(target=visualize)
    sim_thread = threading.Thread(target=simulate)
    sim_thread.start()
    vis_thread.start()
