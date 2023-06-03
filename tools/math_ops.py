import math
from sc2.position import Point2

def closest_point(point, points):
    """This function returns the nearest point to a given point from a list of points."""
    def distance(p):
        x1, y1 = point
        x2, y2 = p
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    return min(points, key=distance)

def get_distance(point1: Point2, point2: Point2):
    """
    Given two Point2 (x,y) locations, return the distance in units
    Example get_distance(self, self.start_location, self.enemy_start_locations[0])
    Example Returns 115.5 which can be useful to determine how long until enemy shows up at doorstep
    This can be useful for prioritizing defending against enemy attacks
    """

    distance = point1.distance_to_point2(point2)
    return distance