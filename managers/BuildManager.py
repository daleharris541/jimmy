from tools import makeBuildOrder

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

#This class should do the following.
#   -Execute Build order.           -partially done
#   -Track Build order progress     -partially done
#   -Building placement.            -not started
#   -Rebuild destroyed structures   -not started
 
async def get_build_progress(self: BotAI):
    structures = [structure for structure in self.structures if structure.is_ready]
    current_structures = {}
    for unit in structures:
        uppercase_name = unit.name.upper()
        if uppercase_name in current_structures:
            current_structures[uppercase_name] += 1
        else:
            current_structures[uppercase_name] = 1
    sorted_current_structures = sorted(current_structures.items())

    return dict(sorted_current_structures)

async def get_build_order_progress(self: BotAI,  build_order, buildstep):
    expected_structures = {}
    for i in range(buildstep):
        if build_order[i][2] == 'structure':
            if build_order[i][0] in expected_structures:
                expected_structures[build_order[i][0]] += 1
            else:
                expected_structures[build_order[i][0]] = 1
    sorted_expected_structures = sorted(expected_structures.items())

    return dict(sorted_expected_structures)

async def get_constructing_orders(self: BotAI):
    constructing_structures = {}
    worker_and_order = []   #This list contains the worker tag and the build order and is currently not used
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

    return dict(constructing_structures)

async def combine_dicts(self: BotAI):
    combined_dict = {}
    current_structures = await get_build_progress(self)
    constructing_structures = await get_constructing_orders(self)

    for key in set(current_structures.keys()) | set(constructing_structures.keys()):
        value = current_structures.get(key, 0) + constructing_structures.get(key, 0)
        combined_dict[key] = value if key in current_structures and key in constructing_structures else value

    sorted_combined_dict = sorted(combined_dict.items())

    return dict(sorted_combined_dict)

async def compare_dicts(self: BotAI, build_order, buildstep):
    current_structures = await combine_dicts(self)
    expected_structures = await get_build_order_progress(self, build_order, buildstep)

    common_keys = set(current_structures.keys()).intersection(expected_structures.keys())

    for key in common_keys:
        if current_structures[key] != expected_structures[key]:
            print(f"FALSE: {current_structures} and {expected_structures} not matching")

    #TODO Find out why some checks fail (ingame list faster updated then build order)

    #print(f"Ingame: {current_structures} | BuildOrder: {expected_structures}")
    pass


#construction order
async def build_structure(self : BotAI, unit_name):
    #cc: Unit = self.townhalls(UnitTypeId.COMMANDCENTER).first
    cc : Unit = self.townhalls.first
    #TODO #8 Reactor doesn't work - may break everything
    if unit_name == 'BARRACKSREACTOR':
        print("**********")
        print("I have a barracks reactor to build!")
        print("**********")
        for barrack in self.structures(UnitTypeId.BARRACKS).ready.idle:
            print("I have an idle barracks!")
            if not barrack.has_add_on and barrack.add_on_position:
                print("I have a barracks without an addon")
                if barrack(AbilityId.BUILD_REACTOR_BARRACKS):
                    return True
            else:
                return False
        return False
    if unit_name == 'BARRACKSTECHLAB':
        print("**********")
        print("I have a barracks tech lab to build!")
        print("**********")
        for barrack in self.structures(UnitTypeId.BARRACKS).ready.idle:
            print("I have an idle barracks!")
            if not barrack.has_add_on and barrack.add_on_position:
                print("I have a barracks without an addon")
                if barrack(AbilityId.BUILD_TECHLAB_BARRACKS):
                    return True
            else:
                return False
        return False
    # if unit_name == 'BARRACKSTECHLABRESEARCH_STIMPACK':
    #     if self.structures(UnitTypeId.TECHLAB):
    #         for techlab in self.structures(UnitTypeId.TECHLAB).ready.idle:
    #             if techlab(AbilityId.BARRACKSTECHLABRESEARCH_STIMPACK):
    #                 return True
    #     else:
    #         print("No tech lab, so skipping Stimpack")
    #         return True
    else:
        if unit_name == "SUPPLYDEPOT":
            await self.build(UnitTypeId[unit_name], near=cc.position.towards(self.game_info.map_center, 5)) #building placement logic missing
        else:
            await self.build(UnitTypeId[unit_name], near=cc.position.towards(self.game_info.map_center, 12)) #building placement logic missing

def get_build_order(self : BotAI, strategy):
    """
    The build order is a json file you must parse.
    It returns a list of items matching the json keys.
    """
    build_order = None
    build_order = makeBuildOrder('strategies/' + strategy + '.json')
    if build_order is not None:
        return build_order
    else:
        return False