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
from BuildManager import getBuildOrder, build_next, build_progress

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
        self.produce_from_starports = True
        self.produce_from_factories = True
        self.produce_from_barracks = True
        self.scouted_at_time = -1000                 # save moment at which we scouted, so that we don't re-send units every frame
        self.buildstep = 0

        self.build_order = getBuildOrder(self,'test')    #BuildManager(self)

        super().__init__()

    async def on_start(self):
        #print("Game started")
        # Do things here before the game starts
        self.CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        self.cc: Unit = self.CCs.first
        #Load build manager once and print once
        if self.build_order.count != 0:
            print("successfully loaded build order:")
            print(self.build_order)
        else:
            print("Build order failed to load")
        
    async def on_step(self, iteration: int):

        if not self.CCs:
            target: Point2 = self.enemy_structures.random_or(
                self.enemy_start_locations[0]
            ).position
            for unit in self.workers | self.units(UnitTypeId.MARINE):
                unit.attack(target)
            return
        
        #if self.can_afford(UnitTypeId.SCV) and self.supply_workers < 17 and self.cc.is_idle:
        #    self.cc.train(UnitTypeId.SCV)
        
        if self.buildstep != len(self.build_order):
            if await build_next(self, self.build_order[self.buildstep]):
                if self.buildstep < (len(self.build_order)):
                    self.buildstep = self.buildstep + 1
                else:
                    print("buid order finished")

        #print(self.buildstep)
        build_progress(self, self.build_order,self.buildstep)

    async def on_end(self):
        print("Game ended.")
        # Do things here after the game ends

def main():
    run_game(
        maps.get("BerlingradAIE"),
        [Bot(Race.Terran, Jimmy()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()