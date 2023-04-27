from tools import makeBuildOrder

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
#from jimmy import *

#This class should do the following.
#   -Execute Build order.
#   -Track Build order progress
#   -Building placement.
#   -Rebuild destroyed structures

# class BuildManager():
#     # def __init__(self, bot : BotAI):
#     #     mybot = bot
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

#     async def build_unitd(ccs, mybot, unit_name):
#         #CCs: Units = mybot.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
#         cc: Unit = ccs.first                                    #remove - debug only / main base logic
#         print("I'm in build_unitd")
#         if mybot.can_afford(UnitTypeId.unit_name):
#             print("I can afford a Supply Depot and should be building one now")
#             await mybot.build(UnitTypeId.unit_name, near=cc.position.towards(mybot.game_info.map_center, 8)) #building placement logic missing
   
#     def getBuildOrder(self):
#         return makeBuildOrder('tools/test.json')

#good info on calling async function in another class: https://stackoverflow.com/questions/42009202/how-to-call-a-async-function-contained-in-a-class

class BuildManager1():
    def __init__(self, mybot): #works
        self.bot = mybot #works
        #print("I'm properly assigning Jimmy bot to self.bot variable upon initiation") #works
        #print(str(self.bot.supply_left)) #works!
        #self.queue = [["SUPPLYDEPOT", "build", 15, 1]] #debug
        #self.execute_build_queue(self.queue)

    #@staticmethod
    # async def create(bot: BotAI) -> 'BuildManager':
    #     queue = [["SUPPLYDEPOT", "build", 15, 1], ["COMMANDCENTER", "build", 15, 1]]
    #     instance = BuildManager(bot)
    #     await instance.execute_build_queue(queue)
    #     return instance
    
    # async def execute_build_queue(self, queue):
    #     for active in queue:
    #         unit_name, action, atSupply, quantity = active
            
    #         if self.can_build(unit_name):
    #             await self.build_unit(unit_name)
    #         else:
    #             continue
            
    #         queue.remove(active)

    #check prerequisites(minerals/gas, under construction, already existing)
    # def can_build(self, unit_name):
    #     if self.bot.can_afford(UnitTypeId[unit_name]):
    #         return True
    #     else:
    #         return False  
    
    #build request execution
    # async def build_unit(self, unit_name):
    #     CCs: Units = self.bot.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
    #     cc: Unit = CCs.first                                        #remove - debug only / main base logic
    #     if self.bot.can_afford(UnitTypeId[unit_name]):
    #         await self.bot.build(UnitTypeId[unit_name], near=cc.position.towards(self.bot.game_info.map_center, 8)) #building placement logic missing

#understanding relations between classes: https://stackoverflow.com/questions/46686008/access-self-from-another-class-in-python
#passing variables between classes: https://stackoverflow.com/questions/7501706/how-do-i-pass-variables-between-class-instances-or-get-the-caller

    async def build_unitf(self, mybot, building_name):
        # I took out this from parameters: Jimmy: BotAI
        #self.bot = mybot
        CCs: Units = mybot.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
        cc: Unit = mybot.townhalls.first                              #remove - debug only / main base logic
        print("I'm in build_unitf and next is how much supply Jimmy bot has remaining")
        print(str(mybot.supply_left))

        if mybot.can_afford(UnitTypeId[building_name]):
            print("I can afford a Supply Depot and should be building one now")
            await mybot.build(UnitTypeId[building_name], near=cc.position.towards(mybot.game_info.map_center, 8)) #building placement logic missing
   
    def getBuildOrder(self):
        return makeBuildOrder('tools/test.json')