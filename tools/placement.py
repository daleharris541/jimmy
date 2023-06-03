from sc2.bot_ai import BotAI
from sc2.position import Point2
from sc2.units import UnitTypeId
from typing import Set

def placement_positions(self: BotAI):
    direction_vector = get_direction_vector(self.start_location, self.main_base_ramp.top_center.position) #self.main_base_ramp.barracks_in_middle
    start_position = self.start_location

    base_offset = 4.5
    starting_point = Point2((int(start_position.x + (round(direction_vector.x) * base_offset)), start_position.y + (round(direction_vector.y) * base_offset)))

    return direction_vector, starting_point

def depot_positions(self: BotAI):
    depot_placements: Set[Point2] = []
    direction_vector, starting_point = placement_positions(self)
    offsets = [2, 4, 6, 8, 10, 12, 14]

    for depot in self.main_base_ramp.corner_depots:
        depot_placements.append(depot)

    depot_placements.append(starting_point)

    for offset in offsets:
        depot_placements.append(Point2((int(starting_point.x + (offset * -direction_vector.x)), int(starting_point.y))))
        depot_placements.append(Point2((int(starting_point.x), int(starting_point.y + (offset * -direction_vector.y)))))
    
    return depot_placements

def building_positions(self: BotAI):
    building_placements: Set[Point2] = []
    direction_vector, starting_point = placement_positions(self)
    inverse_starting_point = Point2((starting_point.x + (9 *(-direction_vector.x)), starting_point.y + (9 *(-direction_vector.y))))
    starting_height = self.get_terrain_z_height(self.start_location)
    y_offsets = [0, 3, 6, 9, 12, 15, 18, 21, 24]
    x_spacing = [0, 6, 12, 18, 24]

    building_placements.append(self.main_base_ramp.barracks_correct_placement)
    vg_positions = create_vespene_geyser_points(self)

    for space in x_spacing:
        for offset in y_offsets:
            point = Point2((int(inverse_starting_point.x + (space * direction_vector.x)), int(inverse_starting_point.y + (offset * direction_vector.y))))
            if not (point in vg_positions or invalid_positions(self, point, starting_height)):
                building_placements.append(point)

    valid_placements = filter_points(Point2((starting_point.x + (1 * direction_vector.x), starting_point.y+ (1 * direction_vector.y))), Point2((-direction_vector.x, -direction_vector.y)), building_placements)
    return valid_placements

def filter_points(reference_point: Point2, vektor: Point2, points: Set[Point2]):
    invalid_placements: Set[Point2] = []

    for point in points:
        diff_vector = Point2((point.x - reference_point.x , point.y - reference_point.y))

        if (diff_vector.x * vektor.x) > 0 and (diff_vector.y * vektor.y) > 0:
            invalid_placements.append(point)

    new_placements: Set[Point2] = [pos for pos in points if pos not in invalid_placements]

    return new_placements

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
        supply_depot_placement_list.append(depot)
    
    # direction vector to point from enemy back to our CC
    # Enemy to Me Vector: (-1.0, 1.0) showing enemy sees us left and above us
    direction_vector = get_direction_vector(self.enemy_start_locations[0], self.start_location)
    xdirection = round(direction_vector.x)
    ydirection = round(direction_vector.y)
    x = self.start_location.x+(-2.5*xdirection)
    y = self.start_location.y+(-2.5*ydirection)

    offset_space = -1 #this is the offset around the command center
    corner = Point2(( x + (xdirection * offset_space), y + (ydirection * offset_space) ))
    # add 9 supply depots to be symmetrical can not do 11 since placement will be rough
    cornerx = int(corner.x)
    cornery = int(corner.y)
    for coordx in range(cornerx + (2 * xdirection), cornerx + (10 * xdirection), 2 * xdirection):
        supply_depot_placement_list.append(Point2((coordx, cornery)))
    for coordy in range(cornery, cornery + (10 * ydirection), 2 * ydirection):
        supply_depot_placement_list.append(Point2((cornerx, coordy)))
    return supply_depot_placement_list

def calc_tech_building_zones(self: BotAI, corner_supply_depot: list):
    """
    This function will create a list of suitable locations for tech buildings
    It will return multiple sets of coordinates in a list
    We only do this once on start and use that list
    for all future placement until it's empty
    """
    tech_buildings_placement_list: Set[Point2] = []
    tech_buildings_placement_list.append(self.main_base_ramp.barracks_correct_placement)
    # shoot vector towards self.start_location
    direction_vector = get_direction_vector(self.start_location, self.main_base_ramp.top_center.position)
    vector_y = round(direction_vector.y)
    vector_x = round(direction_vector.x)

    starting_height = self.get_terrain_z_height(self.start_location)

    spacing = 6
 
    vg_positions = create_vespene_geyser_points(self)
    #builds left to right/right to left
    for offset in range(0, spacing * spacing, spacing):
        for axis_y in range(corner_supply_depot.y+(3*vector_y), corner_supply_depot.y + (18 * vector_y), 3 * vector_y):
            hpoint = Point2(((corner_supply_depot.x + (-offset * vector_x)), axis_y))
            if not (hpoint in vg_positions or invalid_positions(self, hpoint, starting_height)):
                tech_buildings_placement_list.append(hpoint)
    
    #builds bottom to top/top to bottom
    for offset in range(3, spacing * spacing, spacing):
        for axis_y in range(corner_supply_depot.y+(-3*vector_y), corner_supply_depot.y + (-18 * vector_y), -3 * vector_y):
            vpoint = Point2(((corner_supply_depot.x + (offset * vector_x)), axis_y))
            if not (vpoint in vg_positions or invalid_positions(self, vpoint, starting_height)):
                tech_buildings_placement_list.append(vpoint)
    
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
    corners = temp_point.neighbors4
    for point in corners:
        point = Point2((point))
        if not (self.game_info.pathing_grid[point] == 1 and self.get_terrain_z_height(point) == starting_height):
            return True
    return False

def create_vespene_geyser_points(self: BotAI):
    """
    ## Creates a set of points representing Vespene Geysers  \n
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    - Returns a list of positions that will be collision checks
    - For building our tech building layout
    """
    controlled_vespene_geysers: Set[Point2] = []
    for vespene_geyser in self.vespene_geyser:
        controlled_vespene_geysers
        if self.townhalls.first.distance_to(vespene_geyser) < 8:
            controlled_vespene_geysers.append(vespene_geyser.position.rounded)
    vg_position_collisions: Point2 = []
    for g in controlled_vespene_geysers:
        for x in range(g.x-1,g.x+3,1):
            for y in range(g.y-1,g.y+3,1):
                vg_position_collisions.append(((x,y)))
    return vg_position_collisions

def get_direction_vector(point1: Point2, point2: Point2):
    """
    Given two Point2 (x,y) locations, return the direction vector
    Example get_direction_vector(self, self.start_location, self.main_base_ramp)
    Example Returns (-1.0, 1.0) as a Point2 tuple showing ramp is left and higher than starting position
    This can be useful for attacking as well and can get vectors all the way to enemy position, etc
    """
    direction_vector = point1.direction_vector(point2)
    return direction_vector