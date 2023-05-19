from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units
from typing import FrozenSet, Set

class ConstructionManager:

    def __init__(self, bot: BotAI, build_order, depot_positions, building_positions):
        self.bot = bot
        self.build_order = build_order
        self.depot_positions = depot_positions
        self.building_positions = building_positions
        self.building_list = []
        self.test = 20

    async def supervisor(self, order):
        ### UPDATE VARIABLES ###
        self.building_list.append(order)
        ### BEHAVIOR ###
        if order[0] == 'REFINERY' or order[0] == 'ORBITALCOMMAND':
            pass
        elif order[0] == 'SUPPLYDEPOT':
            await self.build_structure(order[0], self.depot_positions)
        else:
            await self.build_structure(order[0], self.building_positions)

    #construction order
    async def build_structure(self: BotAI, unit_name, pos=None):
        """
        This function builds various structures based on build order
        You must send a position 
        It returns True/False to identify whether it executed or not
        This allows multiple attempts to build without skipping
        """
        cc : Unit = self.townhalls.first
        if pos is None:
            #We didn't pass a position, so pick one since the lists are empty
            pos = self.find_placement(near = cc.position.towards(self.game_info.map_center, 15))
        #first two supply depots will be built on ramp, the rest on our planned layout
        if unit_name == "SUPPLYDEPOT":
            worker =  self.select_build_worker(pos)
            if (await self.build(UnitTypeId[unit_name], pos,build_worker=worker)):
                return True
            else:
                return False
        elif unit_name == "BARRACKS": #build all buildings (except first barracks) in a different area lined up top to bottom
            if self.structures(UnitTypeId.BARRACKS).amount + self.already_pending(UnitTypeId.BARRACKS) == 0:
                pos = self.main_base_ramp.barracks_correct_placement.as_Point2D
            if (await self.build(UnitTypeId[unit_name], pos)):
                return True
            else:
                return False
        else:
            if (await self.build(UnitTypeId[unit_name],near = cc.position.towards(self.game_info.map_center, 15))):
                return True
            else:
                return False

    async def build_addon(self, unit_name):
        """
        Function to properly assign the buildings to which is being assigned
        to build the addon since SCVs do not build it
        It returns True/False to identify whether it executed or not
        """
        abilityID = ''
        if unit_name[:8] == 'BARRACKS':
            if unit_name[-7:] == 'TECHLAB':
                abilityID = 'BUILD_TECHLAB_BARRACKS'
            elif unit_name[-7:] == 'REACTOR':
                abilityID = 'BUILD_REACTOR_BARRACKS'

        elif unit_name[:7] == 'FACTORY':
            if unit_name[-7:] == 'REACTOR':
                abilityID = "BUILD_REACTOR_FACTORY"
            elif unit_name[-7:] == 'TECHLAB':
                abilityID = "BUILD_TECHLAB_FACTORY"

        elif unit_name[:8] == 'STARPORT':
            if unit_name[-7:] == 'REACTOR':
                abilityID = "BUILD_REACTOR_STARPORT"
            elif unit_name[-7:] == 'TECHLAB':
                abilityID = "BUILD_TECHLAB_STARPORT"

        buildingType = abilityID.split("_")[2]
        for building in self.bot.structures(UnitTypeId[buildingType]).ready.idle:
            if not building.has_add_on and building.add_on_position:
                if building(AbilityId[abilityID]):
                    return True
                else:
                    return False

    def get_build_progress(self):
        structures = [structure for structure in self.bot.structures if structure.is_ready]
        current_structures = {}
        for unit in structures:
            uppercase_name = unit.name.upper()
            if uppercase_name in current_structures:
                current_structures[uppercase_name] += 1
            else:
                current_structures[uppercase_name] = 1
        sorted_current_structures = sorted(current_structures.items())

        return dict(sorted_current_structures)

    def get_build_order_progress(self, build_order, buildstep):
        expected_structures = {}
        for i in range(buildstep):
            if build_order[i][2] == 'structure':
                if build_order[i][0] in expected_structures:
                    expected_structures[build_order[i][0]] += 1
                else:
                    expected_structures[build_order[i][0]] = 1
        sorted_expected_structures = sorted(expected_structures.items())

        return dict(sorted_expected_structures)

    def get_constructing_orders(self):
        constructing_structures = {}
        worker_and_order = []   #This list contains the worker tag and the build order and is currently not used
        constructing_workers = [(unit.tag, unit.orders[0].ability) for unit in self.bot.units(UnitTypeId.SCV) if unit.is_constructing_scv and unit.order_target is not None]
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

    def combine_dicts(self):
        combined_dict = {}
        current_structures = self.get_build_progress(self)
        constructing_structures = self.get_constructing_orders(self)

        for key in set(current_structures.keys()) | set(constructing_structures.keys()):
            value = current_structures.get(key, 0) + constructing_structures.get(key, 0)
            combined_dict[key] = value if key in current_structures and key in constructing_structures else value

        sorted_combined_dict = sorted(combined_dict.items())

        return dict(sorted_combined_dict)

    def compare_dicts(self, build_order, buildstep):
        current_structures = self.combine_dicts()
        expected_structures = self.get_build_order_progress(build_order, buildstep)

        common_keys = set(current_structures.keys()).intersection(expected_structures.keys())

        for key in common_keys:
            if current_structures[key] != expected_structures[key]:
                print(f"FALSE: {current_structures} and {expected_structures} not matching")

        #TODO Find out why some checks fail (ingame list faster updated then build order)
        
        #print(f"Ingame: {current_structures} | BuildOrder: {expected_structures}")
        pass