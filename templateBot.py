import random
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.ability_id import AbilityId
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2, Point3
from sc2.unit import Unit
from sc2.units import Units
from typing import FrozenSet, Set
from loguru import logger
from managers.BuildManager import get_build_order, compare_dicts, build_structure, build_addon
from managers.ArmyManager import train_unit
from managers.CC_Manager import CC_Manager
from managers.UpgradeManager import research_upgrade
from managers.ControlHelper import idle_workers

#https://burnysc2.github.io/python-sc2/docs/text_files/introduction.html

class Jimmy(BotAI):
    
    #following variables from bot.py from smoothbrain bot as example
    def __init__(self):
        self.unit_command_uses_self_do = False
        self.distance_calculation_method = 2
        self.game_step: int = 2                      # 2 usually, 6 vs human
        self.build_starport_techlab_first = True     # always make techlab first on starport, good against dts, skytoss, burrowed roaches, and siege tanks
        self.worker_rushed = False                   # tells if we are worker rushed, if the enemies were repelled we should close the wall quick before they come back
        self.out_of_fight_workers = []               # workers with too low hp to defend a worker rush
        self.scouting_units = []                     # lists units assigned to scout so that we do not cancel their orders
        self.worker_assigned_to_repair = {}          # lists workers assigned to repair
        self.worker_assigned_to_follow = {}          # lists workers assigned to follow objects (used to prevent Planetary Fortress rushes)
        self.worker_assigned_to_defend = {}          # lists workers assigned to defend other workers during construction
        self.worker_assigned_to_resume_building = {} # lists workers assigned to resume the construction of a building
        self.worker_assigned_to_expand = {}          # lists workers assigned to expand /!\ not used yet
        self.worker_assigned_to_premove = {}         # list worker assigned to pre-move to next build item in the order
        self.townhall_saturations = {}               # lists the mineral saturation of townhalls in queues of 40 frames, we consider the townhall saturated if max_number + 1 >= ideal_number
        self.refineries_age = {}                     # this is here to tackle an issue with refineries having 0 workers on them when finished, although the building worker is assigned to it
        self.lifted_cc_pos = {}                      # remember where lifted ccs were
        self.scouted_at_time = -1000                 # save moment at which we scouted, so that we don't re-send units every frame
        self.buildstep = 0
        self.worker_pool = 12
        self.cc_managers = []
        self.build_order_progress = 0
        self.build_order_count = 0
        self.supply_depot_placement_list: Set[Point2] = []
        self.tech_buildings_placement_list: Set[Point2] = []
        self.build_order = get_build_order(self,'16marinedrop-example')    #    16marinedrop-example or debug
        self.debug = True
        self.normal_buildings = ['BARRACKS','STARPORT','ENGINEERINGBAY','FACTORY']
        self.building_list = []


    async def on_start(self):
        #print("Game started")
        #Load build manager once and print once##
        if self.build_order.count != 0:
            print("successfully loaded build order:")
            print(self.build_order)
        else:
            print("Build order failed to load")
        self.build_order_count = len(self.build_order)
        print(f"Ramp = {self.main_base_ramp}")
        print(f"Start Location = {self.start_location}")
        print(f"Enemy Location = {self.enemy_start_locations[0]}")
        worker = self.select_build_worker(self.start_location.position)
        self.shimmy_the_wonder_SCV = worker.tag
        self.supply_depot_placement_list: Set[Point2] = calc_supply_depot_zones(self)
        for item in self.build_order:
            if "structure" in item:
                if item[0] in self.normal_buildings:
                    self.building_list.append(item[0])
        print(f"Building List Count: {len(self.building_list)}")
        print(self.building_list)
        self.tech_buildings_placement_list: Set[Point2] = calc_tech_building_zones(self, self.supply_depot_placement_list[2], self.building_list)
        #worker.move(self.supply_depot_placement_list[0])

        #self.worker_assigned_to_premove.add(worker)
        #print(self.worker_assigned_to_premove)
        #add supply depots for ramp for 1st and 2nd Depots to be built
        #self.supply_depot_placement_list#[Point2] = self.main_base_ramp.corner_depots[0]

    async def on_step(self, iteration: int):
        #first check is to look for enemy units
        #await self.on_enemy_unit_entered_vision(Unit)
        # Find all Command Centers
        cc_list = self.townhalls
        # Create a new CC_Manager instance for each Command Center if it doesn't already exist
        for cc in cc_list:
            if not any(cc_manager.townhall.tag == cc.tag for cc_manager in self.cc_managers):
                cc_manager = CC_Manager(self, cc)
                self.cc_managers.append(cc_manager)

        # Call the manage_cc function for each CC_Manager instance
        for cc_manager in self.cc_managers:
            if cc_manager.townhall.tag not in self.townhalls.tags:
                self.cc_managers.remove(cc_manager)
            else:
                await cc_manager.manage_cc(self.worker_pool)

        await idle_workers(self)

        if self.debug:
            green = Point3((0, 255, 0))
            red = Point3((0,0,255))
            blue = Point3((255,0,0))
            self.client.debug_text_screen(text=str(self.build_order[0]), pos=Point2((0, 0)), color=green, size=18)
            #properly send each item in the build order for tech buildings
            self.draw_building_points(self.supply_depot_placement_list, green, ['depot'])
            self.draw_building_points(self.tech_buildings_placement_list, red, self.building_list)
            self.draw_expansions()

        # We want to be able to quickly respond to enemy attack:
        # This is like the limbic system, it can quickly take over if we are in danger
        # Otherwise, let the frontal lobe do all the work

        # Perhaps we can initiate this into a function call when an enemy is detected
        # instead of always doing this code + responding with attacking with nearby units
        # We can do this by having a ramp location instead
        
        if len(self.build_order) > 0:
            if await build_next(self, self.build_order[self.buildstep], self.cc_managers, self.supply_depot_placement_list, self.tech_buildings_placement_list):
                #TODO: keep this code until the check against the current buildings is finished
                self.build_order.pop(self.buildstep) #remove item from the list once it's done
                self.buildstep += 1
                self.build_order_progress = (self.build_order_count-len(self.build_order))
                if self.debug:
                        buildOrderPercentage = 100 * ((self.build_order_count-len(self.build_order))/self.build_order_count)
                        print(f"Build Step: {self.build_order_progress} Total Steps Remaining:{len(self.build_order)}")
                        print("Percentage of build order completed: %.2f%%" % (buildOrderPercentage))
                        #await self.label_unit(self.shimmy_the_wonder_SCV, "Shimmy")
        
        #await compare_dicts(self, self.build_order, self.buildstep) #debug

    # async def on_end(self):
    #     print("Game ended.")
        # Do things here after the game ends
        
    async def label_unit(self, unit, text):
        #worker = self.workers.by_tag(self.shimmy_the_wonder_SCV)
        green = Point3((0, 255, 0))
        self.client.debug_text_3d(text=text, pos=unit, color=green, size=14)
        # if self.build_order_progress < .05 and self.minerals >30:
        #     unit.move(self.supply_depot_placement_list[0])

    #def on_enemy_unit_entered_vision(self, unit: Unit):
        # Raise Ramp Wall when enemy detected nearby
        # if get_distance(self,self.main_base_ramp.top_center,Unit.position) < 15:
        #     for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
        #         depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)
        # else:
        #     for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
        #         depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)
            
    def draw_building_points(self, points : Set[Point2], color : Point3, labels : list):
        counter = 0
        print(f"Count of points being sent: {len(points)}")
        print(f"Length of buildings list {len(labels)}")
        for p in points:
            p = Point2(p)
            h2 = self.get_terrain_z_height(p)
            pos = Point3((p.x, p.y, h2))
            if len(labels) > counter-1:
                self.client.debug_text_world(text=labels[counter],pos=pos,color=Point3((0,0,255)),size=16)
                counter += 1
            else:
                self.client.debug_text_world(text='Depot',pos=pos,color=Point3((0,0,255)),size=16)
            self.client.debug_box2_out(pos + Point2((0.5, 0.5)), half_vertex_length=0.5, color=color)

        #self.client.debug_box2_out((self.start_location,self.get_terrain_z_height(self.start_location)), half_vertex_length=2.5, color=green)

    def draw_expansions(self):
        green = Point3((0, 255, 0))
        for expansion_pos in self.expansion_locations_list:
            height = self.get_terrain_z_height(expansion_pos)
            expansion_pos3 = Point3((*expansion_pos, height))
            self.client.debug_box2_out(expansion_pos3, half_vertex_length=0.5, color=green)

