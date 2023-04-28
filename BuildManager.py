from tools import makeBuildOrder

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

#This class should do the following.
#   -Execute Build order.
#   -Track Build order progress
#   -Building placement.
#   -Rebuild destroyed structures

async def execute_build_queue(self):
    queue = [["SUPPLYDEPOT", "build", 15, 1], ["BARRACKS", "build", 15, 1]]
    for active in queue:
        unit_name, action, atSupply, quantity = active

        if self.check_prerequisites(unit_name, quantity):
            await self.build_unit(unit_name)
        else:
            continue
        
        print(queue[0])
        queue.remove(active) #not working

#check prerequisites(minerals/gas, under construction, already existing)
def check_prerequisites(self : BotAI, unit_name):
    if self.can_afford(UnitTypeId[unit_name]):
        return True
    else:
        return False  
    
def build_progress(self):
    structures = self.bot.structures
    structure_counts = {}

    for unit in structures:
        if unit.name in structure_counts:
            structure_counts[unit.name] += 1
        else:
            structure_counts[unit.name] = 1

    sorted_structure_counts = sorted(structure_counts.items())

    print(sorted_structure_counts)  #debug
    #return sorted_structure_counts 

async def build_next(self : BotAI, buildrequest):
    #0 unit name, 1 unit id, 2 type of unit, 3 action type, 4 quantity, 5 supply, 6 time, 7 frame
    buildinfo = str(buildrequest).split(", ")
    supplyrequired = int(buildinfo[5])

    if self.supply_used < supplyrequired:
        print("Cannot build, current supply: " + str(self.supply_used))
        return False
    
    unit_name = (str(buildinfo[0]).strip("[")).strip("'").upper
    #print("checking to see if we can build " + unit_name)
    if check_prerequisites(self, unit_name) == False:
        return False
    else:
        unit_type = str(buildinfo[2])
        if unit_type.strip("'") == "structure":
            build_unit(self, unit_name)

#build request execution
async def build_unit(self : BotAI, unit_name):
    CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
    cc: Unit = CCs.first
    await self.build(UnitTypeId[unit_name], near=cc.position.towards(self.game_info.map_center, 10)) #building placement logic missing
    return True

def getBuildOrder(self : BotAI, strategy):
    build_order = None
    build_order = makeBuildOrder('tools/' + strategy + '.json')
    #print("Imported " + len(build_order) + " items into build order")
    if build_order is not None:
        return build_order
    else:
        return False