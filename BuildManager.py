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
       
def build_progress(self: BotAI, build_order, buildstep):
    structures = self.structures
    current_structures = {}
    for unit in structures:
        uppercase_name = unit.name.upper()
        if uppercase_name in current_structures:
            current_structures[uppercase_name] += 1
        else:
            current_structures[uppercase_name] = 1
    sorted_current_structures = sorted(current_structures.items())

    expected_structures = {}
    for i in range(buildstep):
        if build_order[i][0] in expected_structures:
            expected_structures[build_order[i][0]] += 1
        else:
            expected_structures[build_order[i][0]] = 1
    sorted_expected_structures = sorted(expected_structures.items())
    
    print(f"Current Structures: {sorted_current_structures}")
    print(f"Expected Structures: {sorted_expected_structures}")  #debug
    #return sorted_structure_counts

#check prerequisites(minerals/gas, under construction, already existing)
async def build_next(self : BotAI, buildrequest):
    unit_name, unitId, unitType, supplyrequired, gametime, frame = buildrequest
    if self.supply_used < supplyrequired:
        print(f"Cannot build, current supply: {self.supply_used}")
        return False
    
    if self.can_afford(UnitTypeId[unit_name]) and self.tech_requirement_progress(UnitTypeId[unit_name]) == 1:
        print(self.tech_requirement_progress(UnitTypeId[unit_name]))
        await build_unit(self, unit_name)
        return True

#construction order
async def build_unit(self : BotAI, unit_name):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    await self.build(UnitTypeId[unit_name], near=cc.position.towards(self.game_info.map_center, 8)) #building placement logic missing

def getBuildOrder(self : BotAI, strategy):
    build_order = None
    build_order = makeBuildOrder('tools/' + strategy + '.json')
    #print("Imported " + len(build_order) + " items into build order")
    if build_order is not None:
        return build_order
    else:
        return False