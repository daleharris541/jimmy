from tools import makeBuildOrder
from sc2.unit import Unit
from sc2.units import Units

#this is absolutely trash and only for debugging

def getBuildOrder():
    return makeBuildOrder('tools/test.json')

def printOrder():
    order = getBuildOrder()
    for row in order:
        print(row)

printOrder()