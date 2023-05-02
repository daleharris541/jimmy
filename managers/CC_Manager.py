from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
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
    cc: Unit = self.townhalls(UnitTypeId.COMMANDCENTER).first
    if self.can_afford(UnitTypeId[unit_name]):
        cc.train(UnitTypeId[unit_name])
    pass

async def getIdleSCVS(self: BotAI):
    cc: Unit = self.townhalls(UnitTypeId.COMMANDCENTER).first
    for scv in self.workers.idle:
            scv.gather(self.mineral_field.closest_to(cc))

async def getVespenes(self: BotAI):
    cc: Unit = self.townhalls(UnitTypeId.COMMANDCENTER).first
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
    for refinery in refineries:
        if refinery.assigned_harvesters < refinery.ideal_harvesters:
                worker: Units = self.workers.closer_than(10, refinery)
                if worker:
                    worker.random.gather(refinery)
        else:
             return True
