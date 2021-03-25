import math
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
FLN_THRESHOLD = 45


def convert(s):
    new = ""
    for x in s:
        new += x
    return new

def computeFirelineIntensity():
    return None

def rothermelModel():
    return 5

def decomposeRateOfSpread(RoS, ltb_ratio):
    # TODO: this decomposition requires a wind direction facing North,
    #  we need to add the wind direction to the equations

    pi = math.pi
    #       N    NE    E      SE    S     SW       W       NW
    theta = [0, pi/4, pi/2, 3*pi/4, pi, 5*pi/4, 3*pi/2, 7*pi/4]
    RoS_i = []

    # Find the parameters of the ellipse
    a = RoS/(math.sqrt(ltb_ratio**2 - 1) + ltb_ratio)
    b = ltb_ratio * a
    c = RoS - b

    # Find the x,y- components of the RoS in a certain direction on the ellipse
    for i in range(len(theta)):
        x = a*math.sin(theta[i])
        y = b*math.cos(theta[i]) + c
        RoS[i] = math.sqrt(x**2 + y**2)

    return RoS_i

def computeFireSpread():
    # Calculate the burn delays t_i = d_i/RoS_i
    # Do some fancy weird scheduling algorithm and tadaa, there is firespread :)
    return None

def getLengthToBreadthRatio():
    return 2


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
        self.outputs = [self.addOutPort("outN"), self.addOutPort("outNE"), self.addOutPort("outE"),
                        self.addOutPort("outSE"), self.addOutPort("outS"), self.addOutPort("outSW"),
                        self.addOutPort("outW"), self.addOutPort("outNW")]

        self.taMap = {INACTIVE: INFINITY, INITIAL: 0, UNBURNED: 1.0, BURNING: 5.0, BURNED: INFINITY}

    def intTransition(self):
        self.state.elapsed += self.timeAdvance()
        if self.state.phase == INITIAL:
            self.state.phase = UNBURNED
        elif self.state.phase == BURNING:
            self.state.phase = BURNED
            self.state.temperature = T_BURNED
        return self.state

    def extTransition(self, inputs):
        # Only receive inputs if the cell is not burning yet
        for i in range(self.inputs.__len__()):
            if self.inputs[i] in inputs:
                """fli = computeFirelineIntensity(0, 0, 0)
                if fli > getLengthToBreadthRatio() and self.state.phase != BURNED:
                    Set the cell to burning"""
                if inputs[self.inputs[i]][0] == T_BURNING and self.state.phase != BURNED:
                    self.state.temperature = inputs[self.inputs[i]][0]
                    self.state.phase = BURNING
        return self.state

    def outputFnc(self):
        """ Send message to neighbor when a fire has reached them """
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
        self.outputs = [self.addOutPort("outN"), self.addOutPort("outNE"), self.addOutPort("outE"),
                        self.addOutPort("outSE"), self.addOutPort("outS"), self.addOutPort("outSW"),
                        self.addOutPort("outW"), self.addOutPort("outNW")]

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
