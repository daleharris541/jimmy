from tools import makeBuildOrder

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

#This class should do the following.
#   -Execute Build order.           -partially done
#   -Track Build order progress     -done
#   -Building placement.            -not started
#   -Rebuild destroyed structures   -not started

#Current bugs 
#   -cant build refinery because of fixed location
#   -json build order not compatible UnitTypeId
#   -engineeringbay coud not be build coud not find out why
#   -last objekt in BuildOrder get build constantly (coud be fixed with quantity)
       
def build_progress(self: BotAI):
    structures = self.structures
    structure_counts = {}

    for unit in structures:
        if unit.name in structure_counts:
            structure_counts[unit.name] += 1
        else:
            structure_counts[unit.name] = 1

    sorted_structure_counts = sorted(structure_counts.items())

    #print(sorted_structure_counts)  #debug
    return sorted_structure_counts

#check prerequisites(minerals/gas, under construction, already existing)
async def build_next(self : BotAI, buildrequest):
    unit_name, unitId, unitType, action, quantity, supplyrequired, time, frame = buildrequest

    if self.supply_used < supplyrequired:
        print(f"Cannot build, current supply: {self.supply_used}")
        return False
    
    if self.can_afford(UnitTypeId[unit_name]):
        await build_unit(self, unit_name)
        return True

#construction order
async def build_unit(self : BotAI, unit_name):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    await self.build(UnitTypeId[unit_name], near=cc.position.towards(self.game_info.map_center, 10)) #building placement logic missing

def getBuildOrder(self : BotAI, strategy):
    build_order = None
    build_order = makeBuildOrder('tools/' + strategy + '.json')
    #print("Imported " + len(build_order) + " items into build order")
    if build_order is not None:
        return build_order
    else:
        return False