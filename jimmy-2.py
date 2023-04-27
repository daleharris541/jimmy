from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units
from datetime import datetime

from BuildManager import BuildManager1
from tools import makeBuildOrder

#Used base BurnySC2 Bot base to make Jimmy https://github.com/BurnySc2/python-sc2/tree/3ca497e1d1e8390da1633c79939c22d5f9b12c39

class Jimmy(BotAI):
    async def on_start(self):
        self.client.game_step = 2

    # pylint: disable=R0912
    async def on_step(self, iteration):

        #initiate buildmanager now


        ccs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)
        # If we don't have a townhall anymore, send all units to attack
        if not ccs:
            target: Point2 = self.enemy_structures.random_or(
                self.enemy_start_locations[0]
            ).position
            for unit in self.workers | self.units(UnitTypeId.MARINE):
                unit.attack(target)
            return
        
        #buildManager = BuildManager()


        #Start a 10 iteration counting method
        # Once 10 has gone by, reset it to 0
        # This can be used to keep some built in delays
        # maybe not as efficient: (datetime.now()).second will give seconds
        # can create 1 or 2 second delays, str((datetime.now()).second)[1] gives second digit properly
        if 'iterationdelay' in locals():
            iterationdelay = iterationdelay+1
        else:
            iterationdelay = 0
        
        if iterationdelay == 10:
                iterationdelay = 0
        
        #starting command center is now cc variable
        cc: Unit = ccs.first
        self.cc = cc
        # async def build_unitd(self,cc, unit_name):
        # #CCs: Units = mybot.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
        #                           #remove - debug only / main base logic
        #     print("I'm in build_unitd")
        #     if self.can_afford(UnitTypeId.SUPPLYDEPOT):
        #         print("I can afford a Supply Depot and should be building one now")
        #         await self.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.game_info.map_center, 8)) #building placement logic missing

        #await self.build_unitd() #this code works, function inside Jimmy class
        #Builder = BuildManager #this runs without any issue

        #instantiate the class into a new object?
        Builder = BuildManager1(self)
        await Builder.build_unitf(self,"SUPPLYDEPOT")
        #build home base
        # Build more SCVs until 19 (does this mean it won't build a barracks early?)
        if self.can_afford(UnitTypeId.SCV) and self.supply_workers < 19 and cc.is_idle:
            cc.train(UnitTypeId.SCV)

        #if self.can_afford(UnitTypeId.SUPPLYDEPOT):
            #print("I am putting this inside the main class under on_step function")
            #await self.build(UnitTypeId.SUPPLYDEPOT, near=self.cc.position.towards(self.game_info.map_center, 8)) #building placement logic missing

        #Look at this section as a separate chain of building
        # Build barracks if we have none
        # if self.tech_requirement_progress(UnitTypeId.BARRACKS) == 1:
        #     if not self.structures(UnitTypeId.BARRACKS):
        #         if self.can_afford(UnitTypeId.BARRACKS):
        #             #We are now building a barracks and we have the following supply
        #             print("We have " + str(self.supply_workers) + " workers and are building a barracks")
        #             await self.build(
        #                 UnitTypeId.BARRACKS,
        #                 near=cc.position.towards(self.game_info.map_center, 8),
        #             )
        
        #Build Reaper to Harass and Scout

        # Build more supply depots
        #Tweak supply left to build it earlier or later depending on timing
        # if (
        #     self.supply_left < 6
        #     and self.supply_used >= 14
        #     and not self.already_pending(UnitTypeId.SUPPLYDEPOT)
        # ):
        #     if self.can_afford(UnitTypeId.SUPPLYDEPOT):
        #         await self.build(
        #             UnitTypeId.SUPPLYDEPOT,
        #             near=cc.position.towards(self.game_info.map_center, 8),
        #         )

        # Build another barracks if we have exactly 1
        # if self.tech_requirement_progress(UnitTypeId.BARRACKS) == 1:
        #     if self.structures(UnitTypeId.BARRACKS) == 1:
        #         if self.can_afford(UnitTypeId.BARRACKS):
        #             print("Building second barracks as we always need 2")
        #             await self.build(
        #                 UnitTypeId.BARRACKS,
        #                 near=cc.position.towards(self.game_info.map_center, 8),
        #             )

            # Build a refinery if we don't have any
            # elif self.structures(UnitTypeId.BARRACKS) and self.gas_buildings.amount < 1:
            #     if self.can_afford(UnitTypeId.REFINERY):
            #         vgs: Units = self.vespene_geyser.closer_than(20, cc)
            #         for vg in vgs:
            #             if self.gas_buildings.filter(
            #                 lambda unit: unit.distance_to(vg) < 1
            #             ):
            #                 break

            #             worker: Unit = self.select_build_worker(vg.position)
            #             if worker is None:
            #                 break

            #             worker.build_gas(vg)
            #             break
            
            # Build factory if we dont have one
            # if self.tech_requirement_progress(UnitTypeId.FACTORY) == 1:
            #     factories: Units = self.structures(UnitTypeId.FACTORY)
            #     if not factories:
            #         if self.can_afford(UnitTypeId.FACTORY):
            #             await self.build(
            #                 UnitTypeId.FACTORY,
            #                 near=cc.position.towards(self.game_info.map_center, 8),
            #             )
            #     # Build starport once we can build starports, up to 2
            #     elif (
            #         factories.ready
            #         and self.structures.of_type(
            #             {UnitTypeId.STARPORT, UnitTypeId.STARPORTFLYING}
            #         ).ready.amount
            #         + self.already_pending(UnitTypeId.STARPORT)
            #         < 2
            #     ):
            #         if self.can_afford(UnitTypeId.STARPORT):
            #             await self.build(
            #                 UnitTypeId.STARPORT,
            #                 near=cc.position.towards(
            #                     self.game_info.map_center, 15
            #                 ).random_on_distance(8),
            #             )
        # Saturate refineries
        # This sort of works and self corrects, but it assigns workers too quickly if they don't get there fast enough
        # Maybe bringing in some type of delay without pausing the script or just sending one and making check have to go through a basic adding script to once it
        # goes through 10 iterations, it checks it again - could be good to delay some things this way, not only gas
        # this str((datetime.now()).second)[1] must end in 0 in order for it to kick off
        # it will create a slow addition of SCVs and only add them to refineries if they aren't optimal every 10 seconds for checks
        # downside is it will create uneven gas mining times but better to do that than add 4 at once
        # for refinery in self.gas_buildings:
        #     if refinery.assigned_harvesters < refinery.ideal_harvesters and str((datetime.now()).second)[1] == "0":
        #         worker: Units = self.workers.closer_than(10, refinery)
        #         if worker:
        #             worker.random.gather(refinery)

        #1 CC
        #"Terran_ReaperRush"     : { "Race" : "Terran", "OpeningBuildOrder" : ["Barracks", "Refinery", "Barracks", "Refinery",  "Barracks", "Factory", "Starport", "FusionCore", "Battlecruiser", "Armory", "Armory" ] }


        # Build proxy barracks
        # elif self.structures(UnitTypeId.BARRACKS).amount < 3 or (
        #     self.minerals > 400 and self.structures(UnitTypeId.BARRACKS).amount < 3
        # ):
        #     if self.can_afford(UnitTypeId.BARRACKS):
        #         p: Point2 = self.game_info.map_center.towards(
        #             self.enemy_start_locations[0], 25
        #         )
        #         await self.build(UnitTypeId.BARRACKS, near=p)

        # Train marines
        # for rax in self.structures(UnitTypeId.BARRACKS).ready.idle:
        #     if self.can_afford(UnitTypeId.MARINE):
        #         rax.train(UnitTypeId.MARINE)

        # Send idle workers to gather minerals near command center
        # this has no checks and puts more idle workers than the CC can manage
        # would rather the SCV be put to proper use for build times and perhaps stay idle
        # early build times, SCV should go out to first expansion base, build supply depots non-stop, etc
        # for scv in self.workers.idle:
        #     scv.gather(self.mineral_field.closest_to(cc))

    async def build_unitd(self):
        #Syes, this one works! Just call with await self.build_unitd()
        CCs: Units = self.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
        cc = CCs.first                          #remove - debug only / main base logic
        print("I'm in build_unitd and next is how much supply Jimmy bot has remaining")
        print(str(self.supply_left))
        if self.can_afford(UnitTypeId.SUPPLYDEPOT):
            print("I can afford a Supply Depot and should be building one now")
            await self.build(UnitTypeId.SUPPLYDEPOT, near=self.cc.position.towards(self.game_info.map_center, 8)) #building placement logic missing


    #Place all Drawing Definitions from ramp_wall.py
    def draw_ramp_points(self):
        print("draw ramp points")
        for ramp in self.game_info.map_ramps:
            for p in ramp.points:
                h2 = self.get_terrain_z_height(p)
                pos = Point3((p.x, p.y, h2))
                color = Point3((255, 0, 0))
                if p in ramp.upper:
                    color = Point3((0, 255, 0))
                if p in ramp.upper2_for_ramp_wall:
                    color = Point3((0, 255, 255))
                if p in ramp.lower:
                    color = Point3((0, 0, 255))
                self.client.debug_box2_out(
                    pos + Point2((0.5, 0.5)), half_vertex_length=0.25, color=color
                )
                # Identical to above:
                # p0 = Point3((pos.x + 0.25, pos.y + 0.25, pos.z + 0.25))
                # p1 = Point3((pos.x + 0.75, pos.y + 0.75, pos.z - 0.25))
                # logger.info(f"Drawing {p0} to {p1}")
                # self.client.debug_box_out(p0, p1, color=color)
    
    def draw_expansions(self):
        print("draw expansions")
        green = Point3((0, 255, 0))
        for expansion_pos in self.expansion_locations_list:
            height = self.get_terrain_z_height(expansion_pos)
            expansion_pos3 = Point3((*expansion_pos, height))
            self.client.debug_box2_out(
                expansion_pos3, half_vertex_length=2.5, color=green
            )

    def draw_vision_blockers(self):
        for p in self.game_info.vision_blockers:
            h2 = self.get_terrain_z_height(p)
            pos = Point3((p.x, p.y, h2))
            p0 = Point3((pos.x - 0.25, pos.y - 0.25, pos.z + 0.25)) + Point2((0.5, 0.5))
            p1 = Point3((pos.x + 0.25, pos.y + 0.25, pos.z - 0.25)) + Point2((0.5, 0.5))
            # logger.info(f"Drawing {p0} to {p1}")
            color = Point3((255, 0, 0))
            self.client.debug_box_out(p0, p1, color=color)

    def draw_example(self):
        # Draw green boxes around SCVs if they are gathering, yellow if they are returning cargo, red the rest
        scv: Unit
        for scv in self.workers:
            pos = scv.position3d
            p0 = Point3((pos.x - 0.25, pos.y - 0.25, pos.z + 0.25))
            p1 = Point3((pos.x + 0.25, pos.y + 0.25, pos.z - 0.25))
            # Red
            color = Point3((255, 0, 0))
            if scv.is_gathering:
                color = Point3((0, 255, 0))
            elif scv.is_returning:
                color = Point3((255, 255, 0))
            self.client.debug_box_out(p0, p1, color=color)

        # Draw lines from structures to command center
        if self.townhalls:
            cc = self.townhalls[0]
            p0 = cc.position3d
            if not self.structures:
                return
            structure: Unit
            for structure in self.structures:
                if structure == cc:
                    continue
                p1 = structure.position3d
                # Red
                color = Point3((255, 0, 0))
                self.client.debug_line_out(p0, p1, color=color)

            # Draw text on barracks
            if structure.type_id == UnitTypeId.BARRACKS:
                # Blue
                color = Point3((0, 0, 255))
                pos = structure.position3d + Point3((0, 0, 0.5))
                # TODO: Why is this text flickering
                self.client.debug_text_world(
                    text="MY RAX", pos=pos, color=color, size=16
                )

        # Draw text in top left of screen
        self.client.debug_text_screen(
            text="Hello world!", pos=Point2((0, 0)), color=None, size=16
        )
        self.client.debug_text_simple(text="Hello world2!")

    #BuildOrder Class
    #To make it easier, I'll just use Terran everything, but can be modified
    #"Terran_ReaperRush"     : {"OpeningBuildOrder" : ["Barracks", "Refinery", "Barracks", "Refinery",  "Barracks", "Factory", "Starport", "FusionCore", "Battlecruiser", "Armory", "Armory" ] }
    
