from typing import FrozenSet, Set, List, Tuple
from random import randrange
from loguru import logger

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

from managers.BuildOrderManager import fill_build_queue, build_queue
from managers.ArmyManager import train_unit
from managers.UpgradeManager import research_upgrade
from managers.CC_Manager import CC_Manager
from managers.ConstructionManager import ConstructionManager
from managers.MicroManager import MicroManager

from tools import make_build_order
from tools import draw_building_points
from tools.placement import depot_positions, building_positions

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

class Jimmy(BotAI):
    
    #following code from bot.py from smoothbrain bot as example
    def __init__(self):
        self.build_order = get_build_order(self,'16marinedrop-example')
        self.queue_size = 5
        self.step = 0

        self.cc_managers = []
        self.worker_pool = 12

        self.game_step: int = 2                      # 2 usually, 6 vs human
        self.debug = True

    async def on_start(self):
        build_order_cost(self, self.build_order)
        print(self.build_order)

        self.supply_depot_placement_list: Set[Point2] = depot_positions(self)
        self.tech_buildings_placement_list: Set[Point2] = building_positions(self)

        ### ConstructionManager ###
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

        ### MicroManager ###
        await self.micro_manager.controller()

        ### BuildOrderManager ###
        if self.step < len(self.build_order):
            self.step = fill_build_queue(self.build_order, self.step, self.queue_size)

        await self.order_distributor(build_queue(self))
        
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)

        if self.debug:
            green = Point3((0, 255, 0))
            red = Point3((0, 0, 255))
            blue = Point3((255, 0, 0))
            self.client.debug_text_screen(text=str(self.build_order[0]), pos=Point2((0, 0)), color=green, size=18)
            draw_building_points(self, self.supply_depot_placement_list, blue, labels="DEPOT")
            draw_building_points(self, self.tech_buildings_placement_list, green, labels="TechBuilding")
    
    async def order_distributor(self, order):
        if order != None:

            if order[2] == 'structure' or order[2] == 'addon':
                    await self.construction_manager.supervisor(order, self.cc_managers)

            elif order[2] == 'unit':
                await train_unit(self, order[0])

            elif order[2] == 'worker':
                self.worker_pool += 1
                for manager in self.cc_managers:
                    if await manager.train_worker(self.worker_pool):
                        break

            elif order[2] == 'upgrade':
                await research_upgrade(self, order[0])

def build_order_cost(self: BotAI, build_order):
    for order in build_order:
        if order[2] == 'unit' or order[2] == 'worker' or order[2] == 'structure':
            order.append(self.calculate_cost(UnitTypeId[order[0]]))
        elif order[2] == 'addon':
            order.append(self.calculate_cost(AbilityId[order[1]]))
        elif order[2] == 'upgrade':
            order.append(self.calculate_cost(UpgradeId[order[0]]))
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

def main():
    run_game(
        maps.get("HardwireAIE"),
        [Bot(Race.Terran, Jimmy()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()