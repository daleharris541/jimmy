from tools import closest_point
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.position import Point2, Point3
from typing import FrozenSet, Set

class ConstructionManager:

    def __init__(self, bot: BotAI, build_order, depot_positions: Set[Point2], building_positions: Set[Point2]):
        self.bot = bot
        self.build_order = build_order
        self.depot_positions = depot_positions
        self.building_positions = building_positions
        self.building_list = []

    async def supervisor(self, order, cc_managers: list):
        ### UPDATE VARIABLES ###
        self.building_list.append(order)

        ### BEHAVIOR ###
        if ("TECHLAB" or "REACTOR") in order[0]:
            if (await self.build_addon(order[1])):
                return order
            
        elif order[0] == 'REFINERY':
            for manager in cc_managers:
                if manager.build_refinery():
                    break

        elif order[0] == 'ORBITALCOMMAND':
            for manager in cc_managers:
                if manager.upgrade_orbital_command():
                    break

        elif order[0] == 'COMMANDCENTER':
            await self.build_expansion()    #under threat check

        elif order[0] == 'SUPPLYDEPOT':
            await self.build_structure(order[0], self.depot_positions[0])
            self.depot_positions.pop(0)
        else:
            await self.build_structure(order[0], self.building_positions[0])
            self.building_positions.pop(0)

    async def build_structure(self, unit_name, pos=None):
        """
        This function builds various structures based on build order
        You must send a position 
        It returns True/False to identify whether it executed or not
        This allows multiple attempts to build without skipping
        """
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


    # works for addons
    async def on_building_construction_started(self, unit: Unit):
        pass

    async def on_building_construction_complete(self, unit: Unit):
        pass