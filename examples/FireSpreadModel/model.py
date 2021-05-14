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
T_BURNING = 30
T_BURNED = 10
FLN_THRESHOLD = 45.0
CELL_SIZE = 5

""" FUEL TYPES """
chaparral = {"w_o": 0.528, "delta": 6.0, "sigma": 1250.0, "h": 9500.0,
             "rho_p": 32.0, "M_f": 0.1, "S_T": 0.0555, "S_e": 0.01, "M_x": 0.15}
grass = {"w_o": 0.0253, "delta": 1.0, "sigma": 2000.0, "h": 8000.0,
         "rho_p": 32.0, "M_f": 0.05, "S_T": 0.0555, "S_e": 0.01, "M_x": 0.15}
sawgrass = {"w_o": 0.1012, "delta": 3.0, "sigma": 1500.0, "h": 8700.0,
         "rho_p": 32.0, "M_f": 0.1, "S_T": 0.0555, "S_e": 0.01, "M_x": 0.40}
sagebrush = {"w_o": 0.1265, "delta": 1.25, "sigma": 1500.0, "h": 8000.0,
         "rho_p": 32.0, "M_f": 0.1, "S_T": 0.0555, "S_e": 0.01, "M_x": 0.15}
pocosin = {"w_o": 0.3543, "delta": 4.0, "sigma": 1500.0, "h": 9000.0,
         "rho_p": 32.0, "M_f": 0.1, "S_T": 0.0555, "S_e": 0.01, "M_x": 0.15}

fuel = {"chaparral": chaparral,
        "grass": grass,
        "sawgrass": sawgrass,
        "sagebrush": sagebrush,
        "pocosin": pocosin}

"""
    Info of input parameters:
        - w_o: oven dry fuel loading                            [lb/ft^2]
        - delta: fuel depth                                     [ft]
        - sigma: fuel particle surface-area-to-volume ratio     [1/ft]
        - h: fuel particle low heat content                     [B.t.u./lb]
        - rho_p: oven dry particle density                      [lb/ft^3]
        - M_f: fuel particle moisture content                   [lb moisture / lb oven dry wood]
        - S_T: fuel particle total mineral content              [lb minerals / lb oven dry wood]
        - S_e: fuel particle effective mineral content          [lb silica-free minerals / lb oven dry wood]
        - U: wind velocity at midflame height                   [m/s]
        - slope: terrain slope                                  [degrees]
        - M_x: moisture content of extinction
            -> This term needs experimental determination. Currently using 0.3 which is the fiber saturation
            point of many dead fuels. For aerial fuels (beta < 0.02) with low wind velocity (< 2.23 m/s) M_x ~= 0.15
"""
def rothermelModel(w_o, delta, sigma, h, rho_p, M_f, S_T, S_e, U, slope, M_x):
    # Oven dry bulk density
    rho_b = w_o / delta

    # Packing ratio
    beta = rho_b/rho_p

    # Mineral damping coefficient
    eta_s = max(0.174 * S_e ** -0.19, 1.0)

    # Moisture damping coefficient
    eta_M = 1 - 2.59 * (M_f / M_x) + 5.11 * (M_f / M_x) ** 2 - 3.52 * (M_f / M_x) ** 3
    A = 1333*sigma**-0.7913

    # Optimum packing ratio
    beta_op = 3.348 * (sigma ** -0.8189)

    # Maximum reaction velocity
    gamma_max = (sigma ** 1.5) * (495 + 0.0594 * (sigma ** 1.5)) ** -1

    # Optimum reaction velocity
    gamma = gamma_max * ((beta / beta_op) ** A) * math.exp(A * (1 - beta/beta_op))

    # Net fuel loading
    w_n = w_o * (1 - S_T)

    # Reaction intensity
    I_r = gamma * w_n * h * eta_M * eta_s

    # Propagation flux ratio
    xi = (192 + 0.2595*sigma)**-1 * math.exp((0.792+0.681*sigma**0.5)*(beta+0.1))

    # Parameters for wind coefficient calculation
    C = 7.47*math.exp(-0.133*sigma**0.55)
    B = 0.02526*sigma**0.54
    E = 0.715*math.exp(-3.59*10**-4*sigma)

    # Convert wind speed from m/s to ft/min
    U *= 196.85039

    # Wind coefficient
    theta_w = C*U**B * (beta/beta_op)**-E

    # Slope factor
    theta_s = 5.275*beta**-0.3*math.tan(math.radians(slope))**2

    # Epsilon
    epsilon = math.exp(-138/sigma)

    # Heat of pre-ignition
    Q_ig = 250+1116*M_f

    return (I_r*xi*(1+theta_w+theta_s))/(rho_b*epsilon*Q_ig)    # [ft/min]


