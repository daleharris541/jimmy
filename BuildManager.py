from tools import makeBuildOrder

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units

#This class should do the following.
#   -Execute Build order.
#   -Track Build order progress
#   -Building placement.
#   -Rebuild destroyed structures

class BuildManager():
    def __init__(self, bot: BotAI):
        self.bot = bot
        #self.queue = [["SUPPLYDEPOT", "build", 15, 1]] #debug
        #self.execute_build_queue(self.queue)

    @staticmethod
    async def create(bot: BotAI) -> 'BuildManager':
        queue = [["SUPPLYDEPOT", "build", 15, 1], ["COMMANDCENTER", "build", 15, 1]]
        instance = BuildManager(bot)
        await instance.execute_build_queue(queue)
        return instance
    
    async def execute_build_queue(self, queue):
        for active in queue:
            unit_name, action, atSupply, quantity = active
            
            if self.can_build(unit_name):
                await self.build_unit(unit_name)
            else:
                continue
            
            queue.remove(active)

    #check prerequisites(minerals/gas, under construction, already existing)
    def can_build(self, unit_name):
        if self.bot.can_afford(UnitTypeId[unit_name]):
            return True
        else:
            return False  
    
    #build request execution
    async def build_unit(self, unit_name):
        CCs: Units = self.bot.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
        cc: Unit = CCs.first                                        #remove - debug only / main base logic
        if self.bot.can_afford(UnitTypeId[unit_name]):
            await self.bot.build(UnitTypeId[unit_name], near=cc.position.towards(self.bot.game_info.map_center, 8)) #building placement logic missing

    def getBuildOrder(self):
        return makeBuildOrder('tools/test.json')