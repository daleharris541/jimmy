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
from sc2.unit import Unit, RallyTarget
from sc2.units import Units
from sc2.game_data import AbilityData, Cost

from managers.BuildOrderManager import fill_build_queue, build_queue
from managers.ArmyManager import train_unit
from managers.UpgradeManager import research_upgrade
from managers.CC_Manager import CC_Manager
from managers.ConstructionManager import ConstructionManager
from managers.MicroManager import MicroManager
from managers.StructureClass import Structure

from tools import make_build_order
from tools import draw_building_points
from tools.placement import depot_positions, building_positions
import tools.logger_levels as l

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

class Jimmy(BotAI):
    
    def __init__(self):
        self.build_order = get_build_order(self,'16marinedrop-example')
        self.queue_size = 5
        self.step_index = 0
        self.upgrades = []                          # all of the upgrades from build order
        self.unit_types_qty = []                    # all of the units and counts we will build on build order load
        self.cc_managers = []                       # Instantiate all CC Class Managers in here
        self.worker_pool = 16                       # Total workers per CC
        self.workers_required = []                  # Total Workers from Build Order
        self.structure_tracker = []                 # List of all structures built from the class

        self.game_step: int = 2                      # 2 usually, 6 vs human
        self.debug = False                           #set to True to see debug logs

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
        #self.construction_manager = ConstructionManager(self, self.build_order, self.supply_depot_placement_list, self.tech_buildings_placement_list)

        ### Structure Class ###
        cc_list = self.townhalls.ready #should only be starting CC
        for cc in cc_list:
            Structure(self,"COMMANDCENTER", cc.position,True,cc)

        ### MicroManager ###
        self.micro_manager = MicroManager(self)

    async def on_step(self, iteration):
        ### CC_Manager ###
        cc_list = self.townhalls.ready
        for cc in cc_list:
            if not any(cc_manager.townhall.tag == cc.tag for cc_manager in self.cc_managers):
                self.cc_managers.append(CC_Manager(self, cc))

        for cc_manager in self.cc_managers:
            if cc_manager.townhall.tag not in self.townhalls.tags:
                self.cc_managers.remove(cc_manager)
            else:
                await cc_manager.manage_cc()

        ### Structure_Class ###
        
        #Note: We should only call on structures that haven't been built yet
        #so if we get a ton of buildings, we don't always have to keep pinging them
        for structure in self.structure_tracker:
            await structure.manage_structure()
        for incomplete_structure in self.structures_without_construction_SCVs:
            for structure in self.structure_tracker:
                if incomplete_structure.tag == structure.tag:
                    structure.scv_destroyed_during_build()
        
        ### BuildOrderManager ###
        if self.step_index < len(self.build_order):
            self.step_index = fill_build_queue(self.build_order, self.step_index, self.queue_size)
        await self.order_distributor(build_queue(self))

        ### MicroManager ###
        await self.micro_manager.controller()
        
        for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
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

            if order[3] == 'addon' or order[3] == 'commandcenter':
                    await self.construction_manager.supervisor(order, self.cc_managers)

            elif order[3] == 'structure':
                if order[0] == 'SUPPLYDEPOT':
                    print(f"Attempting to build supply depot at {self.supply_depot_placement_list[0]}")
                    self.structure_tracker.append(Structure(self,order[0], self.supply_depot_placement_list[0]))
                    self.supply_depot_placement_list.pop(0)
                else:
                    self.structure_tracker.append(Structure(self,order[0], self.tech_buildings_placement_list[0]))
                    self.tech_buildings_placement_list.pop(0)

            elif order[3] == 'unit':
                await train_unit(self, order[0])

            elif order[3] == 'worker':
                self.worker_pool += 1
                for manager in self.cc_managers:
                    if await manager.train_worker(self.worker_pool):
                        break

            elif order[3] == 'upgrade':
                await research_upgrade(self, order[2])
    
    #Following functions are called and happen asynchronously as an underlying interrupt function
    #from the BotAI - This will be something that happens outside of normal step function for the Bot
    async def on_building_construction_started(self, unit: Unit):
        """
        This function will always be called whenever a building has started to be built
        It finds the appropriate matching structure class object and sends the update
        Based on testing, this may be called even when it doesn't happen - something to validate
        
        :param is unit/building:
        """
        if self.debug:
            l.g.log("CONSTRUCTION",f"{unit.name} started building")
        
        #once construction on a building has started, then assign the tag to the structure class
        for structure in self.structure_tracker:
            if structure.tag == None:
                print(unit)
                structure.assign_tag(unit)
                structure.started_building(unit)

    async def on_building_construction_complete(self, unit: Unit):
        """
        This function will always be called whenever a building completes.
        
        :param is unit/building:
        """
        if self.debug:
            l.g.log("CONSTRUCTION",f"{unit.name} completed building")
        for str in self.structure_tracker:
            if str.tag == unit.tag:
                str.completed_building(unit)
    
    async def on_unit_took_damage(self, unit: Unit, amount_damage_taken: float):
        if self.debug:l.g.log("MICROMANAGER",f"Unit Took Damage: {unit}")
        if self.structures.find_by_tag(unit.tag) is not None:
            l.g.log("MICROMANAGER",f"Unit {unit.name} took damage of {amount_damage_taken} and is of type Structure")
            for structure in self.structure_tracker:
                if structure.tag == unit.tag:
                    structure.building_took_damage()
        else:
            #Unit took damage, can be worker or Army
            l.g.log("MICROMANAGER",f"Unit {unit.name} took damage of {amount_damage_taken} and is of type Unit")


    async def on_upgrade_complete(self, upgrade: UpgradeId):
        """
        This function is called with the upgrade id of an upgrade that was not finished last step and is now.

        :param upgrade:
        """
        if self.debug:
            l.g.log("UPGRADE", f"Self Bot AI just told me I finished researching {upgrade}")

    async def on_unit_created(self, unit: Unit):
        """
        This function is called when a unit is created.

        :param unit:
        """
        if self.debug:
            l.g.log("ARMY", f"Bot AI just told me I finished creating a {unit}")

    async def on_enemy_unit_entered_vision(self, unit: Unit):
        """
        This function will always be called whenever an enemy comes into vision

        :param unit:
        """
        #await self.micro_manager.on_enemy_unit_entered_vision(unit)
    #End Override Functions for Bot Async Responses

    #end Bot Class
def build_order_cost(self: BotAI, build_order):
    for order in build_order:
        if order[3] == 'unit' or order[3] == 'worker' or order[3] == 'structure' or order[0] == 'REFINERY':
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
        realtime=True,
    )

if __name__ == "__main__":
    main()