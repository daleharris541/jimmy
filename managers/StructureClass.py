from tools import closest_point
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.position import Point2, Point3
from typing import Set
from tools.math_ops import get_distance
import tools.logger_levels as l

# Class Structure - 
# Parameters - Building Name, Placement Location, Priority for rebuild/repair
# Variable after built -
# Name, TagOrder received (class instantiated)
# In progress
# Completed build
# Optional:Parameters: , Variable after built - 
# Name, Tag
# Building Destroyed
# Building Damaged
# Change Priority (i.e. Supply Depot for wall-in needs to be priority 0 for repair/rebuild but initially we will send all supply depots with priority 3 for example)

#Structure(self, unit_name, pos, worker )

class Structure:

    def __init__(self, bot: BotAI, building_name, pos: Point2):
        self.bot = bot
        self.pos = pos                              #position where building is originally built
        self.scv = self.get_new_scv()               #upon init, grabbed closest SCV mining
        self.scv_required = True
        self.scv_previous_dist = get_distance(self.scv.position,self.pos)
        self.scv_current_dist = get_distance(self.scv.position,self.pos)
        self.scv_stalled_count = 0
        self.building_name = building_name
        self.tag = None                             #building tag
        self.priority = None
        self.buildstatus = "RECEIVED"               #Received, started, incomplete, completed, damaged, destroyed
        self.no_scv_building = False
        self.damaged = False
        self.debug = False

    async def manage_structure(self):
        """The main function of the Structure class"""
        if self.scv_required == True:
            self.pre_build_phase()
        else:
            if self.buildstatus == "COMPLETED":
                self.completed_building()
            elif self.buildstatus == "DAMAGED":
                self.building_took_damage()
            elif self.buildstatus == "DESTROYED":
                self.building_destroyed()


### Functions for SCVs to build the structure with multiple failures/unforeseen circumstances
    def pre_build_phase(self):
        #l.g.log("BUILD",f"Prebuild Structure: {self.building_name, self.pos}")
        #l.g.log("BUILD", f"Build status: {self.buildstatus}")
        if self.scv in self.bot.workers:
            self.update_scv()
            self.update_distance()
            ### BEHAVIOR ###
            if self.buildstatus == "RECEIVED":
                #if self.building_name not in self.scv.orders():
                    #build structure, doesn't exist right now
                self.scv.build(UnitTypeId[self.building_name],self.pos,can_afford_check=True)
                if self.debug: print(self.scv.orders,self.pos)
                if self.scv_previous_dist == self.scv_current_dist:
                    self.scv_stalled_count += 1
                    if self.debug: print(get_distance(self.scv.position,self.pos))
                    if self.debug: print(self.scv_stalled_count)
                    if self.scv_stalled_count >= 10:
                        #our SCV is stuck somehow, get a new SCV
                        self.scv.stop()
                        self.scv_stalled_count = 0
                        self.scv = self.get_new_scv()
                #Break out of the loop by waiting until a tag is assigned upon construction started
                if self.tag != None:
                    self.buildstatus = "STARTED"
            elif self.buildstatus == "STARTED":
                self.started_building()
            elif self.buildstatus == "INCOMPLETE":
                self.no_scv_building = True
                self.scv = self.get_new_scv()
                pass
        else:
            #one of the boys is dead, get a new SCV assigned
            self.scv_destroyed_during_build()

    def update_distance(self):
        self.scv_previous_dist = self.scv_current_dist
        self.scv_current_dist = get_distance(self.scv.position,self.pos)
    
    def update_scv(self):
        self.scv = self.bot.workers.find_by_tag(self.scv.tag)

    def scv_destroyed_during_build(self):
        #new scv needed if the tag no longer exists in the game, then tell new SCV to continue to build the building
        #if SCV destroyed while en_route, should properly continue
        self.buildstatus == "INCOMPLETE"
        self.no_scv_building = False
        self.scv_stalled_count = 0
        self.scv = self.get_new_scv()
        self.scv.repair(self.bot.structures.find_by_tag(self.tag))

    def get_new_scv(self):
        """
        This function returns a list of all workers sorted by closest and mining of the structure
        """
        #grab closest worker for repair, or build a turret nearby to guard it or bunker
        nearest_worker: Unit = self.pos.closest(self.bot.workers.collecting)
        return nearest_worker
    
    def started_building(self):
        #we have started building this structure
        #track the SCV's progress
        #Assign the Priority
        pass

    def completed_building(self):
        self.scv_required = False

    def building_took_damage(self):
        self.under_attack = True
        #do something to save it?

    def building_destroyed(self):
        #rebuild the building
        self.scv = self.get_new_scv()
        self.scv_required = True
        self.buildstatus = "RECEIVED"
        pass

    def set_priority(self):
        pass
    
    def assign_tag(self, unit: Unit):
        self.tag = unit.tag                         #assigns building tag for this building
    


    # DELETE MemoryError
    # def update_unit_list(units, type):
    # unit_list = []
    # for unit in units:
    #     found = False
    #     if unit[3] == type:
    #         for item in unit_list:
    #             if item['name'] == unit[0]:
    #                 item['quantity'] += 1
    #                 found = True
    #                 break
    #         if not found:
    #             unit_list.append({'name': unit[0], 'quantity': 1})
    # return unit_list
