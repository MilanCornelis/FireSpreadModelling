import numpy as np


def getTerrainData():
    terrain = "./examples/FireSpreadModel/terrain.txt"
    f = open(terrain, 'r')
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

    return np.array(data)
