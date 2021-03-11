from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY


class CellState(object):
    def __init__(self, value):
        self.temperature = value

    def toCellState(self):
        return self.temperature


class Cell(AtomicDEVS):
    def __init__(self, x, y):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x,y))
        self.temp = CellState(25)
        self.state = "initial"
        self.elapsed = 0.0

        # Position of the cell
        self.x = x
        self.y = y

        # Create in- and output ports
        self.inputs = self.addInPort("inT")
        self.outputs = self.addOutPort("outT")

    def intTransition(self):
        if self.state == "initial":
            return "unburned"
        elif self.state == "burning":
            self.temp.temperature = 30
            return "burned"

    def extTransition(self, inputs):
        inp = inputs[self.inputs]
        if inp == "show_burned":
            self.temp.temperature = 500
            return "burning"
        return self.state

    def outputFnc(self):
        if self.state == "initial":
            return {self.outputs: "show_unburned"}
        elif self.state == "unburned":
            return {self.outputs: "show_burning"}
        elif self.state == "burning":
            return {self.outputs: "show_burned"}

    def timeAdvance(self):
        state = self.state
        return {"initial": 0,
                "unburned": INFINITY,
                "burning": 200,
                "burned": INFINITY}[state]


class BurningCell(AtomicDEVS):
    def __init__(self, x, y):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x,y))
        self.temp = CellState(25)
        self.state = "initial"
        self.elapsed = 0.0
        self.temperature = 50

        # Position of the cell
        self.x = x
        self.y = y

        # Create in- and output ports
        self.outputs = self.addOutPort("outT")

    def intTransition(self):
        if self.state == "initial":
            return "unburned"
        elif self.state == "unburned":
            self.temp.temperature = 500
            return "burning"
        elif self.state == "burning":
            self.temp.temperature = 30
            return "burned"

    def outputFnc(self):
        if self.state == "initial":
            return {self.outputs: "show_unburned"}
        elif self.state == "unburned":
            return {self.outputs: "show_burning"}
        elif self.state == "burning":
            return {self.outputs: "show_burned"}

    def timeAdvance(self):
        state = self.state
        return {"initial": 0,
                "unburned": 500,
                "burning": 100,
                "burned": INFINITY}[state]
