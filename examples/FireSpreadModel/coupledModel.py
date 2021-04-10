from pypdevs.DEVS import CoupledDEVS
from model import Cell, BurningCell


class CellSpace(CoupledDEVS):
    def __init__(self, x_max, y_max, burn_x, burn_y, temperature, wind_dir, wind_speed):
        CoupledDEVS.__init__(self, "FireSpread")

        # Create the cell space
        print("Creating cell space: START")
        cells = []
        for x in range(x_max):
            row = []
            for y in range(y_max):
                if x == burn_x and y == burn_y:
                    row.append(self.addSubModel(BurningCell(x, y, wind_dir, wind_speed)))
                else:
                    row.append(self.addSubModel(Cell(x, y, temperature, wind_dir, wind_speed)))
            cells.append(row)
        print("Creating cell space: END")

        # Connect all the cells in the cell space according to the moore neighborhood
        print("Connecting all cells in the cell space: START")
        for x in range(x_max):
            for y in range(y_max):
                if not(x == x_max-1):
                    self.connectPorts(cells[x][y].outputs[0], cells[x+1][y].inputs[4])          # N -> S
                if not(y == y_max-1):
                    self.connectPorts(cells[x][y].outputs[2], cells[x][y+1].inputs[6])          # E -> W
                    if not(x == 0):
                        self.connectPorts(cells[x][y].outputs[3], cells[x-1][y+1].inputs[7])    # SE -> NW
                    if not(x == x_max-1):
                        self.connectPorts(cells[x][y].outputs[1], cells[x+1][y+1].inputs[5])    # NE -> SW
                if not(x == 0):
                    self.connectPorts(cells[x][y].outputs[4], cells[x-1][y].inputs[0])          # S -> N
                if not(y == 0):
                    self.connectPorts(cells[x][y].outputs[6], cells[x][y-1].inputs[2])          # W -> E
                    if not(x == 0):
                        self.connectPorts(cells[x][y].outputs[5], cells[x-1][y-1].inputs[1])    # SW -> NE
                    if not(x == x_max-1):
                        self.connectPorts(cells[x][y].outputs[7], cells[x+1][y-1].inputs[3])    # NW -> SE
        print("Connecting all cells in the cell space: END")
