from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY


class CellState(object):
    def __init__(self, value):
        self.value = value


    def toCellState(self):
        # Simply return the value, but could also first
        # perform some operations on the value
        return self.value


class Cell(AtomicDEVS):
    def __init__(self, x, y):
        AtomicDEVS.__init__(self, 'Cell(%i, %i)' % (x, y))
        self.x = x
        self.y = y
        self.state = "unburned"
        self.inputs = [self.addInPort("inN"), self.addInPort("inNE"), self.addInPort("inE"),
                       self.addInPort("inSE"), self.addInPort("inS"), self.addInPort("inSW"),
                       self.addInPort("inW"), self.addInPort("inNW"), self.addInPort("inWeather"),
                       self.addInPort("inIgniter")]
        self.outputs = [self.addOutPort("outN"), self.addOutPort("outNE"), self.addOutPort("outE"),
                        self.addOutPort("outSE"), self.addOutPort("outS"), self.addOutPort("outSW"),
                        self.addOutPort("outW"), self.addOutPort("outNW"), self.addOutPort("outTrans")]

    def intTransition(self):
        return self.state

    def outputFnc(self):
        return {self.outport: self.state.toCellState()}

    def timeAdvance(self):
        return INFINITY