from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY


def convert(s):
    new = ""
    for x in s:
        new += x
    return new


class CellState(object):
    def __init__(self, temp):
        self.temperature = temp
        self.phase = "initial"
        self.elapsed = 0.0

    def toCellState(self):
        return self.temperature


class Cell(AtomicDEVS):
    def __init__(self, x, y, temperature):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x,y))
        self.state = CellState(temperature)

        # Position of the cell
        self.x = x
        self.y = y

        # Create in- and output ports
        self.inputs = [self.addInPort("inN"), self.addInPort("inNE"), self.addInPort("inE"), self.addInPort("inSE"),
                       self.addInPort("inS"), self.addInPort("inSW"), self.addInPort("inW"), self.addInPort("inNW")]
        self.outputs = [self.addOutPort("outN"), self.addOutPort("outNE"), self.addOutPort("outE"), self.addOutPort("outSE"),
                        self.addOutPort("outS"), self.addOutPort("outSW"), self.addOutPort("outW"), self.addOutPort("outNW")]

    def intTransition(self):
        if self.state.phase == "initial":
            self.state.phase = "unburned"
        elif self.state.phase == "unburned":
            return self.state
        elif self.state.phase == "burning":
            self.state.phase = "burned"
            self.state.temperature = 333
        return self.state

    def extTransition(self, inputs):
        inp = inputs[self.inputs]
        inp = convert(inp)
        if inp.__contains__("show_burned") and self.state.phase != "burned":
            self.state.phase = "burning"
            self.state.temperature = 999
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
                "unburned": 1,
                "burning": 1,
                "burned": INFINITY}[state]


class BurningCell(AtomicDEVS):
    def __init__(self, x, y):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x,y))
        self.state = CellState(125)

        # Position of the cell
        self.x = x
        self.y = y

        # Create in- and output ports (inputs are not used, just for easier cell space creation)
        self.inputs = [self.addInPort("inN"), self.addInPort("inNE"), self.addInPort("inE"), self.addInPort("inSE"),
                       self.addInPort("inS"), self.addInPort("inSW"), self.addInPort("inW"), self.addInPort("inNW")]
        self.outputs = [self.addOutPort("outN"), self.addOutPort("outNE"), self.addOutPort("outE"), self.addOutPort("outSE"),
                        self.addOutPort("outS"), self.addOutPort("outSW"), self.addOutPort("outW"), self.addOutPort("outNW")]

    def intTransition(self):
        if self.state.phase == "initial":
            self.state.phase = "unburned"
        elif self.state.phase == "unburned":
            self.state.temperature = 999
            self.state.phase = "burning"
        elif self.state.phase == "burning":
            self.state.temperature = 333
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
                "unburned": 1,
                "burning": 1,
                "burned": INFINITY}[state]
