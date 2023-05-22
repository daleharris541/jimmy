from tools import closest_point
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
from typing import FrozenSet, Set

class ConstructionManager:

    def __init__(self, bot: BotAI, build_order, depot_positions: Set[Point2], building_positions: Set[Point2]):
        self.bot = bot
        self.build_order = build_order
        self.depot_positions = depot_positions
        self.building_positions = building_positions
        self.building_list = []
        self.test = 20

    async def supervisor(self, order, cc_managers: list):
        ### UPDATE VARIABLES ###
        self.building_list.append(order)

        ### BEHAVIOR ###
        if ("TECHLAB" or "REACTOR") in order[0]:
            if (await self.build_addon(order[1])):
                return order
            
        elif order[0] == 'REFINERY':
            cc_managers[0].build_refinery()

        elif order[0] == 'ORBITALCOMMAND':
            cc_managers[0].upgrade_orbital_command()

        elif order[0] == 'COMMANDCENTER':
            await self.build_expansion()    #under threat check

        elif order[0] == 'SUPPLYDEPOT':
            await self.build_structure(order[0], self.depot_positions[0])
            self.depot_positions.pop(0)
        else:
            await self.build_structure(order[0], self.building_positions[0])
            self.building_positions.pop(0)

    #construction order
    async def build_structure(self, unit_name, pos=None):
        """
        This function builds various structures based on build order
        You must send a position 
        It returns True/False to identify whether it executed or not
        This allows multiple attempts to build without skipping
        """
        print(f"building {unit_name} at {pos}")
        if (await self.bot.build(UnitTypeId[unit_name], pos)):
            return True

    async def build_addon(self, unit_name):
        """
        Function to properly assign the buildings to which is being assigned
        to build the addon since SCVs do not build it
        It returns True/False to identify whether it executed or not
        """
        buildingType = unit_name.split("_")[2]
        for building in self.bot.structures(UnitTypeId[buildingType]).ready.idle:
            if not building.has_add_on:
                if building(AbilityId[unit_name]):
                    print("Construction Manager: I built an addon!")
                    return True
                else:
                    return False
                
    async def build_expansion(self):
        """This function looks for the neares expansion location."""
        used_positions = []
        all_positions = self.bot.expansion_locations_list
        available_positions = []

        for townhall in self.bot.townhalls:
            used_positions.append(townhall.position)
        
        for pos in all_positions:
            if pos not in used_positions:
                available_positions.append(pos)

        pos = closest_point(self.bot.start_location, available_positions)
        
        #as we expand, move army nearby to cover expansion
        await self.bot.build(UnitTypeId.COMMANDCENTER, pos)

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