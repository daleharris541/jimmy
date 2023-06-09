from tools import closest_point
from tools.draw import label_unit, draw_line_to_target
from managers.CC_Manager import cc_positions, cc_list
from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units
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
all_scvs_assigned = []          #we want to add our assigned SCVs to build to this list and make sure they are removed once they are no longer building
all_structures = []             #all structures in this list will exist only until they are completely built
structure_list = []

class Structure:

    def __init__(self, bot: BotAI, building_name, pos: Point2,is_townhall=False,townhall=None):
        """
        This class is instantiated per building to enable tracking from Jimmy.py
        """
        ### Structure Related Variables ###
        self.bot = bot                                      #ensure we can still see bot information
        self.pos = pos                                      #position where building is originally built
        self.unit: Unit = None
        self.building_name = building_name                  #set the name
        self.tag = None                                     #structure tag assigned when construction starts
        self.priority = None                                #used to determine if should be repaired/rebuilt or wait for others
        self.damaged = False                                #status for damage allowing for repair
        self.buildstatus = "RECEIVED"                       #Received, started, incomplete, completed, damaged, destroyed
        self.incomplete_no_scv = False                      #same way we can see an incomplete building where SCV has been killed

        ### SCV Related Variables ###
        self.scv = self.get_new_scv()                       #upon init, grabbed closest SCV mining
        self.scv_required = True                            #a building requires an SCV before and during construction                    
        self.scv_building_other = False                     #set to True when an SCV is building another structure           
        self.scv_previous_dist = None
        self.scv_current_dist = None
        self.scv_stalled_count = 0                          #if SCV is stuck or sits still, will eventually pick new SCV
        self.scv_queued_to_build = False                    #set to True when build command is queued
        self.scv_is_not_repairing = True                    #default, changes when SCV assigned to repair

        ### Unit Creation Variables
        self.rallypoint = self.bot.main_base_ramp.bottom_center
        self.rallypoint_set = False
        
        ### Misc Variables ###
        self.debug = True
        if is_townhall:
            self.buildstatus = "COMPLETED"
            self.building_name = "COMMANDCENTER"
            self.tag = townhall.tag
            self.pos = townhall.position
            self.unit = townhall
            self.scv_required = False

    async def manage_structure(self):
        """The main function of the Structure class"""
        if self.scv_required:
            if self.debug:
                label_unit(self.bot,self.scv, self.building_name)
                draw_line_to_target(self.bot, self.scv, self.pos)
            await self.pre_build_phase()
            

