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
        self.scv = self.get_new_scv()
        self.scv_required = True
        self.scv_previous_dist = get_distance(self.scv.position,self.pos)
        self.scv_current_dist = get_distance(self.scv.position,self.pos)
        self.scv_stalled_count = 0
        self.building_name = building_name
        self.tag = None
        self.priority = None
        self.buildstatus = "RECEIVED"               #Received, started, incomplete, completed, damaged, destroyed
        self.no_scv_building = False
        self.damaged = False
        self.debug = True

    async def manage_structure(self):
        """The main function of the Structure class"""
        ### UPDATE VARIABLES ###
        self.scv = self.bot.workers.find_by_tag(self.scv.tag)
        self.scv_previous_dist = self.scv_current_dist
        self.scv_current_dist = get_distance(self.scv.position,self.pos)
        #self.tag = self.scv.orders[0]
        #if SCV doesn't show up in list of workers, it's dead, so don't do anything to cause crashing
        if self.scv in self.bot.workers and self.scv_required == True:
            ### BEHAVIOR ###
            if self.buildstatus == "RECEIVED":
                #build structure, doesn't exist right now
                
                self.scv.build(UnitTypeId[self.building_name],self.pos,can_afford_check=False)
                

                l.g.log("BUILD", f"We are in RECEIVED STATUS and SCV is {self.scv_current_dist} units away")
                #print(self.scv.orders[0],self.tag)
                if self.scv_previous_dist == self.scv_current_dist:
                    self.scv_stalled_count += 1
                    print(self.scv_stalled_count)
                    l.g.log("BUILD","Stalled worker!!!")
                    if self.scv_stalled_count >= 10:
                        #our SCV is no longer coming, get a new SCV
                        self.scv.stop
                        self.scv_stalled_count = 0
                        self.scv = self.get_new_scv()
                if self.tag != None:
                    self.buildstatus = "STARTED"
            elif self.buildstatus == "STARTED":
                #assign the tag of the structure to the class
                l.g.log("BUILD","Celebrate if you got here")
                pass
            elif self.buildstatus == "INCOMPLETE":
                pass
        else:
            #he's dead, get a new SCV assigned
            self.scv = self.get_new_scv()
            self.scv_stalled_count = 0
        if self.buildstatus == "COMPLETED":
            self.scv_required = False
            pass
        elif self.buildstatus == "DAMAGED":
            pass
        elif self.buildstatus == "DESTROYED":
            pass


### Functions for SCVs to build the structure with multiple failures/unforeseen circumstances
    def get_new_scv(self):
        """
        This function returns a list of all workers in range of the structure
        """
        #grab closest worker for repair, or build a turret nearby to guard it or bunker
        nearest_worker: Unit = self.pos.closest(self.bot.workers.collecting)
        return nearest_worker
    
    def scv_destroyed_during_build(self):
        pass

    def started_building(self):
        #we have started building this structure
        #track the SCV
        #assign the tag to self assign the variable
        pass

    def building_took_damage(self):
        self.under_attack = True
        #do something

    def building_destroyed(self):
        #rebuild the building if it's proper priority
        pass

    def set_priority(self):
        pass
    
    def assign_tag(self, unit: Unit):
        self.tag = unit.tag


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
