from pypdevs.DEVS import CoupledDEVS
from model import Cell, BurningCell


class CellSpace(CoupledDEVS):
    def __init__(self):
        CoupledDEVS.__init__(self, "FireSpread")

        # Cell Space
        # |2| ---> |3|
        #  ^        ^
        #  |        |
        # |0| ---> |1|

        self.cell0 = self.addSubModel(BurningCell(0,0))
        self.cell1 = self.addSubModel(Cell(0,1))
        self.cell2 = self.addSubModel(Cell(1,0))
        self.cell3 = self.addSubModel(Cell(1,1))

        # Test

        self.connectPorts(self.cell0.outputs, self.cell1.inputs)
        self.connectPorts(self.cell0.outputs, self.cell2.inputs)
        self.connectPorts(self.cell1.outputs, self.cell3.inputs)
        self.connectPorts(self.cell2.outputs, self.cell3.inputs)
