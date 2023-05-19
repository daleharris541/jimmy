from sc2.bot_ai import BotAI
from sc2.units import Units
from sc2.ids.unit_typeid import UnitTypeId
from sc2.position import Point2, Point3
from typing import FrozenSet, Set
from loguru import logger


def label_unit(self: BotAI, unit, text):
    # worker = self.workers.by_tag(self.shimmy_the_wonder_SCV)
    green = Point3((0, 255, 0))
    self.client.debug_text_3d(text=text, pos=unit, color=green, size=14)
    # if self.build_order_progress < .05 and self.minerals >30:
    #     unit.move(self.supply_depot_placement_list[0])


# def on_enemy_unit_entered_vision(self, unit: Unit):
# Raise Ramp Wall when enemy detected nearby
# if get_distance(self,self.main_base_ramp.top_center,Unit.position) < 15:
#     for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
#         depot(AbilityId.MORPH_SUPPLYDEPOT_RAISE)
# else:
#     for depot in self.structures(UnitTypeId.SUPPLYDEPOT).ready:
#         depot(AbilityId.MORPH_SUPPLYDEPOT_LOWER)


def draw_building_points(self: BotAI, points: Set[Point2], color: Point3, labels: list, half_vertex_length = 1):
    """
    This function creates green boxes based on points
    It will also draw labels you give it
    We only do this once on start and use that list
    for all future placement until it's empty
    """
    counter = 0
    for p in points:
        p = Point2(p)
        h2 = self.get_terrain_z_height(p)
        pos = Point3((p.x, p.y, h2))
        if len(labels) > 1:
            self.client.debug_text_world(
                text=str(f"{p.x-half_vertex_length},{p.y-half_vertex_length}"),
                pos=pos,
                color=Point3((0, 0, 255)),
                size=16,
            )
            counter += 1
        self.client.debug_box2_out(
            pos, half_vertex_length=half_vertex_length, color=color
        )

    # self.client.debug_box2_out((self.start_location,self.get_terrain_z_height(self.start_location)), half_vertex_length=2.5, color=green)


def draw_expansions(self: BotAI):
    green = Point3((0, 255, 0))
    for expansion_pos in self.expansion_locations_list:
        height = self.get_terrain_z_height(expansion_pos)
        expansion_pos3 = Point3((*expansion_pos, height))
        self.client.debug_box2_out(expansion_pos3, half_vertex_length=1, color=green)


def calc_supply_depot_zones(self: BotAI):
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

    # Since this is fixed, we just need to add the ramp depots first for build order
    for depot in self.main_base_ramp.corner_depots:
        supply_depot_placement_list.append(depot.position)
    # Determine if we are on top or bottom
    # build 5 centered on CC, then match last one and build 5 perpendicular
    direction_vector = get_direction_vector(
        self, self.enemy_start_locations[0], self.start_location
    )
    #distance = get_distance(self, self.start_location, self.enemy_start_locations[0])
    # print(f"Enemy to Me Vector: {direction_vector}") #Output Example: Enemy to Me Vector: (-1.0, 1.0) showing enemy sees us left and above us
    xdirection = round(direction_vector.x)
    ydirection = round(direction_vector.y)
    x = round(self.start_location.x)
    y = round(self.start_location.y)
    # corner is an important point since it is our Corner that is in between us and enemy location
    # we can always add to the multiplier to increase the offset
    corner = Point2((x + (xdirection * -5), y + (ydirection * -5)))
    # supply_depot_placement_list.append(corner)
    # we will now calculate 10 total placement locations, then populate it all into the list
    # supply depots are 2x2 units
    # add 9 supply depots to be symmetrical can not do 11 since placement will be rough
    for coordx in range(corner.x, corner.x + (10 * xdirection), 2 * xdirection):
        supply_depot_placement_list.append(Point2((coordx, corner.y)))
        depot1 = Point2((corner.x + (8 * xdirection),corner.y))
    for coordy in range(corner.y + (-2 * xdirection), corner.y + (10 * ydirection), 2 * ydirection):
        supply_depot_placement_list.append(Point2((corner.x, coordy)))
        depot2 = Point2((corner.x, corner.y + (8 * ydirection)))
    # print(f"This is the point list before drawing: {supply_depot_placement_list}")
    return supply_depot_placement_list, depot1, depot2


