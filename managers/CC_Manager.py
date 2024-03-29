from tools import closest_point
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units

import tools.logger_levels as l

cc_positions = []
cc_list = []
vespene_workers = [] #you can import this variable and read it from other classes from X import vespene_workers

class CC_Manager:

    def __init__(self, bot: BotAI, townhall: Unit):
        self.bot = bot
        self.townhall = townhall
        self.sphere_of_influence = 10 
        self.max_worker = 16
        self.debug = False
        self.cc = self.townhall #redundant but used in manage_cc class
        #Added Variables
        self.tag = self.cc.tag
        cc_positions.append(self.townhall.position)
        cc_list.append(self)

    async def manage_cc(self):
        """The main function of the CC_Manager that manages the Command Center."""
        ### UPDATE VARIABLES ###
        self.cc = self.bot.structures.find_by_tag(self.townhall.tag) #why does this need to run each time when a CC is created?
        if self.cc.position in self.bot.expansion_locations_list:
            self.workers = self.get_close_workers()
            self.available_minerals = self.get_mineral_fields()
            self.available_vespene = self.get_vespene_geysers()
            self.available_refinerys = self.get_refineries()
        ### BEHAVIOR ###
            if self.cc.name == 'OrbitalCommand':
                self.call_down_mule()

            if len(self.available_refinerys) > 0 and len(self.workers) > 15:
                self.assign_workers_to_refinery()

        else:
            self.cc(AbilityId.LIFT)
            landing_position = closest_point(self.bot.start_location, self.get_expansion_location())
            self.cc(AbilityId.LAND, landing_position)

### Functions for Workers
    def get_close_workers(self):
        """This function returns a list of all workers in range of the Command Center"""
        controlled_worker = Units([], self)
        for worker in self.bot.workers:
            if self.cc.distance_to(worker) < self.sphere_of_influence:
                controlled_worker.append(worker)
        return controlled_worker

    #TODO #27 Only create the worker at the specified Command Center if it's not "full", otherwise create elsewhere
    async def train_worker(self, worker_pool):
        """This function trains workers in the Command Center"""
        if len(self.bot.workers) < worker_pool and len(self.workers) <= self.max_worker and len(self.cc.orders) < 5 and self.cc.is_idle:
            self.cc.train(UnitTypeId.SCV)
            return True
        else:
            return False
    
### Functions for Minerals   
    def get_mineral_fields(self):
        """This function returns the mineral fields in range of the Command Center."""
        controlled_minerals = Units([], self)
        for mineral_field in self.bot.mineral_field:
            if self.cc.distance_to(mineral_field) < self.sphere_of_influence:
                controlled_minerals.append(mineral_field)
        return controlled_minerals

### Functions for Vespene gas  
    def get_vespene_geysers(self):
        """This function returns the unoccupied vespene geysers in range of the Command Center."""
        close_vespene_geysers = Units([], self)
        close_refineries = Units([], self)
        available_vespene_geysers = Units([], self)

        for vespene_geyser in self.bot.vespene_geyser:
            if self.cc.distance_to(vespene_geyser) < self.sphere_of_influence:
                close_vespene_geysers.append(vespene_geyser)

        for refinery in self.bot.gas_buildings:
            if self.cc.distance_to(refinery) < self.sphere_of_influence:
                close_refineries.append(refinery.position)
        
        for cvg in close_vespene_geysers:
            if cvg.position not in close_refineries:
                available_vespene_geysers.append(cvg)
        
        return available_vespene_geysers
            
    def build_refinery(self):
        """This function builds Refinerys in range of the Command Center."""
        if len(self.available_vespene) > 0:
            for vespene_geyser in self.available_vespene:
                worker: Unit = self.bot.select_build_worker(vespene_geyser)
                worker.build_gas(vespene_geyser)
                vespene_workers.append(worker)
                return True
        else:
            return False

    def get_refineries(self):
        """This function returns Refinerys in range of the Command Center."""
        existing_refineries = Units([], self)
        for refinery in self.bot.gas_buildings.ready:
            if self.cc.distance_to(refinery) < self.sphere_of_influence and refinery.has_vespene:
                existing_refineries.append(refinery)
        return existing_refineries

    def assign_workers_to_refinery(self):
        """This function assigns workers to available Refinerys in range of the Command Center."""
        for refinery in self.available_refinerys:
            assigned_workers = refinery.assigned_harvesters
            surplus_workers = assigned_workers - 3
            if assigned_workers < 3 and len(self.workers) > 10:
                worker = self.workers.random
                worker.gather(refinery)
                vespene_workers.append(worker)
            elif surplus_workers != 0:
                for worker in self.workers: #list should only contain workers who are gathering minerals or returning with minerals
                    if worker.order_target == refinery.tag:
                        worker.gather(self.available_minerals.random)
    
### Upgrade CommandCenter
    def upgrade_orbital_command(self):
        """This function upgrades the Command Center to an Orbital Command."""
        #TODO Issue is we no longer check can affords before it gets to this point
        #New build order = ability ID
        if self.cc.is_idle and self.bot.can_afford(UnitTypeId.ORBITALCOMMAND):
            self.cc(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
            return True
        else:
            return False

    def upgrade_planetaryfortress(self):
        """This function upgrades the Command Center to Planetary Fortress."""
        if self.cc.is_idle and self.bot.can_afford(UnitTypeId.PLANETARYFORTRESS):
            self.cc(AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS)
            return True
        else:
            return False

### Abilitys OrbitalCommand
    def call_down_supply(self):
        """This function calls down a Supply Drop to a random Supply Depot."""
        if self.cc.energy > 50:
            closest_supply_depot = self.bot.structures(UnitTypeId.SUPPLYDEPOT).random
            self.cc(AbilityId.SUPPLYDROP_SUPPLYDROP, closest_supply_depot)

    def call_down_mule(self):
        """This function calls down a MULE to the nearest mineral field."""
        if self.cc.energy > 50:
            closest_mineral_field = self.bot.mineral_field.closest_to(self.cc)
            self.cc(AbilityId.CALLDOWNMULE_CALLDOWNMULE, closest_mineral_field)

    def scanner_sweep(self, position):
        """This function scanns at a given location."""
        if self.cc.energy > 50:
            self.cc(AbilityId.SCANNERSWEEP_SCAN, position)

### Expansion Location
    def get_expansion_location(self):
        """This function returns the unoccupied expansion locations."""
        used_positions = []
        all_positions = self.bot.expansion_locations_list
        available_positions = []

        for townhall in self.bot.townhalls:
            used_positions.append(townhall.position)
        
        for pos in all_positions:
            if pos not in used_positions:
                available_positions.append(pos)
  
        return available_positions
    
### Return nearest CC to unit/building/manager
    def return_nearest_cc_position(self, pos):
        return closest_point(pos, cc_positions)