#function to later move somewhere else
async def build_next(self: BotAI, buildrequest, cc_managers, sd_pos, tech_pos):
    unit_name, unitId, unitType, supplyRequired, gametime, frame = buildrequest
    #example for how to read time target and execution:
    #Target time for 2nd SCV to be queued to build - 12 seconds. Actual execution in game time: 8 seconds (Ahead)
    #if self.debug:
        #print("Unit Name: SupplyRequired : Supply Used: Target Time - " + str(gametime) + ": Current Minerals")
        #print(unit_name + "          " + str(supplyRequired) + "             " + str(self.supply_used) + "           " + (str(self.time)).split(".")[0] + "        " + str(self.minerals))
    #logger.info(f"Executing at {self.time} - Step Time = {gametime}")
    #would be cool to subtract the timing of the build based on actual and show ahead or behind

    if unitType == 'action':
        #skip actions
        return True
    elif unitType == 'upgrade':
        await research_upgrade(self, unit_name)
        return True
    #elif unitType == 'unit':
    #    return True
    if self.can_afford(UnitTypeId[unit_name]) and self.tech_requirement_progress(UnitTypeId[unit_name]) == 1:
        if unitType == 'structure':
            if unit_name == 'REFINERY':
                cc_managers[0].build_refinery()
                return True
            elif unit_name == 'ORBITALCOMMAND':
                cc_managers[0].upgrade_orbital_command()
                return True
            elif "TECHLAB" in unit_name or "REACTOR" in unit_name:
                if await build_addon(self, unit_name):
                    return True
                else:
                    return False
            elif unit_name == "SUPPLYDEPOT":
                if await build_structure(self, unit_name,sd_pos[0]): 
                    return True
                else:
                    return False
            else:
                if await build_structure(self, unit_name, tech_pos): #building placement logic missing
                    return True
                else:
                    return False
        elif unitType == 'unit':
            #skip unit training
            return True
        elif unitType == 'worker':
            await cc_managers[0].train_worker(70)
            return True

