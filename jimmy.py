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

from managers.BuildOrderManager import fill_build_queue, build_queue, remove_from_hopper
from managers.ArmyManager import train_unit
from managers.UpgradeManager import research_upgrade
from managers.CC_Manager import CC_Manager
from managers.ConstructionManager import ConstructionManager
from managers.MicroManager import MicroManager

from tools import make_build_order
from tools import draw_building_points
from tools.placement import depot_positions, building_positions
import tools.logger_levels as l

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

class Jimmy(BotAI):
    
    #following code from bot.py from smoothbrain bot as example
    def __init__(self):
        self.build_order = get_build_order(self,'16marinedrop-example')
        self.queue_size = 5
        self.step_index = 0
        self.upgrades = []                          # all of the upgrades from build order
        self.unit_types_qty = []                    # all of the units and counts we will build on build order load
        self.cc_managers = []                       # Instantiate all CC Class Managers in here
        self.worker_pool = 16                       # Total workers per CC
        self.workers_required = []                  # Total Workers from Build Order

        self.game_step: int = 2                      # 2 usually, 6 vs human
        self.debug = True

    async def on_start(self):
        ### Build Order ###
        build_order_cost(self, self.build_order)
        print(self.build_order)
        if self.debug: l.g.log("BUILD", self.build_order)
        for order in self.build_order:
            if order[3] == 'upgrade': self.upgrades.append(order[2])
        if self.debug: l.g.log("BUILD", f"Upgrades list: {self.upgrades}")

        ### Building Placement ###
        self.supply_depot_placement_list: Set[Point2] = depot_positions(self)
        self.tech_buildings_placement_list: Set[Point2] = building_positions(self)

        ### Army Manager ###
        self.unit_types_qty = update_unit_list(self.build_order, 'unit')
        if self.debug: l.g.log("ARMY", f"Army Units by Qty and Type from Build Order: {self.unit_types_qty}")

        ### Worker Count ###
        self.workers_required = update_unit_list(self.build_order, 'worker')
        if self.debug: l.g.log("CC", f"SCV Quantities: {self.workers_required}")
        ### Construction Manager ###
        self.construction_manager = ConstructionManager(self, self.build_order, self.supply_depot_placement_list, self.tech_buildings_placement_list)
        ### MicroManager ###
        self.micro_manager = MicroManager(self)

    async def on_step(self, iteration):
        ### CC_Manager ###
        cc_list = self.townhalls.ready
        for cc in cc_list:
            if not any(cc_manager.townhall.tag == cc.tag for cc_manager in self.cc_managers):
                cc_manager = CC_Manager(self, cc)
                self.cc_managers.append(cc_manager)

        for cc_manager in self.cc_managers:
            if cc_manager.townhall.tag not in self.townhalls.tags:
                self.cc_managers.remove(cc_manager)
            else:
                await cc_manager.manage_cc()

        ### BuildOrderManager ###
        if self.step_index < len(self.build_order):
            self.step_index = fill_build_queue(self.build_order, self.step_index, self.queue_size)
        await self.order_distributor(build_queue(self))

        ### MicroManager ###
        await self.micro_manager.controller()
        
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            #l.g.log("FATAL", "A user updated some information.")
            #logger.jimmy("This is without the extra logger Test")
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

        if self.debug:
            green = Point3((0, 255, 0))
            red = Point3((0, 0, 255))
            blue = Point3((255, 0, 0))
            if self.step_index < len(self.build_order): self.client.debug_text_screen(text=f"Next To Build: {str(self.build_order[self.step_index-1])}", pos=Point2((0, 0)), color=green, size=18)
            draw_building_points(self, self.supply_depot_placement_list, blue)
            draw_building_points(self, self.tech_buildings_placement_list, green)
    
    async def order_distributor(self, order):
        if order != None:

            if order[3] == 'structure' or order[3] == 'addon' or order[3] == 'commandcenter':
                    await self.construction_manager.supervisor(order, self.cc_managers)

            elif order[3] == 'unit':
                await train_unit(self, order[0])

            elif order[3] == 'worker':
                self.worker_pool += 1
                for manager in self.cc_managers:
                    if await manager.train_worker(self.worker_pool):
                        break

            elif order[3] == 'upgrade':
                await research_upgrade(self, order[0])
    
    #Following functions are called and happen asynchronously as an underlying interrupt function
    #from the BotAI - This will be something that happens outside of normal step function for the Bot
    async def on_building_construction_started(self, unit: Unit):
        """
        This function will always be called whenever a building has started to be built
        It sends the building type to the construction manager for the list
        if the building matches a building that was in the "waiting to validate" list
        removes it from the list
        
        :param is unit/building:
        """
        if self.debug:
            l.g.log("CONSTRUCTION",f"{unit.name} started building")
        self.construction_manager.construction_started(unit)
        remove_from_hopper(unit)

    async def on_building_construction_complete(self, unit: Unit):
        """
        This function will always be called whenever a building completes.
        
        :param is unit/building:
        """
        if self.debug:
            l.g.log("CONSTRUCTION",f"{unit.name} completed building")
        self.construction_manager.construction_complete(unit)
        self.micro_manager.on_building_construction_complete(unit)

    async def on_upgrade_complete(self, upgrade: UpgradeId):
        """
        Override this in your bot class. This function is called with the upgrade id of an upgrade that was not finished last step and is now.

        :param upgrade:
        """
        if self.debug:
            l.g.log("UPGRADE", f"Self Bot AI just told me I finished researching {upgrade}")
        remove_from_hopper(upgrade)

    async def on_unit_created(self, unit: Unit):
        """Override this in your bot class. This function is called when a unit is created.

        :param unit:"""
        if self.debug:
            l.g.log("ARMY", f"Self Bot AI just told me I finished creating a {unit}")
        remove_from_hopper(unit)

    async def on_enemy_unit_entered_vision(self, unit: Unit):
        """
        This function will always be called whenever a building completes.

        :param unit:
        """
        #await self.micro_manager.on_enemy_unit_entered_vision(unit)
    #End Override Functions for Bot Async Responses

    #end Bot Class
def build_order_cost(self: BotAI, build_order):
    for order in build_order:
        if order[3] == 'unit' or order[3] == 'worker' or order[3] == 'structure':
            order.append(self.calculate_cost(UnitTypeId[order[0]]))
        elif order[3] == 'addon' or order[3] == 'commandcenter':
            order.append(self.calculate_cost(AbilityId[order[1]]))
        elif order[3] == 'upgrade':
            order.append(self.calculate_cost(UpgradeId[order[2]]))
        else:
            order.append(Cost(0,0))

def get_build_order(self: BotAI, strategy):
    """The build order is a json file you must parse. It returns a list of items matching the json keys."""
    build_order = None
    build_order = make_build_order('strategies/' + strategy + '.json')
    if build_order is not None:
        return build_order
    else:
        return False

def update_unit_list(units, type):
    unit_list = []
    for unit in units:
        found = False
        if unit[3] == type:
            for item in unit_list:
                if item['name'] == unit[0]:
                    item['quantity'] += 1
                    found = True
                    break
            if not found:
                unit_list.append({'name': unit[0], 'quantity': 1})
    return unit_list

def main():
    run_game(
        maps.get("HardwireAIE"),
        [Bot(Race.Terran, Jimmy()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()