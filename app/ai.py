import geopy, geopy.distance
from app.models import Point


class BaseAI:

    def __init__(self):
        # A distance object we will use for moving the point around
        # (see https://stackoverflow.com/questions/24427828/calculate-point-based-on-distance-and-direction)
        self.move_dist = 2000
        self.makeMover()

    def makeMover(self):
        self.mover = geopy.distance.VincentyDistance(feet=self.move_dist)

    def findNextPoint(self, current):
        raise NotImplementedError("This should be implemented in the subclass")


class SimpleAI(BaseAI):
    name = 'simple'

    def findNextPoint(self, current):
        print("moving in simple direction: " + str(current.direction + 180))
        new_latlng = self.mover.destination(current.geo, bearing=current.direction + 180)
        new_point = Point(new_latlng.latitude, new_latlng.longitude)
        if not new_point.is_in_bounds():
            print("point " + str(new_point) + " is out of bounds")
            return current
        if not new_point.is_better_than(current):
            self.move_dist *= .9
            self.makeMover()
        return new_point


class SpreadAI(BaseAI):
    name = 'spread'

    def findNextPoint(self, current):
        best_point = current
        new_points = [
            self.mover.destination(current.geo, bearing=current.direction + 90),
            self.mover.destination(current.geo, bearing=current.direction + 135),
            self.mover.destination(current.geo, bearing=current.direction + 180),
            self.mover.destination(current.geo, bearing=current.direction + 225),
            self.mover.destination(current.geo, bearing=current.direction + 270)
        ]
        for p in new_points:
            new_point = Point(p.latitude, p.longitude)
            if not new_point.is_in_bounds():
                print("point " + str(new_point) + " is out of bounds")
                continue
            if new_point.is_better_than(best_point):
                best_point = new_point

        return best_point


class WeightedAI(BaseAI):
    name = 'weighted'

    def findNextPoint(self, current):
        new_dir = current.find_weighted_direction()
        print("moving in weighted direction: " + str(new_dir))
        new_latlng = self.mover.destination(current.geo, bearing=new_dir)

        new_point = Point(new_latlng.latitude, new_latlng.longitude)
        if not new_point.is_in_bounds():
            print("point " + str(new_point) + " is out of bounds")
            return current
        if not new_point.is_better_than(current):
            self.move_dist *= .9
            self.makeMover()
        # if new_point.is_better_than(current):
        return new_point
        # else:
        #     return current
