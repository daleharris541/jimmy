from tools import makeBuildOrder
from sc2.unit import Unit
from sc2.units import Units

#This class should do the following.
#   -Execute Build order.
#   -Track Build order progress
#   -Building placement.
#   -Rebuild destroyed structures
#   -Send workers back to Comand Center / Mining


class BuildManager:
    def getBuildOrder():
        return makeBuildOrder('tools/test.json')

    order = getBuildOrder()
    for row in order:
        print(row)