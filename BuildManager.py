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
#   -Send workers back to Comand Center / Mining

class BuildManager():
    def __init__(self, bot : BotAI):
        self.bot = bot
        #self.queue = [["SUPPLYDEPOT", "build", 15, 1]] #debug
        #self.execute_build_queue(self.queue)
        self.debug()

    def execute_build_queue(self, queue):
        for active in queue:
            unit_name, action, at_supply, quantity = active
            
            if self.can_build(unit_name):
                self.build_unit(unit_name)
            else:
                continue
            
            queue.remove(active)

    def can_build(self, unit_name):
        return True #debug
        

    def build_unit(self, unit_name):
        print("one")
        pass

    def debug(self):
        CCs: Units = self.bot.townhalls(UnitTypeId.COMMANDCENTER)
        cc: Unit = CCs.first
        if self.bot.can_afford(UnitTypeId.SUPPLYDEPOT):
            print(f"ComandCenter {cc.position} | MapCenter {self.bot.game_info.map_center}")
            #self.bot.townhalls[0].train(UnitTypeId.SCV)
            #self.bot.build(UnitTypeId.SUPPLYDEPOT, near=cc.position.towards(self.bot.game_info.map_center, 8))
        
    def getBuildOrder(self):
        return makeBuildOrder('tools/test.json')