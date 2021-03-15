from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY


class CellState(object):
    def __init__(self, temp):
        self.temperature = temp
        self.phase = "initial"

    def toCellState(self):
        return self.temperature


class Cell(AtomicDEVS):
    def __init__(self, x, y):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x,y))
        self.state = CellState(25)
        self.elapsed = 0.0

        # Position of the cell
        self.x = x
        self.y = y

        # Create in- and output ports
        self.inputs = self.addInPort("inT")
        self.outputs = self.addOutPort("outT")

    def intTransition(self):
        if self.state.phase == "initial":
            self.state.phase = "unburned"
            return self.state
        elif self.state == "burning":
            self.state.phase = "burned"
            self.state.temperature = 50
            return self.state

    def extTransition(self, inputs):
        inp = inputs[self.inputs]
        if inp == "show_burned":
            self.state.phase = "burning"
            self.state.temperature = 250
        return self.state

    def outputFnc(self):
        if self.state.phase == "initial":
            return {self.outputs: "show_unburned"}
        elif self.state.phase == "unburned":
            return {self.outputs: "show_burning"}
        elif self.state.phase == "burning":
            return {self.outputs: "show_burned"}

    def timeAdvance(self):
        state = self.state.phase
        return {"initial": 0,
                "unburned": INFINITY,
                "burning": 200,
                "burned": INFINITY}[state]


class BurningCell(AtomicDEVS):
    def __init__(self, x, y):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x,y))
        self.state = CellState(25)
        self.elapsed = 0.0

        # Position of the cell
        self.x = x
        self.y = y

        # Create in- and output ports
        self.outputs = self.addOutPort("outT")

    def intTransition(self):
        if self.state.phase == "initial":
            self.state.phase = "unburned"
            return self.state
        elif self.state.phase == "unburned":
            self.state.temperature = 250
            self.state.phase = "burning"
            return self.state
        elif self.state.phase == "burning":
            self.state.temperature = 50
            self.state.phase = "burned"
            return self.state

    def outputFnc(self):
        if self.state.phase == "initial":
            return {self.outputs: "show_unburned"}
        elif self.state.phase == "unburned":
            return {self.outputs: "show_burning"}
        elif self.state.phase == "burning":
            return {self.outputs: "show_burned"}

    def timeAdvance(self):
        state = self.state.phase
        return {"initial": 0,
                "unburned": 300,
                "burning": 100,
                "burned": INFINITY}[state]
