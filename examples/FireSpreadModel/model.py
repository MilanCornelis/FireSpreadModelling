import math
from pypdevs.DEVS import AtomicDEVS
from pypdevs.infinity import INFINITY
from operator import itemgetter

""" STATES """
INACTIVE = "inactive"
INITIAL = "initial"
UNBURNED = "unburned"
BURNING = "burning"
BURNED = "burned"
TO_BURNING = "to_burning"

""" VALUES """
T_BURNING = 999
T_BURNED = 333
FLN_THRESHOLD = 45.0
CELL_SIZE = 5


def computeFirelineIntensity():
    return 50.0


def rothermelModel():
    # TODO: make this the real Rothermel model formula
    return 5.0


def decomposeRateOfSpread(RoS, ltb_ratio, wind_dir):
    pi = math.pi
    #       N    NE    E      SE    S     SW       W       NW
    theta = [0, pi/4, pi/2, 3*pi/4, pi, 5*pi/4, 3*pi/2, 7*pi/4]

    for i in range(len(theta)):
        theta[i] += math.radians(wind_dir)

    RoS_i = [0, 0, 0, 0, 0, 0, 0, 0]

    # Find the parameters of the ellipse
    a = RoS/(math.sqrt(ltb_ratio**2 - 1) + ltb_ratio)
    b = ltb_ratio * a
    c = RoS - b

    # Find the x,y- components of the RoS in a certain direction on the ellipse
    for i in range(len(theta)):
        x = a*math.sin(theta[i])
        y = b*math.cos(theta[i]) + c
        RoS_i[i] = math.sqrt(x**2 + y**2)

    return RoS_i


def calculateBurnDelays(cell_size, RoS_i):
    t_i = [0, 0, 0, 0, 0, 0, 0, 0]
    long_side = math.sqrt(2*(cell_size**2))
    dir_i = ["N",        "NE",      "E",      "SE",       "S",      "SW",       "W",      "NW"]
    d_i = [cell_size, long_side, cell_size, long_side, cell_size, long_side, cell_size, long_side]

    # Calculate the burn delay in each direction
    for i in range(len(d_i)):
        t_i[i] = (d_i[i]/RoS_i[i], dir_i[i])

    # Sort in non decreasing order
    t_i = sorted(t_i, key=itemgetter(0), reverse=False)

    # Subtract the minimum delay from all others
    for i in range(1, len(t_i)):
        t_i[i] = (t_i[i][0]-t_i[0][0], t_i[i][1])

    return t_i


def getLengthToBreadthRatio(wind_speed):
    # TODO: make this a table with ratio's based on the wind speed
    return 2.0


def computeFireSpread(wind_dir, wind_speed):
    RoS = rothermelModel()                                  # Calculate the main rate of spread
    ltb = getLengthToBreadthRatio(wind_speed)               # Get the dimensions of the ellipse
    RoS_i = decomposeRateOfSpread(RoS, ltb, wind_dir)       # 1D -> 2D

    # Calculate and return the burn delays in the main directions
    return calculateBurnDelays(CELL_SIZE, RoS_i)


def updateOrderContainer(order):
    # Remove the first element
    del order[0]

    # Subtract the minimum delay from all others
    for i in range(1, len(order)):
        order[i] = (order[i][0]-order[0][0], order[i][1])

    return order


class CellState(object):
    def __init__(self, temp):
        self.temperature = temp
        self.phase = INITIAL
        self.elapsed = 0.0

    def toCellState(self):
        return self.temperature


