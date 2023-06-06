from tools import closest_point
from tools.draw import label_unit, draw_line_to_target
from managers.CC_Manager import cc_positions, cc_list
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
all_scvs_assigned = []          #we want to add our assigned SCVs to build to this list and make sure they are removed once they are no longer building
all_structures = []

class Structure:

    def __init__(self, bot: BotAI, building_name, pos: Point2):
        self.bot = bot
        self.pos = pos                                      #position where building is originally built
        self.scv = self.get_new_scv()                       #upon init, grabbed closest SCV mining
        self.assigned_cc = closest_point(pos,cc_positions)  #tracks it's nearest CC by position
        self.scv_required = True
        self.scv_already_building = False
        self.scv_previous_dist = get_distance(self.scv.position,self.pos)
        self.scv_current_dist = get_distance(self.scv.position,self.pos)
        self.scv_stalled_count = 0
        self.rallypoint = self.bot.main_base_ramp.bottom_center
        self.rallypoint_set = False
        self.building_name = building_name
        self.tag = None                             #structure tag assigned when started construction
        self.priority = None                        #used to determine if should be repaired
        self.buildstatus = "RECEIVED"               #Received, started, incomplete, completed, damaged, destroyed
        self.scv_not_building = True                 #set to False only when we have issued a build command
        self.damaged = False
        self.debug = True

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
                #if self.building_name not in self.scv.orders():
                if self.scv_not_building:
                    if self.scv_already_building:
                        self.scv.build(UnitTypeId[self.building_name],self.pos,queue=True,can_afford_check=True)
                    else:
                        self.scv.build(UnitTypeId[self.building_name],self.pos,queue=False,can_afford_check=True)
                    self.scv_already_building = True
                    self.scv_not_building = False
                if self.scv_previous_dist == self.scv_current_dist:
                    self.scv_stalled_count += 1
                    if self.scv_stalled_count >= 10:
                        #our SCV is stuck somehow, get a new SCV
                        self.scv.stop()
                        self.scv_stalled_count = 0
                        self.scv_not_building = True
                        self.scv = self.get_new_scv()
            elif self.buildstatus == "INCOMPLETE":
                self.scv_not_building = True
                self.scv = self.get_new_scv()
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
        self.scv_stalled_count = 0              #resets stalled count
        self.scv_not_building = True
        self.scv = self.get_new_scv()
        #self.scv.repair(self.bot.structures.find_by_tag(self.tag))

    def get_new_scv(self):
        """
        This function returns the closest SCV nearest to our target structure position
        Additionally queues up the SCV building something next to it for now
        """
        #grab closest worker for repair, or build a turret nearby to guard it or bunker
        #also consider if it's one of the first 4 buildings to simply queue it up if it's close to finishing
        # random_worker = None
        # # closest_scv = self.pos.closest(self.bot.workers)
        # # #get all buildings being built and progress towards finishing, see if we can match up that building tag with structure and SCV tag
        # # for structure in all_structures:            #get all in_progress/being built structures
        # #     if closest_scv.tag == structure.tag:    #if the SCV we grabbed is the closest
        # #         random_worker = closest_scv
        # if random_worker is None:
        #     all_scvs_mining = []
        #     for cc in cc_list:
        #         all_scvs_mining += cc.mineral_workers
        #     random_worker = self.pos.closest(all_scvs_mining)   #pick the closest one from the mining list
        #     while random_worker in all_scvs_assigned:           #if the scv is already assigned to build something else, pick a new one
        #         random_worker: Unit = self.pos.closest(all_scvs_mining)
        # all_scvs_assigned.append(random_worker)
        nearest_worker: Unit = self.pos.closest(self.bot.workers)
        all_scvs_assigned.append(nearest_worker)
        return nearest_worker
    
    def started_building(self, unit):
        #we have started building this structure
        #track the SCV's progress
        #Assign the Priority
        l.g.log("BUILD",f"I've received confirmation that {self.building_name} has started")
        all_structures.append(unit)
        self.buildstatus = "STARTED"

    def completed_building(self, rallypoint: Point2):
        """
        This function takes one parameter of a Point2 on rally point target
        If None is sent over, then it uses the default of main base ramp bottom
        """
        self.scv_required = False
        self.scv = None
        self.buildstatus = "COMPLETED"
        all_structures.remove(self)
        #if building produces units, then rally to bottom of ramp for now
        structure = self.bot.structures.find_by_tag(self.tag)
        if self.rallypoint_set == False:
            if self.debug:l.g.log("BUILD",f"Setting rally point for {self.building_name}")
            structure(AbilityId.RALLY_BUILDING,self.rallypoint)
            self.rallypoint_set = True


    def building_took_damage(self):
        self.scv_required = True
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
