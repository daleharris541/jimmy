from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units
from loguru import logger
from managers.BuildManager import get_build_order, compare_dicts, build_structure, build_addon
from managers.ArmyManager import train_unit
from managers.CC_Manager import CC_Manager
from managers.UpgradeManager import research_upgrade
from managers.ControlHelper import idle_workers

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

class Jimmy(BotAI):
    
    #following code from bot.py from smoothbrain bot as example
    def __init__(self):
        self.unit_command_uses_self_do = False
        self.distance_calculation_method = 2
        self.game_step: int = 2                      # 2 usually, 6 vs human
        self.build_starport_techlab_first = True     # always make techlab first on starport, good against dts, skytoss, burrowed roaches, and siege tanks
        self.worker_rushed = False                   # tells if we are worker rushed, if the enemies were repelled we should close the wall quick before they come back
        self.out_of_fight_workers = []               # workers with too low hp to defend a worker rush
        self.scouting_units = []                     # lists units assigned to scout so that we do not cancel their orders
        self.worker_assigned_to_repair = {}          # lists workers assigned to repair
        self.worker_assigned_to_follow = {}          # lists workers assigned to follow objects (used to prevent Planetary Fortress rushes)
        self.worker_assigned_to_defend = {}          # lists workers assigned to defend other workers during construction
        self.worker_assigned_to_resume_building = {} # lists workers assigned to resume the construction of a building
        self.worker_assigned_to_expand = {}          # lists workers assigned to expand /!\ not used yet
        self.townhall_saturations = {}               # lists the mineral saturation of townhalls in queues of 40 frames, we consider the townhall saturated if max_number + 1 >= ideal_number
        self.refineries_age = {}                     # this is here to tackle an issue with refineries having 0 workers on them when finished, although the building worker is assigned to it
        self.lifted_cc_pos = {}                      # remember where lifted ccs were
        self.scouted_at_time = -1000                 # save moment at which we scouted, so that we don't re-send units every frame
        self.buildstep = 0
        self.worker_pool = 12
        self.cc_managers = []
        self.build_order_progress = 0
        self.build_order_count = 0

        self.build_order = get_build_order(self,'16marinedrop-example')    #    16marinedrop-example or debug
        self.debug = True

    async def on_start(self):
        #print("Game started")
        #Load build manager once and print once##
        if self.build_order.count != 0:
            print("successfully loaded build order:")
            print(self.build_order)
        else:
            print("Build order failed to load")
        self.build_order_count = len(self.build_order)
        
    async def on_step(self, iteration: int):
        # Find all Command Centers
        cc_list = self.townhalls
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

        await idle_workers(self)
        
        if len(self.build_order) > 0:
            if await build_next(self, self.build_order[self.buildstep], self.cc_managers):
                #TODO: keep this code until the check against the current buildings is finished
                self.build_order.pop(self.buildstep) #remove item from the list once it's done
                self.build_order_progress = (self.build_order_count-len(self.build_order))
                if self.debug:
                        buildOrderPercentage = 100 * ((self.build_order_count-len(self.build_order))/self.build_order_count)
                        print(f"Build Step: {self.buildstep} Total Steps Remaining:{len(self.build_order)}")
                self.build_order.pop(self.buildstep) #remove item from the list once it's done
                self.build_order_progress = (self.build_order_count-len(self.build_order))
                if self.debug:
                        buildOrderPercentage = 100 * ((self.build_order_count-len(self.build_order))/self.build_order_count)
                        print(f"Build Step: {self.buildstep} Total Steps Remaining:{len(self.build_order)}")
                        print("Percentage of build order completed: %.2f%%" % (buildOrderPercentage))
                #if self.buildstep < (len(self.build_order)):
                    #self.buildstep = self.buildstep + 1
                    
                #if self.buildstep < (len(self.build_order)):
                    #self.buildstep = self.buildstep + 1
                    
                #send to check against build order step

        #await compare_dicts(self, self.build_order, self.buildstep) #debug

    async def on_end(self):
        print("Game ended.")
        # Do things here after the game ends

#check prerequisites
async def build_next(self: BotAI, buildrequest, cc_managers):
    unit_name, unitId, unitType, supplyRequired, gametime, frame = buildrequest
    
    #example for how to read time target and execution:
    #Target time for 2nd SCV to be queued to build - 12 seconds. Actual execution in game time: 8 seconds (Ahead)
    if self.debug:
        print("Unit Name: SupplyRequired : Supply Used: Target Time - " + str(gametime) + ": Current Minerals")
        print(unit_name + "          " + str(supplyRequired) + "             " + str(self.supply_used) + "           " + (str(self.time)).split(".")[0] + "        " + str(self.minerals))
    #logger.info(f"Executing at {self.time} - Step Time = {gametime}")
    #would be cool to subtract the timing of the build based on actual and show ahead or behind

    if unitType == 'action':
        #skip actions
        return True
    elif unitType == 'upgrade':
        await research_upgrade(self, unit_name)
        return True
    #elif unitType == 'unit':
    #    return True

    if self.can_afford(UnitTypeId[unit_name]) and self.tech_requirement_progress(UnitTypeId[unit_name]) == 1:
        if unitType == 'structure':
            if unit_name == 'REFINERY':
                cc_managers[0].build_refinery()
                return True
            elif unit_name == 'ORBITALCOMMAND':
                cc_managers[0].upgrade_orbital_command()
                return True
            elif "TECHLAB" in unit_name or "REACTOR" in unit_name:
                if await build_addon(self, unit_name):
                    return True
            else:
                if await build_structure(self, unit_name): #building placement logic missing
                    return True
        elif unitType == 'unit':
            #skip unit training
            return True
        elif unitType == 'worker':
            await cc_managers[0].train_worker(70)
            return True

def main():
    run_game(
        maps.get("BerlingradAIE"),
        [Bot(Race.Terran, Jimmy()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=True,
    )

if __name__ == "__main__":
    main()