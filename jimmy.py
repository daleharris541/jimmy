from typing import FrozenSet, Set, List, Tuple
from random import randrange

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units
from sc2.game_data import AbilityData, Cost
from loguru import logger

from tools import make_build_order
from managers.BuildOrderManager import fill_build_queue, build_queue
from managers.ArmyManager import train_unit
from managers.MicroManager import idle_workers
from managers.CC_Manager import CC_Manager
from managers.ConstructionManager import ConstructionManager

from tools.draw import draw_building_points
from tools.placement import calc_supply_depot_zones, calc_tech_building_zones

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

class Jimmy(BotAI):
    
    #following code from bot.py from smoothbrain bot as example
    def __init__(self):
        self.game_step: int = 2                      # 2 usually, 6 vs human
        self.built_army_units = []                   # this will have reapers, marines, dropships, etc
        self.cc_managers = []
        self.worker_pool = 12
        self.failed_steps = []
        self.build_order = get_build_order(self,'16marinedrop-example')
        self.step = 0
        self.queue_size = 5

        self.debug = True

    async def on_start(self):
        print("Game started")
        if len(self.build_order) != 0:
            print(self.build_order)

        build_order_cost(self, self.build_order)

        self.supply_depot_placement_list: Set[Point2] = calc_supply_depot_zones(self)
        self.tech_buildings_placement_list: Set[Point2] = calc_tech_building_zones(self, self.supply_depot_placement_list[2])

        self.construction_manager = ConstructionManager(self, self.build_order, self.supply_depot_placement_list, self.tech_buildings_placement_list)

    async def on_step(self, iteration):
        # Find all Command Centers
        cc_list = self.townhalls.ready
        # Create a new CC_Manager instance for each Command Center if it doesn't already exist
        for cc in cc_list:
            if not any(cc_manager.townhall.tag == cc.tag for cc_manager in self.cc_managers):
                cc_manager = CC_Manager(self, cc)
                self.cc_managers.append(cc_manager)

        # Call the manage_cc function for each CC_Manager instance
        for cc_manager in self.cc_managers:
            if cc_manager.townhall.tag not in self.townhalls.tags:
                self.cc_managers.remove(cc_manager)
            else:
                await cc_manager.manage_cc()

        #add supply depots if we are close on cap
        #if self.supply_left < 10 and self.already_pending(UnitTypeId.SUPPLYDEPOT) == 0:
            #self.build_order.append(['SUPPLYDEPOT',"10",'structure','150',Cost(100, 0)])

        #worker controller
        await idle_workers(self)

        #build order queue
        if self.step < len(self.build_order):
            self.step = fill_build_queue(self.build_order, self.step, self.queue_size)
        else:
            #if (self.all_own_units(UnitTypeId.MARINE).count) < 70:
            #send another army unit type to the queue
            #unit = self.built_army_units[randrange(1,len(self.built_army_units))]
                #select random type, add 5 more units
            #([name, id, type, supply])
            cost = self.calculate_cost(UnitTypeId.MARINE)
            logger.critical("Building 5 marines!")
            for i in range(1,5):
                self.build_order.append(['MARINE',"10",'unit','150',cost])
        
        result = await self.order_distributor(build_queue(self))
        if result is not None:
            self.failed_steps.append(result)
        print(f"Failed Steps: {self.failed_steps}")
        if self.debug:
            green = Point3((0, 255, 0))
            red = Point3((0, 0, 255))
            blue = Point3((255, 0, 0))
            self.client.debug_text_screen(text=str(self.build_order[0]), pos=Point2((0, 0)), color=green, size=18)
            # properly send each item in the build order for tech buildings
            draw_building_points(self, self.supply_depot_placement_list, green, labels="DEPOT")
            draw_building_points(self, self.tech_buildings_placement_list, green, labels="TechBuilding")
        
        # def on_enemy_unit_entered_vision(self, unit: Unit):
        # Raise Ramp Wall when enemy detected nearby
        # if get_distance(self,self.main_base_ramp.top_center,Unit.position) < 15:
        #     for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
        #         depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)
        # else:
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
    
    async def move_army(self, pos):
        #Gather all types of army units
        #send to location
        logger.warning("Moving Army units!")
        all_army_units = self.built_army_units
        for unit_types in all_army_units:
            boys = self.units(UnitTypeId[unit_types])
            boys.move(pos)
        
    async def on_enemy_unit_entered_vision(self, unit: Unit):
        """
        Override this in your bot class. This function is called when an enemy unit (unit or structure) entered vision (which was not visible last frame).

        :param unit:
        """
        # Send all units we've sent to be built to meet enemy entered vision
        logger.critical("Enemy has entered vision!")
        all_army_types = self.built_army_units
        if all_army_types:
            for unit_type in all_army_types:
                target, target_is_enemy_unit = self.select_target()
                attackers: Units = self.units(UnitTypeId[unit_type])
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
            for unit in self.workers:
                if not unit.is_attacking:
                    unit.attack(target)
        
    def select_target(self) -> Tuple[Point2, bool]:
        """Select an enemy target the units should attack."""
        targets: Units = self.enemy_structures
        if targets:
            return targets.random.position, True

        targets: Units = self.enemy_units
        if targets:
            return targets.random.position, True

        if (
            self.units
            and min(
                (
                    u.position.distance_to(self.enemy_start_locations[0])
                    for u in self.units
                )
            )
            < 10
        ):
            return self.enemy_start_locations[0].position, False
        
        return self.mineral_field.random.position, False

    
    
    async def on_building_construction_started(self, unit: Unit):
        logger.info(f"Construction of building {unit} started at {unit.position}.")

    async def on_building_construction_complete(self, unit: Unit):
        logger.info(f"Construction of building {unit} completed at {unit.position}.")
        logger.critical(unit)
        #Example: Construction of building Unit(name='CommandCenter', tag=4361814017) completed at (135.5, 167.5).
        if unit.name == 'CommandCenter':
            self.move_army(unit.position)
    
    async def order_distributor(self, order):
        if order != None:
            if order[2] == 'commandcenter' or order[2] == 'addon' or order[2] == 'structure':
                if order[0] == 'REFINERY':
                    self.cc_managers[0].build_refinery()
                elif order[0] == 'ORBITALCOMMAND':
                    self.cc_managers[0].upgrade_orbital_command()
                else:
                    await self.construction_manager.supervisor(order)
            elif order[2] == 'unit':
                if order[0] not in self.built_army_units:
                    self.built_army_units.append(order[0])
                await train_unit(self, order[0])
            elif order[2] == 'worker':
                self.worker_pool += 1
                for manager in self.cc_managers:
                    if await manager.train_worker(self.worker_pool):
                        break
            elif order[2] == 'upgrade' and order[0] == 'STIMPACK':
                await research_upgrade(self, order[0])
                print(f"Upgrade_Manager: {order}")
            elif order[2] == 'action':
                #await self.Upgrade_Manager.supervisor(order)
                print(f"We do nothing")

def build_order_cost(self: BotAI, build_order):
    for order in build_order:
        if order[2] == 'unit' or order[2] == 'worker' or order[2] == 'structure':
            order.append(self.calculate_cost(UnitTypeId[order[0]]))
        elif order[2] == 'addon' or order[2] == 'commandcenter':
            order.append(self.calculate_cost(AbilityId[order[1]]))
        elif order[2] == 'upgrade':
            order.append(self.calculate_cost(UpgradeId[order[0]]))
        else:
            order.append(Cost(0,0))

def get_build_order(self: BotAI, strategy):
    """
    The build order is a json file you must parse.
    It returns a list of items matching the json keys.
    """
    build_order = None
    build_order = make_build_order('strategies/' + strategy + '.json')
    if build_order is not None:
        return build_order
    else:
        return False

def main():
    run_game(
        maps.get("HardwireAIE"),
        [Bot(Race.Terran, Jimmy()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()