class BuildOrder:

    def __init__(self, strategy, workercount):
        self.strategy = strategy
        queue = []
    
    def add_unit(self, BuildOrderItem):
        self.queue.append(BuildOrderItem)



def main():
    run_game(
        maps.get("AcropolisLE"),
        [Bot(Race.Terran, Jimmy()), Computer(Race.Zerg, Difficulty.VeryEasy)],
        realtime=True,
    )


if __name__ == "__main__":
    main()

# class BuildManager1:
#     def __init__(self, Jimmy : BotAI):
#         self.bot = Jimmy
#         print("I'm properly assigning Jimmy bot to self.bot variable upon initiation")
#         print(str(Jimmy.supply_left))
#         #self.queue = [["SUPPLYDEPOT", "build", 15, 1]] #debug
#         #self.execute_build_queue(self.queue)

#     @staticmethod
#     # async def create(bot: BotAI) -> 'BuildManager':
#     #     queue = [["SUPPLYDEPOT", "build", 15, 1], ["COMMANDCENTER", "build", 15, 1]]
#     #     instance = BuildManager(bot)
#     #     await instance.execute_build_queue(queue)
#     #     return instance
    
#     # async def execute_build_queue(self, queue):
#     #     for active in queue:
#     #         unit_name, action, atSupply, quantity = active
            