def calc_supply_depot_zones(self : BotAI):
    """
    This function will create a list of suitable locations for supply depots
    It will return multiple sets of coordinates in a list
    We only do this once on start and use that list
    for all future placement until it's empty
    """
    supply_depot_placement_list: Set[Point2] = []
        #               24 is max supply depots needed to build with zero CC expansions
        # Below is advice from Reddit on proper supply depot placement we can do later
        # Based on enemy race
        #     TVZ:

        # You'd want to wall your ramp & your natural. After that vision is important, but try to minimize
        # travel distance for SCVs. You can wall your third, on certain maps I like to do it, but not if it costs
        # like 8 depots to wall off. Some pros even do it even when it takes a lot of depots,
        # so it's not neccesarily wrong to do it, more of a personal preference.

        #     TVT:

        # On 2 player maps I like to build the first depot at the ramp, so you can spot for reaper allins.
        # If you later find out your opponent is massing hellions For GG style, build 2 more depots.

        # After that I build depots as close to my mineral line as possible, as that's simply the most efficient
        # economy-wise. If you don't see a banshee @ 7:00 I build ~2 depots at the edges 
        # (just enough to give you vision) to spot for doomdrops/marine hellion medivac builds.

        #     TVP:

        # On 2 player maps the same as TVT, first depot at the ramp, so you can 100% of the time see a probe 
        # enter your base. It's not perfectly efficient but you're pretty much immune to inbase proxy 2 gate.
        # After that build them as close to your mineral line as possible.

    #print("I'm getting the set of Supply Depot placement locations")
    #Since this is fixed, we just need to add the ramp depots first for build order
    for depot in self.main_base_ramp.corner_depots:
        supply_depot_placement_list.append(depot.position)
    #Determine if we are on top or bottom
    #build 5 centered on CC, then match last one and build 5 perpendicular
    direction_vector = get_direction_vector(self, self.enemy_start_locations[0], self.start_location)
    distance = get_distance(self,self.start_location,self.enemy_start_locations[0])
    #print(f"Enemy to Me Vector: {direction_vector}") #Output Example: Enemy to Me Vector: (-1.0, 1.0) showing enemy sees us left and above us
    xdirection = round(direction_vector.x)
    ydirection = round(direction_vector.y)
    x = round(self.start_location.x)
    y = round(self.start_location.y)
    #corner is an important point since it is our Corner that is in between us and enemy location
    #we can always add to the multiplier to increase the offset
    corner = Point2((x+(xdirection*-5),y+(ydirection*-5)))
    #supply_depot_placement_list.append(corner)
    #we will now calculate 10 total placement locations, then populate it all into the list
    #supply depots are 2x2 units
    #add 9 supply depots to be symmetrical can not do 11 since placement will be rough
    for coordx in range(corner.x,corner.x+(10*xdirection),2*xdirection):
        supply_depot_placement_list.append(Point2((coordx,corner.y)))
    for coordy in range(corner.y+(-2*xdirection),corner.y+(10*ydirection),2*ydirection):
        supply_depot_placement_list.append(Point2((corner.x,coordy)))
    #print(f"This is the point list before drawing: {supply_depot_placement_list}")
    return supply_depot_placement_list