def decomposeRateOfSpread(RoS, wind_speed, wind_dir):
    pi = math.pi
    #       N    NE    E      SE    S     SW       W       NW
    theta = [0, pi/4, pi/2, 3*pi/4, pi, 5*pi/4, 3*pi/2, 7*pi/4]

    for i in range(len(theta)):
        theta[i] += math.radians(wind_dir)

    RoS_i = [0, 0, 0, 0, 0, 0, 0, 0]

    # Convert wind speed to mph
    wind_speed *= 0.6214
    # Calculate the length to breadth ratio
    ltb = 1 + 0.25 * wind_speed
    # Calculate the eccentricity
    e = math.sqrt(ltb**2 - 1)/ltb

    # Calculate the RoS in each direction and convert from ft/min to m/s
    for i in range(len(theta)):
        RoS_i[i] = RoS * (1-e)/(1-e*math.cos(theta[i]))
        RoS_i[i] *= 0.00508

    return RoS_i    # [m/s]


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


def computeFireSpread(wind_dir, wind_speed, slope, fuel_type):
    """ !!!MAKE SURE THAT ALL VARIABLES ARE FLOAT!!! """
    # The current fuel type is (living) chaparral
    RoS = rothermelModel(w_o=fuel[fuel_type]["w_o"],                      # Calculate the main rate of spread
                         delta=fuel[fuel_type]["delta"],
                         sigma=fuel[fuel_type]["sigma"],
                         h=fuel[fuel_type]["h"],
                         rho_p=fuel[fuel_type]["rho_p"],
                         M_f=fuel[fuel_type]["M_f"],
                         S_T=fuel[fuel_type]["S_T"],
                         S_e=fuel[fuel_type]["S_e"],
                         U=wind_speed,
                         slope=slope,
                         M_x=fuel[fuel_type]["M_x"])

    RoS_i = decomposeRateOfSpread(RoS, wind_speed, wind_dir)   # 1D -> 2D

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
    def __init__(self, x, y, temperature, fli, wind_dir, wind_speed, fuel_type):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x, y))
        self.state = CellState(temperature)
        self.order = [0, 0, 0, 0, 0, 0, 0, 0]
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed
        self.fuel_type = fuel_type

        if fuel_type != "water":
            self.fli = fli
        else:
            self.fli = 0.0

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
            self.order = computeFireSpread(self.wind_dir, self.wind_speed, 0.0, self.fuel_type)
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
                if (self.fli > FLN_THRESHOLD) and (self.state.phase == UNBURNED):
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
    def __init__(self, x, y, temperature, fli, wind_dir, wind_speed, fuel_type):
        AtomicDEVS.__init__(self, "Cell(%d,%d)" % (x, y))
        self.state = CellState(temperature)
        self.order = [0, 0, 0, 0, 0, 0, 0, 0]
        self.wind_dir = wind_dir
        self.wind_speed = wind_speed
        self.fli = fli
        self.fuel_type = fuel_type

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
            self.order = computeFireSpread(self.wind_dir, self.wind_speed, 0.0, self.fuel_type)
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

    def outputFnc(self):
        if self.state.phase == BURNING:
            return {self.outputs[self.dirs[self.dir]]: [T_BURNING]}
        return {}

    def timeAdvance(self):
        if self.state.phase == BURNING and len(self.order) > 0:
            return self.t_i
        else:
            return self.taMap[self.state.phase]
