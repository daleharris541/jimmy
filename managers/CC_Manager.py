from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

class CC_Manager:

    def __init__(self, bot: BotAI, townhall: Unit):
        self.bot = bot
        self.townhall = townhall
        self.sphere_of_influence = 10

    async def manage_cc(self, worker_pool):
        """The main function of the CC_Manager that manages the Command Center."""
        ### UPDATE VARIABLES ###
        self.cc = self.bot.structures.find_by_tag(self.townhall.tag)
        self.workers = self.get_workers()
        self.minerals = self.get_mineral_fields()
        self.vespene = self.get_vespene_geysers()
        ### BEHAVIOR ###
        if self.cc.name == 'OrbitalCommand' and self.cc.position in self.bot.expansion_locations_list:
            self.call_down_mule()
        #await self.train_worker(worker_pool)
        #await self.get_idle_worker()    #LOGIC: Only execute if CC is on expansion location
        #if self.bot.tech_requirement_progress(UnitTypeId.ORBITALCOMMAND) == 1:
        #    self.upgrade_orbital_command()

    async def train_worker(self, worker_pool):
        """This function builds workers"""
        if len(self.bot.workers) < worker_pool and len(self.workers) < 22 and self.cc.is_idle and self.bot.can_afford(UnitTypeId.SCV):
            self.cc.train(UnitTypeId.SCV)

    async def get_idle_worker(self):
        """This function collects all idle workers"""
        workers = [scv for scv in self.workers if scv.is_idle and self.cc.distance_to(scv) <= self.sphere_of_influence]
        for worker in workers:
            mineral = self.bot.mineral_field.closest_to(worker)
            worker.gather(mineral)

    def upgrade_orbital_command(self):
        """This function upgrades the Command Center to an Orbital Command."""
        if self.cc.is_idle and self.bot.can_afford(UnitTypeId.ORBITALCOMMAND):
            self.cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)

    def upgrade_planetaryfortress(self):
        """This function upgrades the Command Center to Planetary Fortress."""
        if self.cc.is_idle and self.bot.can_afford(UnitTypeId.PLANETARYFORTRESS):
            self.cc(AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS)

    def call_down_supply(self):
        """This function calls down a Supply Depot to the nearest buildable location."""
        if self.cc.energy > 50:
            closest_supply_depot = self.bot.structures(UnitTypeId.SUPPLYDEPOT).random
            self.cc(AbilityId.SUPPLYDROP_SUPPLYDROP, closest_supply_depot)

    def call_down_mule(self):
        """This function calls down a MULE to the nearest mineral field."""
        if self.cc.energy > 50:
            closest_mineral_field = self.bot.mineral_field.closest_to(self.cc)
            self.cc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, closest_mineral_field)

    def scanner_sweep(self, postion):
        """This function calls down a MULE to the nearest mineral field."""
        if self.cc.energy > 50:
            self.cc(AbilityId.SCANNERSWEEP_SCAN, postion)

    def get_workers(self):
        controlled_worker = Units([], self)
        for worker in self.bot.workers:
            if self.townhall.distance_to(worker) < self.sphere_of_influence:
                controlled_worker.append(worker)
        return controlled_worker
    
    def get_mineral_fields(self):
        """This function returns the mineral fields close to the Command Center."""
        controlled_minerals = Units([], self)
        for mineral_field in self.bot.mineral_field:
            if self.townhall.distance_to(mineral_field) < self.sphere_of_influence:
                controlled_minerals.append(mineral_field)
        return controlled_minerals
    
    def get_vespene_geysers(self):
        """This function returns the vespene geysers close to the Command Center."""
        controlled_vespene_geysers = Units([], self)
        for vespene_geyser in self.bot.vespene_geyser:
            if self.cc.distance_to(vespene_geyser) < self.sphere_of_influence:
                controlled_vespene_geysers.append(vespene_geyser)
        return controlled_vespene_geysers
    
    def build_refinery(self):
        for vespene_geyser in self.vespene:
            worker: Unit =self.bot.select_build_worker(vespene_geyser)
            if worker.build_gas(vespene_geyser):
                return True
            else:
                return False
            
    async def saturateGas(self):
        refineries = self.bot.gas_buildings.ready
        if refineries:
            refinery = refineries.random
            workers = self.workers.random_group_of(2)
            for worker in workers:
                worker.gather(refinery)