### Functions for SCVs to build the structure with multiple failures/unforeseen circumstances
    async def pre_build_phase(self):
        #l.g.log("BUILD",f"Prebuild Structure: {self.building_name, self.pos}")
        #l.g.log("BUILD", f"Build status: {self.buildstatus}")
        if self.scv in self.bot.workers:
            self.update_scv()
            self.update_distance()
            ### BEHAVIOR ###
            if self.buildstatus == "RECEIVED":

                if self.scv_building_other == False and self.scv_queued_to_build == False:
                    self.scv.build(UnitTypeId[self.building_name],self.pos,queue=False)
                elif self.scv_building_other and self.scv_queued_to_build == False:
                    self.scv.build(UnitTypeId[self.building_name],self.pos,queue=True)
                
                self.scv_queued_to_build = True
                await self.stall_check()

            elif self.buildstatus == "INCOMPLETE":
                self.incomplete_no_scv = True
                self.buildstatus == "RECEIVED"
                self.scv = self.get_new_scv()
        else:
            #one of the boys is dead, get a new SCV assigned
            self.scv_destroyed_during_build()

    def update_distance(self):
        self.scv_previous_dist = self.scv_current_dist
        if self.bot.workers.find_by_tag(self.scv.tag) is not None:
            self.scv_current_dist = get_distance(self.scv.position,self.pos)
    
    def update_scv(self):
        alive_worker = self.bot.workers.find_by_tag(self.scv.tag)
        if alive_worker is None:
            self.scv = self.get_new_scv()
    
    async def stall_check(self):
        if self.scv_previous_dist == self.scv_current_dist:
            self.scv_stalled_count += 1
            if self.scv_stalled_count >= 10:
                self.scv.stop()
                self.scv_stalled_count = 0
                self.scv_not_building = True
                self.scv = self.get_new_scv()

    def scv_destroyed_during_build(self):
        #new scv needed if the tag no longer exists in the game, then tell new SCV to continue to build the building
        #if SCV destroyed while en_route, should properly continue
        self.buildstatus == "INCOMPLETE"
        self.scv_stalled_count = 0              #resets stalled count
        self.scv_not_building = True
        self.scv_queued = False
        self.scv = self.get_new_scv()

    def get_new_scv(self, priority = None):
        """
        This function returns the closest SCV nearest to our target structure position
        Additionally queues up the SCV if it's already building and past 90% completion
        """
        #grab closest worker for repair, or build a turret nearby to guard it or bunker
        #also consider if it's one of the first 4 buildings to simply queue it up if it's close to finishing
        # random_worker = None
        # # closest_scv = self.pos.closest(self.bot.workers)
        # # #get all buildings being built and progress towards finishing, see if we can match up that building tag with structure and SCV tag
        # # for structure in all_structures:            #get all in_progress/being built structures
        # #     if closest_scv.tag == structure.scv.tag:    #if the SCV we grabbed is the closest
        # #         random_worker = closest_scv
        # if random_worker is None:
        #     all_scvs_mining = []
        #     for cc in cc_list:
        #         all_scvs_mining += cc.mineral_workers
        #     random_worker = self.pos.closest(all_scvs_mining)   #pick the closest one from the mining list
        #     while random_worker in all_scvs_assigned:           #if the scv is already assigned to build something else, pick a new one
        #         random_worker: Unit = self.pos.closest(all_scvs_mining)
        # all_scvs_assigned.append(random_worker)
       
        selected_worker = None
        potential_list = []
        potential_list.append(self.pos.closest(self.bot.workers)) #selects a single SCV
        for objects in all_structures:
            if self.bot.structures.find_by_tag(objects[0].tag).build_progress >= .9:
                potential_list.append(objects[1])
        for worker in self.bot.workers.collecting:
            potential_list.append(worker)
        selected_worker = self.pos.closest(potential_list)
        if selected_worker in all_scvs_assigned:
            self.scv_building_other = True
        else:
            all_scvs_assigned.append(selected_worker)
        return selected_worker
    
    ### These functions get kicked off when async bot functions hit Jimmy
    def started_building(self, unit):
        #we have started building this structure
        #track the SCV's progress
        #Assign the Priority
        l.g.log("BUILD",f"I've received confirmation that {self.building_name} has started")
        all_structures.append([unit, self.scv])
        print(all_structures)
        self.unit = unit
        if get_distance(self.pos,self.bot.main_base_ramp.top_center) < 2:
            self.set_priority(0)
        self.buildstatus = "STARTED"

    def completed_building(self, unit: Unit):
        """
        This function takes one parameter of a Point2 on rally point target
        If None is sent over, then it uses the default of main base ramp bottom
        """
        all_structures.remove([unit, self.scv])
        all_scvs_assigned.remove(self.scv)
        self.scv_required = False
        self.scv = None
        self.buildstatus = "COMPLETED"
        self.set_rallypoint(self.rallypoint)


    def building_took_damage(self):
        if self.debug:l.g.log("BUILD",f"Structure {self.building_name} took damage!")
        self.scv_required = True
        self.under_attack = True
        self.health_percentage = self.unit.health
        
        if self.scv_is_not_repairing:
            self.scv = self.get_new_scv()
            self.scv.repair(self.unit)
            if self.bot.structures.find_by_tag(self.tag).health:
                self.scv_is_not_repairing = False

    def building_destroyed(self, priority = None):
        #rebuild the building
        self.scv = self.get_new_scv()
        self.scv_required = True
        self.buildstatus = "RECEIVED"

    def set_priority(self, priority: int):
        if priority is int:
            self.priority = priority
            return True
        else:
            return False
    
    def assign_tag(self, unit: Unit):
        self.tag = unit.tag                         #assigns building tag for this building

    def set_rallypoint(self, rallypoint: Point2):
        self.rallypoint = rallypoint
        self.unit(AbilityId.RALLY_BUILDING,self.rallypoint)

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