def calc_tech_building_zones(self : BotAI, corner_supply_depot : Point2, building_list):
    """
    This function will create a list of suitable locations for tech buildings
    It will return multiple sets of coordinates in a list
    We only do this once on start and use that list
    for all future placement until it's empty
    """
    tech_buildings_placement_list: Set[Point2] = []
    tech_buildings_placement_list.append(self.main_base_ramp.barracks_correct_placement.position)
    #shoot vector towards self.start_location
    direction_vector = get_direction_vector(self,self.main_base_ramp.top_center.position,self.start_location).rounded
    # #tech buildings footprint 5x5 with 2x2 "lane"
    # #Only placement in columns with buildings for addon purposes
    # #TODO #21 Barracks are 3x3 + addon = 
    # spacing represents the building + addon + 2x2 for a "lane"
    # can't do a ton of rows, but can do a lot stacked along Y axis (column)
    # so spacing is how far the distance will be between 5 buildings stacked in a column
    # if we send the build order queue to this function, we can swap out the BARRACKS for actual building
    # Then it can iterate through and properly place our build order items if structure in the matrix
    # properly allowing for size and custom making the grid match the build order and just increment the build order step
    spacing = 5
    i = 0
    for offset in range(spacing,spacing*spacing,spacing):
        for axis_y in range(corner_supply_depot.y,corner_supply_depot.y+(15*(round(direction_vector.y))),3*(round(direction_vector.y))):
            if self.can_place_single(UnitTypeId[building_list[i]],Point2((corner_supply_depot.x+(-1*offset*direction_vector.x),axis_y))):
                tech_buildings_placement_list.append(Point2((corner_supply_depot.x+(-1*offset*direction_vector.x),axis_y)))
                i += 1
                if i-1 == len(building_list)-1:
                    return tech_buildings_placement_list
    return tech_buildings_placement_list

def get_direction_vector(self, point1 : Point2, point2 : Point2):
    """
    Given two Point2 (x,y) locations, return the direction vector
    Example get_direction_vector(self, self.start_location, self.main_base_ramp)
    Example Returns (-1.0, 1.0) as a Point2 tuple showing ramp is left and higher than starting position
    This can be useful for attacking as well and can get vectors all the way to enemy position, etc
    """
    direction_vector = point1.direction_vector(point2)
    point1.distance_to(point2)
    return direction_vector

def get_distance(self, point1 : Point2, point2 : Point2):
    """
    Given two Point2 (x,y) locations, return the distance in units
    Example get_distance(self, self.start_location, self.enemy_start_locations[0])
    Example Returns 115.5 which can be useful to determine how long until enemy shows up at doorstep
    This can be useful for prioritizing defending against enemy attacks
    """
    distance = point1.distance_to_point2(point2)
    return distance

def main():
    run_game(
        maps.get("AcropolisLE"),
        [Bot(Race.Terran, Jimmy()), Computer(Race.Zerg, Difficulty.Easy)],
        realtime=True,
    )

if __name__ == "__main__":
    main()