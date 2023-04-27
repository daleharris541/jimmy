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
        #self.queue = [["SUPPLYDEPOT", "build", 15, 1], ["BARRACKS", "build", 15, 1]]
        #self.build_progress()

    @staticmethod
    async def create(bot: BotAI) -> 'BuildManager':
        instance = BuildManager(bot)
        await instance.execute_build_queue()
        return instance
    
    async def execute_build_queue(self):
        queue = [["SUPPLYDEPOT", "build", 15, 1], ["BARRACKS", "build", 15, 1]]
        for active in queue:
            unit_name, action, atSupply, quantity = active

            if self.check_prerequisites(unit_name, quantity):
                await self.build_unit(unit_name)
            else:
                continue
            
            print(queue[0])
            queue.remove(active) #not working

    #check prerequisites(minerals/gas, under construction, already existing)
    def check_prerequisites(self, unit_name, quantity):
        if self.bot.can_afford(UnitTypeId[unit_name]) and not self.bot.structures(UnitTypeId[unit_name]):
            return True
        else:
            return False  
        
    def build_progress(self):
        structures = self.bot.structures
        structure_counts = {}

        for unit in structures:
            if unit.name in structure_counts:
                structure_counts[unit.name] += 1
            else:
                structure_counts[unit.name] = 1

        sorted_structure_counts = sorted(structure_counts.items())

        print(sorted_structure_counts)  #debug
        #return sorted_structure_counts 
    
    #build request execution
    async def build_unit(self, unit_name):
        CCs: Units = self.bot.townhalls(UnitTypeId.COMMANDCENTER)   #remove - debug only / main base logic
        cc: Unit = CCs.first                                        #remove - debug only / main base logic
        if self.bot.can_afford(UnitTypeId[unit_name]):
            await self.bot.build(UnitTypeId[unit_name], near=cc.position.towards(self.bot.game_info.map_center, 8)) #building placement logic missing

    def getBuildOrder(self):
        return makeBuildOrder('tools/test.json')