#     #         if self.can_build(unit_name):
#     #             await self.build_unit(unit_name)
#     #         else:
#     #             continue
            
#     #         queue.remove(active)

#     #check prerequisites(minerals/gas, under construction, already existing)
#     # def can_build(self, unit_name):
#     #     if self.bot.can_afford(UnitTypeId[unit_name]):
#     #         return True
#     #     else:
#     #         return False  
    
#     #build request execution
#     # async def build_unit(self, unit_name):
#     #     CCs: Units = self.bot.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
#     #     cc: Unit = CCs.first                                        #remove - debug only / main base logic
#     #     if self.bot.can_afford(UnitTypeId[unit_name]):
#     #         await self.bot.build(UnitTypeId[unit_name], near=cc.position.towards(self.bot.game_info.map_center, 8)) #building placement logic missing

# #understanding relations between classes: https://stackoverflow.com/questions/46686008/access-self-from-another-class-in-python

#     async def build_unitf(self):
#         # I took out this from parameters: Jimmy: BotAI
#         #CCs: Units = mybot.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
#         cc: Unit = Jimmy.townhalls.first                              #remove - debug only / main base logic
#         print("I'm in build_unitf and next is how much supply Jimmy bot has remaining")
#         print(str(Jimmy.supply_left))

#         if Jimmy.can_afford(UnitTypeId.SUPPLYDEPOT):
#             print("I can afford a Supply Depot and should be building one now")
#             await self.bot.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.bot.game_info.map_center, 8)) #building placement logic missing
   
#     def getBuildOrder(self):
#         return makeBuildOrder('tools/test.json')