def calc_tech_building_zones(self: BotAI, corner_supply_depots: list, building_list: list,):
    """
    This function will create a list of suitable locations for tech buildings
    It will return multiple sets of coordinates in a list
    We only do this once on start and use that list
    for all future placement until it's empty
    """
    tech_buildings_placement_list: Set[Point2] = []
    tech_buildings_placement_list.append(self.main_base_ramp.barracks_in_middle.position)
    # shoot vector towards self.start_location
    direction_vector = get_direction_vector(self,self.start_location, self.main_base_ramp.top_center.position).rounded
    
    starting_height = self.get_terrain_z_height(self.start_location)
    first_depot = corner_supply_depots[0]
    last_depot = corner_supply_depots[1]
    corner_supply_depot: Point2
    if first_depot.y > last_depot.y:
        if direction_vector.y > 0:
            corner_supply_depot = first_depot
        else:
            corner_supply_depot = last_depot
    else:
        if direction_vector.y > 0:
            corner_supply_depot = last_depot
        else:
            corner_supply_depot = first_depot

    #corner_supply_depot = corner_supply_depots[0]
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
    vector_y = round(direction_vector.y)
    vector_x = direction_vector.x
    vg_positions = create_vespene_geyser_points(self)
    print(vg_positions)
    for offset in range(0, spacing * spacing, spacing):
        for axis_y in range(corner_supply_depot.y+(3*round(vector_y)), corner_supply_depot.y + (30 * (round(vector_y))), 3 * (round(vector_y)),):
            temp_point = Point2(((corner_supply_depot.x + (offset * vector_x)), axis_y))
            if not (temp_point in vg_positions or invalid_positions(self, temp_point, starting_height)):
                tech_buildings_placement_list.append(Point2((corner_supply_depot.x + (offset * vector_x), axis_y,)))
                i += 1
    return tech_buildings_placement_list

def invalid_positions(self: BotAI, temp_point: Point2, starting_height: float) -> bool:
    """
    ## Given two Point2 (x,y) locations, validate 3x3 grid for placement \n
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Example: check_placement_tech_buildings(self, temp_point, starting_height)\n
    1. Checks 0,0, 0,3, 3,0, 3,3 from original point\n
    1. If any point is not placeable, returns True\n
    1. If all 4 corners of building pass check, returns False\n
    1. This is how we are making the grid for tech buildings\n
    """
    
    for corner_y in range(0,6,3):
                for corner_x in range(0, 6, 3):
                    if not (self.in_placement_grid(Point2(((temp_point.x)+corner_x, temp_point.y + corner_y))) and
                            self.get_terrain_z_height(Point2(((temp_point.x)+corner_x, temp_point.y + corner_y))) == starting_height):
                        return True   
    return False

def create_vespene_geyser_points(self: BotAI, ):
    """
    ## blah blah blah  \n
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    """
    controlled_vespene_geysers: Set[Point2] = []
    for vespene_geyser in self.vespene_geyser:
        controlled_vespene_geysers
        if self.townhalls.first.distance_to(vespene_geyser) < 8:
            controlled_vespene_geysers.append(vespene_geyser.position.rounded)
    vg_position_collision: Point2 = []
    for g in controlled_vespene_geysers:
        for x in range(g.x-1,g.x+3,1):
            for y in range(g.y-1,g.y+3,1):
                vg_position_collision.append(((x,y)))
    return vg_position_collision

def get_direction_vector(self: BotAI, point1: Point2, point2: Point2):
    """
    Given two Point2 (x,y) locations, return the direction vector
    Example get_direction_vector(self, self.start_location, self.main_base_ramp)
    Example Returns (-1.0, 1.0) as a Point2 tuple showing ramp is left and higher than starting position
    This can be useful for attacking as well and can get vectors all the way to enemy position, etc
    """
    direction_vector = point1.direction_vector(point2)
    point1.distance_to(point2)
    return direction_vector


def get_distance(self: BotAI, point1: Point2, point2: Point2):
    """
    Given two Point2 (x,y) locations, return the distance in units
    Example get_distance(self, self.start_location, self.enemy_start_locations[0])
    Example Returns 115.5 which can be useful to determine how long until enemy shows up at doorstep
    This can be useful for prioritizing defending against enemy attacks
    """
    distance = point1.distance_to_point2(point2)
    return distance
