from typing import FrozenSet, Set

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

from BuildOrderManager import fill_build_queue, build_queue
from tools import make_build_order
from managers.CC_Manager import CC_Manager
from managers.ConstructionManager import ConstructionManager
from managers.ArmyManager import train_unit
from managers.MicroManager import idle_workers

from debug import (
    label_unit,
    draw_building_points,
    draw_expansions,
    get_direction_vector,
    get_distance,
    calc_supply_depot_zones,
    calc_tech_building_zones,
)

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

class Jimmy(BotAI):
    
    #following code from bot.py from smoothbrain bot as example
    def __init__(self):
        self.game_step: int = 2                      # 2 usually, 6 vs human

        self.cc_managers = []
        self.worker_pool = 12

        self.build_order = get_build_order(self,'16marinedrop-example')
        self.step = 0
        self.queue_size = 5

        self.debug = False

    async def on_start(self):
        print("Game started")
        if len(self.build_order) != 0:
            print(self.build_order)

        build_order_cost(self, self.build_order)

        self.building_list = [step for step in self.build_order if step[2] == 'structure']
        self.supply_depot_placement_list: Set[Point2] = calc_supply_depot_zones(self)
        self.tech_buildings_placement_list: Set[Point2] = calc_tech_building_zones(self, self.supply_depot_placement_list[2], self.building_list)

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
                await cc_manager.manage_cc(self.worker_pool)
        #grab any workers idle
        await idle_workers(self)
        #await self.construction_manager.supervisor('test')
        if self.step < len(self.build_order):
            self.step = fill_build_queue(self.build_order, self.step, self.queue_size)

        await self.order_distributor(build_queue(self))
        if self.debug:
            green = Point3((0, 255, 0))
            red = Point3((0, 0, 255))
            blue = Point3((255, 0, 0))
            self.client.debug_text_screen(text=str(self.build_order[0]), pos=Point2((0, 0)), color=green, size=18)
            # properly send each item in the build order for tech buildings
            draw_building_points(self, self.supply_depot_placement_list, green, labels="DEPOT")
            draw_building_points(self, self.tech_buildings_placement_list, green, self.building_list)
        
        # def on_enemy_unit_entered_vision(self, unit: Unit):
        # Raise Ramp Wall when enemy detected nearby
        # if get_distance(self,self.main_base_ramp.top_center,Unit.position) < 15:
        #     for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
        #         depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)
        # else:
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
            depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)


    async def order_distributor(self, order):
        if order != None:
            if order[2] == 'structure':
                if order[0] == 'REFINERY':
                    self.cc_managers[0].build_refinery()
                elif order[0] == 'ORBITALCOMMAND':
                    self.cc_managers[0].upgrade_orbital_command()
                else:
                    await self.construction_manager.supervisor(order)
            elif order[2] == 'unit':
                await train_unit(self, order[0])
            elif order[2] == 'worker':
                #worker_pool += 1
                await self.cc_managers[0].train_worker(70)
            elif order[2] == 'upgrade':
                #await self.Upgrade_Manager.supervisor(order)
                print(f"Upgrade_Manager: {order}")
            elif order[2] == 'action':
                #await self.Upgrade_Manager.supervisor(order)
                print(f"We do nothing")

def build_order_cost(self: BotAI, build_order):
    for order in build_order:
        if order[2] == 'structure' or order[2] == 'unit' or order[2] == 'worker':
            order.append(self.calculate_cost(UnitTypeId[order[0]]))
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
        [Bot(Race.Terran, Jimmy()), Computer(Race.Terran, Difficulty.Easy)],
        realtime=True,
    )

if __name__ == "__main__":
    main()