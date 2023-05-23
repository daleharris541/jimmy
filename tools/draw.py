from sc2.bot_ai import BotAI
from sc2.position import Point2, Point3
from typing import Set


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
                text=str(f"{p.x},{p.y}"),
                pos=pos,
                color=Point3((0, 0, 255)),
                size=16,
            )
            counter += 1
        self.client.debug_box2_out(
            pos, half_vertex_length=half_vertex_length, color=color
        )

    # self.client.debug_box2_out((self.start_location,self.get_terrain_z_height(self.start_location)), half_vertex_length=2.5, color=green)

def draw_green_circles(self: BotAI, circle_intersection):
    self.client.debug_sphere_out(circle_intersection, 5)

def draw_expansions(self: BotAI):
    green = Point3((0, 255, 0))
    for expansion_pos in self.expansion_locations_list:
        height = self.get_terrain_z_height(expansion_pos)
        expansion_pos3 = Point3((*expansion_pos, height))
        self.client.debug_box2_out(expansion_pos3, half_vertex_length=1, color=green)