class Cell(AtomicDEVS):
    def __init__(self, x, y, temperature, wind_dir, wind_speed):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x, y))
        self.state = CellState(temperature)
        self.order = [0, 0, 0, 0, 0, 0, 0, 0]
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed

        # Position of the cell
        self.x = x
        self.y = y

        # Create in- and output ports
        self.inputs = [self.addInPort("inN"), self.addInPort("inNE"), self.addInPort("inE"), self.addInPort("inSE"),
                       self.addInPort("inS"), self.addInPort("inSW"), self.addInPort("inW"), self.addInPort("inNW")]
        self.outputs = [self.addOutPort("outN"), self.addOutPort("outNE"), self.addOutPort("outE"),
                        self.addOutPort("outSE"), self.addOutPort("outS"), self.addOutPort("outSW"),
                        self.addOutPort("outW"), self.addOutPort("outNW")]

        self.taMap = {INACTIVE: INFINITY, INITIAL: 0.0, UNBURNED: 1.0, TO_BURNING: 0.0, BURNING: 0.0, BURNED: INFINITY}
        self.dirs = {"N": 0, "NE": 1, "E": 2, "SE": 3, "S": 4, "SW": 5, "W": 6, "NW": 7}
        self.dir = "N"
        self.t_i = 0.0

    def intTransition(self):
        if self.state.phase == INITIAL:
            self.state.phase = UNBURNED
        elif self.state.phase == TO_BURNING:
            self.order = computeFireSpread(self.wind_dir, self.wind_speed)
            self.dir = self.order[0][1]
            self.t_i = self.order[0][0]
            # Update the order container
            self.order = updateOrderContainer(self.order)
            self.state.phase = BURNING
            self.state.temperature = T_BURNING
        elif self.state.phase == BURNING and len(self.order) > 0:
            self.dir = self.order[0][1]
            self.t_i = self.order[0][0]
            # Update the order container
            self.order = updateOrderContainer(self.order)
            self.state.phase = BURNING
            self.state.temperature = T_BURNING
        elif self.state.phase == BURNING and len(self.order) == 0:
            self.state.phase = BURNED
            self.state.temperature = T_BURNED
        return self.state

    def extTransition(self, inputs):
        # Skip this function if the cell is already burning
        if self.state.phase == BURNING:
            return self.state

        for i in range(self.inputs.__len__()):
            if self.inputs[i] in inputs:
                if (computeFirelineIntensity() > FLN_THRESHOLD) and (self.state.phase == UNBURNED):
                    self.state.phase = TO_BURNING
                    return self.state
        return self.state

    def outputFnc(self):
        if self.state.phase == BURNING:
            return {self.outputs[self.dirs[self.dir]]: [T_BURNING]}
        return {}

    def timeAdvance(self):
        if self.state.phase == BURNING and len(self.order) > 0:
            return self.t_i
        else:
            return self.taMap[self.state.phase]


class BurningCell(AtomicDEVS):
    def __init__(self, x, y, wind_dir, wind_speed):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x, y))
        self.state = CellState(125)
        self.order = [0, 0, 0, 0, 0, 0, 0, 0]
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed

        # Position of the cell
        self.x = x
        self.y = y

        # Create in- and output ports (inputs are not used, just for easier cell space creation)
        self.inputs = [self.addInPort("inN"), self.addInPort("inNE"), self.addInPort("inE"), self.addInPort("inSE"),
                       self.addInPort("inS"), self.addInPort("inSW"), self.addInPort("inW"), self.addInPort("inNW")]
        self.outputs = [self.addOutPort("outN"), self.addOutPort("outNE"), self.addOutPort("outE"),
                        self.addOutPort("outSE"), self.addOutPort("outS"), self.addOutPort("outSW"),
                        self.addOutPort("outW"), self.addOutPort("outNW")]

        self.taMap = {INACTIVE: INFINITY, INITIAL: 0, BURNING: 0.0, UNBURNED: 1.0, BURNED: INFINITY}
        self.dirs = {"N": 0, "NE": 1, "E": 2, "SE": 3, "S": 4, "SW": 5, "W": 6, "NW": 7}
        self.dir = "N"
        self.t_i = 0.0

    def intTransition(self):
        if self.state.phase == INITIAL:
            self.state.phase = UNBURNED
        elif self.state.phase == UNBURNED:
            self.order = computeFireSpread(self.wind_dir, self.wind_speed)
            self.dir = self.order[0][1]
            self.t_i = self.order[0][0]
            # Update the order container
            self.order = updateOrderContainer(self.order)
            self.state.phase = BURNING
        elif self.state.phase == BURNING and len(self.order) > 0:
            self.state.temperature = T_BURNING
            self.dir = self.order[0][1]
            self.t_i = self.order[0][0]
            # Update the order container
            self.order = updateOrderContainer(self.order)
            self.state.phase = BURNING
        elif self.state.phase == BURNING and len(self.order) == 0:
            self.state.temperature = T_BURNED
            self.state.phase = BURNED
        return self.state

    # TODO: output function still has to be written
    def outputFnc(self):
        if self.state.phase == BURNING:
            return {self.outputs[self.dirs[self.dir]]: [T_BURNING]}
        return {}

    def timeAdvance(self):
        if self.state.phase == BURNING and len(self.order) > 0:
            return self.t_i
        else:
            return self.taMap[self.state.phase]
