from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY

""" STATES """
INACTIVE = "inactive"
INITIAL = "initial"
UNBURNED = "unburned"
BURNING = "burning"
BURNED = "burned"

""" VALUES """
TIME_STEP = 0.01
T_BURNING = 999
T_BURNED = 333


def convert(s):
    new = ""
    for x in s:
        new += x
    return new


class CellState(object):
    def __init__(self, temp):
        self.temperature = temp
        self.phase = INITIAL
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

        self.taMap = {INACTIVE: 0, INITIAL: 0, UNBURNED: 1.0, BURNING: 5.0, BURNED: INFINITY}

    def intTransition(self):
        self.state.elapsed += self.timeAdvance()
        if self.state.phase == INITIAL:
            self.state.phase = UNBURNED
        elif self.state.phase == BURNING:
            self.state.phase = BURNED
            self.state.temperature = T_BURNED
        return self.state

    def extTransition(self, inputs):
        for i in range(self.inputs.__len__()):
            if self.inputs[i] in inputs:
                if inputs[self.inputs[i]][0] == T_BURNING and self.state.phase != BURNED:
                    self.state.temperature = inputs[self.inputs[i]][0]
                    self.state.phase = BURNING
        return self.state

    def outputFnc(self):
        if self.state.phase == BURNING:
            return {self.outputs[0]: [T_BURNING], self.outputs[1]: [T_BURNING], self.outputs[2]: [T_BURNING],
                    self.outputs[3]: [T_BURNING], self.outputs[4]: [T_BURNING], self.outputs[5]: [T_BURNING],
                    self.outputs[6]: [T_BURNING], self.outputs[7]: [T_BURNING]}
        return {}

    def timeAdvance(self):
        return self.taMap[self.state.phase]


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

        self.taMap = {INACTIVE: 0, INITIAL: 0, UNBURNED: 1.0, BURNING: 10.0, BURNED: INFINITY}

    def intTransition(self):
        self.state.elapsed += self.timeAdvance()
        if self.state.phase == INITIAL:
            self.state.phase = UNBURNED
        elif self.state.phase == UNBURNED:
            self.state.temperature = T_BURNING
            self.state.phase = BURNING
        elif self.state.phase == BURNING:
            self.state.temperature = T_BURNED
            self.state.phase = BURNED
        return self.state

    def outputFnc(self):
        if self.state.phase == BURNING:
            return {self.outputs[0]: [T_BURNING], self.outputs[1]: [T_BURNING], self.outputs[2]: [T_BURNING],
                    self.outputs[3]: [T_BURNING], self.outputs[4]: [T_BURNING], self.outputs[5]: [T_BURNING],
                    self.outputs[6]: [T_BURNING], self.outputs[7]: [T_BURNING]}
        return {}

    def timeAdvance(self):
        return self.taMap[self.state.phase]
