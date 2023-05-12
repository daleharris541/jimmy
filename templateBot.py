import datetime

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units
from typing import FrozenSet, Set
from loguru import logger
from managers.BuildManager import (
    get_build_order,
    compare_dicts,
    build_structure,
    build_addon,
)
from managers.ArmyManager import train_unit
from managers.CC_Manager import CC_Manager
from managers.UpgradeManager import research_upgrade
from managers.ControlHelper import idle_workers

from debug import (
    label_unit,
    draw_building_points,
    draw_expansions,
    get_direction_vector,
    get_distance,
    calc_supply_depot_zones,
    calc_tech_building_zones,
)

# https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html


class Jimmy(BotAI):
    def __init__(self):
        self.distance_calculation_method = 2
        self.game_step: int = 2  # 2 usually, 6 vs human
        self.buildstep = 0
        self.worker_pool = 12
        self.cc_managers = []
        self.build_order_progress = 0
        self.build_order_count = 0
        self.supply_depot_placement_list: Set[Point2] = []
        self.tech_buildings_placement_list: Set[Point2] = []
        self.normal_buildings = ["BARRACKS", "STARPORT", "ENGINEERINGBAY", "FACTORY", "FUSION CORE", "ARMORY"]
        self.building_list = []
        self.build_order = get_build_order(self, "16marinedrop-example")  # 16marinedrop-example or debug
        self.debug = True

    async def on_start(self):
        # print("Game started")
        if self.build_order.count != 0:
            print("successfully loaded build order:")
            # print(self.build_order)
        else:
            print("Build order failed to load")
        self.build_order_count = len(self.build_order)
        self.building_list = [step for step in self.build_order if step[0] in self.normal_buildings]
        # Have to figure out how to reconcile the situation carefully
        # 7 points are added, 6 buildings are in list
        # The first barracks is automatic, so my choice is to add additional entry to building list to match
        print(f"Building List Count: {len(self.building_list)}")
        print(self.building_list[0][0])

        temp, depot1, depot2 = calc_supply_depot_zones(self)
        self.supply_depot_placement_list: Set[Point2] = temp
        
        self.corner_depots_possition= [depot1, depot2, self.supply_depot_placement_list[2]]
        self.tech_buildings_placement_list: Set[Point2] = calc_tech_building_zones(self, self.corner_depots_possition, self.building_list)

    async def on_step(self, iteration: int):
        # Find all Command Centers
        cc_list = self.townhalls
        # Create a new CC_Manager instance for each Command Center if it doesn't already exist
        for cc in cc_list:
            if not any(
                cc_manager.townhall.tag == cc.tag for cc_manager in self.cc_managers
            ):
                cc_manager = CC_Manager(self, cc)
                self.cc_managers.append(cc_manager)

        # Call the manage_cc function for each CC_Manager instance
        for cc_manager in self.cc_managers:
            if cc_manager.townhall.tag not in self.townhalls.tags:
                self.cc_managers.remove(cc_manager)
            else:
                await cc_manager.manage_cc(self.worker_pool)

        await idle_workers(self)

        if self.debug:
            green = Point3((0, 255, 0))
            red = Point3((0, 0, 255))
            blue = Point3((255, 0, 0))
            self.client.debug_text_screen(text=str(self.build_order[0]), pos=Point2((0, 0)), color=green, size=18)
            # properly send each item in the build order for tech buildings
            draw_building_points(self, self.supply_depot_placement_list, green, self.supply_depot_placement_list, 1)
            draw_building_points(self, self.tech_buildings_placement_list, green, self.building_list, 1.5)

        # We want to be able to quickly respond to enemy attack:
        # This is like the limbic system, it can quickly take over if we are in danger
        # Otherwise, let the frontal lobe do all the work

        # Perhaps we can initiate this into a function call when an enemy is detected
        # instead of always doing this code + responding with attacking with nearby units
        # We can do this by having a ramp location instead

        if len(self.build_order) > 0:
            if await build_next(
                self,
                self.build_order[self.buildstep],
                self.cc_managers,
                self.supply_depot_placement_list,
                self.tech_buildings_placement_list,
            ):
                # TODO: keep this code until the check against the current buildings is finished
                self.build_order.pop(
                    self.buildstep
                )  # remove item from the list once it's done
                self.buildstep += 1
                self.build_order_progress = self.build_order_count - len(
                    self.build_order
                )
                if self.debug:
                    buildOrderPercentage = 100 * (
                        (self.build_order_count - len(self.build_order))
                        / self.build_order_count
                    )
                    print(
                        f"Build Step: {self.build_order_progress} Total Steps Remaining:{len(self.build_order)}"
                    )
                    print(
                        "Percentage of build order completed: %.2f%%"
                        % (buildOrderPercentage)
                    )


# Move to build_manager
async def build_next(self: BotAI, buildrequest, cc_managers, sd_pos, tech_pos):
    unit_name, unitId, unitType, supplyRequired, gametime, frame = buildrequest

    if self.debug:
        timer = int(self.time)
        realtime = datetime.timedelta(seconds=timer)
        #print(f"Name: {unit_name} | Supply Target: {supplyRequired} | Supply Used: {self.supply_used} | BO Target Time: {gametime} | Game Time: {realtime})

    if unitType == "action":
        # skip actions
        return True
    elif unitType == "upgrade":
        await research_upgrade(self, unit_name)
        return True

    if (
        self.can_afford(UnitTypeId[unit_name])
        and self.tech_requirement_progress(UnitTypeId[unit_name]) == 1
    ):
        if unitType == "structure":
            if unit_name == "REFINERY":
                cc_managers[0].build_refinery()
                return True
            elif unit_name == "ORBITALCOMMAND":
                cc_managers[0].upgrade_orbital_command()
                return True
            elif "TECHLAB" in unit_name or "REACTOR" in unit_name:
                if await build_addon(self, unit_name):
                    return True
            elif unit_name == "SUPPLYDEPOT":
                if await build_structure(self, unit_name, sd_pos[0]):
                    return True
            else:
                if await build_structure(
                    self, unit_name, tech_pos
                ):  # building placement logic missing
                    return True
        elif unitType == "unit":
            # skip unit training
            return True
        elif unitType == "worker":
            await cc_managers[0].train_worker(70)
            return True

def main():
    run_game(
        maps.get("DeathAuraLE"),
        [Bot(Race.Terran, Jimmy()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=True,
    )

if __name__ == "__main__":
    main()
