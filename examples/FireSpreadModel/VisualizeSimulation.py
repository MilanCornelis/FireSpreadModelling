import matplotlib.pyplot as plt
import os
import numpy as np


folder = "./examples/FireSpreadModel/simout/"
fig, ax = plt.subplots()
for filename in os.listdir(folder):
    file_path = os.path.join(folder, filename)
    try:
        if os.path.isfile(file_path):
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
            ax.imshow(data, vmin=-15.0, vmax=30.0)
            ax.invert_yaxis()
            fig.show()
            plt.pause(0.01)
    except Exception as e:
        print("Failed: %s. Reason: %s" % (file_path, e))
