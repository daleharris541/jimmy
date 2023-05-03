from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

async def ccHealthCheck(self: BotAI):
    #remaining minerals
    #vespenegas saturatet
    #controled scvs
    #hit points
    #defense (turret/bunker)
    #collect idle scvs
    pass

async def trainSCV(self: BotAI, unit_name):
    #TODO #7 When command center is upgraded to Orbital command, this no longer works
    #cc: Unit = self.townhalls(UnitTypeId.COMMANDCENTER).first
    cc : Unit = self.townhalls.first
    if self.can_afford(UnitTypeId[unit_name]):
        cc.train(UnitTypeId[unit_name])

async def getIdleSCVS(self: BotAI):
    #cc: Unit = self.townhalls(UnitTypeId.COMMANDCENTER).first
    cc : Unit = self.townhalls.first
    for scv in self.workers.idle:
            scv.gather(self.mineral_field.closest_to(cc))

async def call_down_mule(self: BotAI):
        """This function calls down a MULE to the nearest mineral field."""
        if self.bot.minerals > 300:
            closest_mineral_field = self.state.mineral_field.closest_to(self.townhall)
            await self.bot.do(self.townhall(AbilityId.CALLDOWNMULE_CALLDOWNMULE, closest_mineral_field))

async def getVespenes(self: BotAI):
    #cc: Unit = self.townhalls(UnitTypeId.COMMANDCENTER).first
    cc : Unit = self.townhalls.first
    vgs: Units = self.vespene_geyser.closer_than(20, cc)
    #loc_vespene = []
    #for vg in vgs:
        #loc_vespene.append(vg.position)
    return vgs

async def buildGas(self: BotAI, vgs):
    #loc_vespene = getVespenes()
    for vg in vgs:
         worker: Unit = self.select_build_worker(vg.position)
         if worker.build_gas(vg):
            return True
         break
    
async def saturateGas(self: BotAI):
    refineries = self.gas_buildings
    if refineries:
        refinery = refineries.random
        workers = self.workers.random_group_of(2)
        for worker in workers:
            worker.gather(refinery)

async def upgradeCC(self: BotAI, unit_name):
    if unit_name == 'ORBITALCOMMAND':
         if self.cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND):
            return True
    elif unit_name == 'PLANETARYFORTRESS':
        if self.cc(AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS):
            return True
    else:
        return False
    