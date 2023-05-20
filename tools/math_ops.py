import math

def closest_point(point, points):
    """This function returns the nearest point to a given point from a list of points."""
    def distance(p):
        x1, y1 = point
        x2, y2 = p
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    
    return min(points, key=distance)