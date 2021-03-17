import sys
import random
schedulers = ["setSchedulerSortedList", "setSchedulerActivityHeap", "setSchedulerMinimalList", "setSchedulerHeapSet"]
sys.path.append("../../src/")
sizes = range(10, 71, 1)
from pypdevs.simulator import Simulator
iters = 1
import time

def runFunc(scheduler):
    f = open("../seq_activity_firespread/" + str(scheduler), 'w')
    for size in sizes:
        from model import FireSpread
        total = 0.0
        for _ in range(iters):
            model = FireSpread(size, size)
            sim = Simulator(model)
            sim.setMessageCopy('none')
            getattr(sim, scheduler)()
            sim.setTerminationTime(150)
            start = time.time()
            sim.setCell(50, 50, cell_file="celltrace-%05d", multifile=True)
            sim.simulate()
            total += (time.time() - start)
        # Take the square of size, as we have this many cells instead of only 'size' cells
        f.write("%s %s\n" % (size*size, total/iters))
        print("%s -- %s %s" % (scheduler, size*size, total/iters))
    f.close()

map(runFunc, schedulers)
"""
from multiprocessing import Pool
p = Pool(4)
p.map(runFunc, schedulers)
"""
