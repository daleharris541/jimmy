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
    structures = [structure for structure in self.structures if structure.is_ready]
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
    
    #print(f"Current Structures:  {sorted_current_structures}")
    #print(f"Expected Structures: {sorted_expected_structures}")
    return dict(sorted_current_structures), dict(sorted_expected_structures)

async def get_workers_constructing_building(self: BotAI):
    constructing_structures = {}
    worker_and_order = []
    constructing_workers = [(unit.tag, unit.orders[0].ability) for unit in self.units(UnitTypeId.SCV) if unit.is_constructing_scv and unit.order_target is not None]
    for obj in constructing_workers:
        tag = int(obj[0])
        name = str(obj[1]).split("=")[1].strip(")").strip("'")
        worker_and_order.append([tag, name])
        
    for structure in worker_and_order:
        uppercase_name = structure[1].upper()
        if uppercase_name in constructing_structures:
            constructing_structures[uppercase_name] += 1
        else:
            constructing_structures[uppercase_name] = 1

    #print(constructing_structures)
    return dict(constructing_structures)

async def combine_and_check(self: BotAI, build_order, buildstep):
    cur_and_const = {}
    current_structures, expected_structures = build_progress(self, build_order, buildstep)
    constructing_structures = await get_workers_constructing_building(self)

    #TODO:
    #compare expected_structures with cur_and_const

    for key in set(current_structures.keys()) | set(constructing_structures.keys()):
        value = current_structures.get(key, 0) + constructing_structures.get(key, 0)
        cur_and_const[key] = value if key in current_structures and key in constructing_structures else value

    print(cur_and_const)  #debug
    #return True

#construction order
async def build_unit(self : BotAI, unit_name, unitType):
    cc: Unit = self.townhalls(UnitTypeId.COMMANDCENTER).first
    await self.build(UnitTypeId[unit_name], near=cc.position.towards(self.game_info.map_center, 8)) #building placement logic missing



def getBuildOrder(self : BotAI, strategy):
    build_order = None
    build_order = makeBuildOrder('tools/strategies/' + strategy + '.json')
    #print("Imported " + len(build_order) + " items into build order")
    if build_order is not None:
        return build_order
    else:
        return False