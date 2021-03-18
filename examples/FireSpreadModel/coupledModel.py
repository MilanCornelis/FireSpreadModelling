from pypdevs.DEVS import CoupledDEVS
from model import Cell, BurningCell


class CellSpace(CoupledDEVS):
    def __init__(self, x_max, y_max, burn_x, burn_y, temperature):
        CoupledDEVS.__init__(self, "FireSpread")

        # Create all cells
        cells = []
        for x in range(x_max):
            row = []
            for y in range(y_max):
                if x == burn_x and y == burn_y:
                    row.append(self.addSubModel(BurningCell(x, y)))
                else:
                    row.append(self.addSubModel(Cell(x, y, temperature)))
            cells.append(row)

        # Connect the cells to create a cell space
        for x in range(x_max):
            for y in range(y_max):
                if x != 0 and x != (burn_x+1):
                    self.connectPorts(cells[x][y].outputs, cells[x-1][y].inputs)
                if y != y_max-1 and y != (burn_y-1):
                    self.connectPorts(cells[x][y].outputs, cells[x][y+1].inputs)
                if x != x_max-1 and x != (burn_x-1):
                    self.connectPorts(cells[x][y].outputs, cells[x+1][y].inputs)
                if y != 0 and y != (burn_y+1):
                    self.connectPorts(cells[x][y].outputs, cells[x][y-1].inputs)
