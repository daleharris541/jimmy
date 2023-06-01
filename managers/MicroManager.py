from typing import Tuple

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

import tools.logger_levels as l

class MicroManager():

    def __init__(self, bot: BotAI):
        self.bot = bot
        self.built_army_units = []                   # this will have reapers, marines, dropships, etc

    async def controller(self):
        self.idle_workers()

    def idle_workers(self):
        if len(self.bot.townhalls) > 0 and len(self.bot.workers) > 0:
            workers = [worker for worker in self.bot.workers if worker.is_idle]
            for worker in workers:
                townhall = self.bot.townhalls.ready.closest_to(worker)
                mineral = self.bot.mineral_field.closest_to(townhall)
                worker.gather(mineral)

    def move_army(self, pos):
        #Gather all types of army units
        #send to location
        units = self.built_army_units
        for unit_types in units:
            #TODO #33 Include logic to create subgroups of unit types (bio, air, and more granular: marines, bcs, etc)
            #TODO #34 Include logic to ensure we aren't grabbing unit types that are empty
            boys = self.bot.units(UnitTypeId[unit_types])
            boys.move(pos)
        
    def on_enemy_unit_entered_vision(self, unit: Unit):
        """
        This function is called when an enemy unit (unit or structure) entered vision (which was not visible last frame).

        :param unit:
        """
        # Send all units we've sent to be built to meet enemy entered vision
    
        all_army_types = self.built_army_units
        if all_army_types:
            for unit_type in all_army_types:
                target, target_is_enemy_unit = self.select_target()
                attackers: Units = self.bot.units(UnitTypeId[unit_type])
                unit: Unit
                for unit in attackers:
                    # Order the unit to attack-move the target
                    if target_is_enemy_unit and (unit.is_idle or unit.is_moving):
                        unit.attack(target)
                    # Order the units to move to the target, and once the select_target returns an attack-target, change it to attack-move
                    elif unit.is_idle:
                        unit.move(target)
        else:
            #pull the boys
            for unit in self.bot.workers:
                if not unit.is_attacking:
                    unit.attack(target)
        
    def select_target(self) -> Tuple[Point2, bool]:
        """Select an enemy target the units should attack."""
        targets: Units = self.bot.enemy_structures
        if targets:
            return targets.random.position, True

        targets: Units = self.bot.enemy_units
        if targets:
            return targets.random.position, True

        if (self.bot.units and min((u.position.distance_to(self.bot.enemy_start_locations[0]) for u in self.bot.units))< 10):
            return self.bot.enemy_start_locations[0].position, False
        
        return self.bot.mineral_field.random.position, False

    def on_building_construction_complete(self, unit: Unit):
        #print(f"MM: Building Construction Complete: {unit}")
        #print(f"Building Construction Complete: {unit}")
        #if unit.name == 'CommandCenter':
            #self.move_army(unit.position)
        pass