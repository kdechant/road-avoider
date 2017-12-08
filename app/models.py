from app import db
import geopy, geopy.distance


class Point:

    base_sql = """
    select osm_id, name, highway, ref,
     ST_AsText(ST_Transform(ST_ClosestPoint(way, 'SRID=900913;POINT({lon} {lat})'::geometry), 4326)) as closest_point,
      ST_Distance(
       ST_Transform(way,2269),
       ST_Transform(ST_GeomFromText('POINT({lon} {lat})',4326), 2269)
     ) as distance,
     degrees(ST_Azimuth(
      ST_GeomFromText('POINT({lon} {lat})', 4326),
      ST_ClosestPoint(ST_Transform(way,4326), ST_GeomFromText('POINT({lon} {lat})', 4326))
     )) as azimuth
    from planet_osm_line
    where
      highway in ('motorway')
    order by distance
    limit {limit}
    """

    def __init__(self, lat, lon):
        self.geo = geopy.Point(latitude=lat, longitude=lon)
        self.distance = 0
        self.direction = 0
        self.find_nearest_road()

    def __str__(self):
        return str(self.geo.latitude) + ", " + str(self.geo.longitude)

    def to_json(self):
        return {
            'lat': self.geo.latitude,
            'lng': self.geo.longitude,
            'distance': self.distance,
            'direction': self.direction
        }

    def find_nearest_road(self):
        sql = self.base_sql.format(**{'lat': self.geo.latitude, "lon": self.geo.longitude, "limit": 1})
        result = db.engine.execute(sql)
        for row in result:
            self.distance = round(row['distance'],1)
            self.direction = round(row['azimuth'],1)

    def find_weighted_direction(self):
        """
        Finds the weighted average of the directions to the nearest two roads. Used by the "weighted" algorithm
        :return:
        """
        sql = self.base_sql.format(**{'lat': self.geo.latitude, "lon": self.geo.longitude, "limit": 2})
        result = db.engine.execute(sql)
        distance = []
        direction = []
        i = 0
        for row in result:
            distance.append(round(row['distance'],1))
            direction.append(round(row['azimuth'],1))
            i += 1

        new_dir = (direction[0] * distance[1] + direction[1] * distance[0]) / (distance[0] + distance[1])
        if abs(direction[0] - direction[1]) < 180:
            new_dir += 180.0
        print("new dir = " + str(new_dir))
        return new_dir

    def is_better_than(self, other_point):
        """
        Determines if this point (self) is valid and is in a better position than another point (other_point)
        :param pt: Another Point object, which will be compared to this one
        :return: boolean True if this point is valid and farther away than the other point. False otherwise.
        """
        # if not self.is_in_bounds():
        #     print("point " + str(self) + " is out of bounds")
        #     return False
        if self.distance > other_point.distance:
            print("new point " + str(self) + " is better than " + str(other_point))
            return True
        else:
            print("new point " + str(self) + " is worse than " + str(other_point))

    def is_in_bounds(self):
        """
        Determine if a point is within the allowed boundaries (i.e., is it inside the Portland city limits?)
        :return:
        """
        sql = """
        select osm_id, name, ST_Intersects(
            ST_GeomFromText('POINT({lon} {lat})', 4326),
            ST_Transform(way, 4326)
        ) as intersects
        from planet_osm_polygon
        where admin_level = '4'
        """
        # where admin_level = '4' and name = 'Portland'
        in_bounds = False
        result = db.engine.execute(sql.format(**{'lat': self.geo.latitude, "lon": self.geo.longitude}))
        for row in result:
            if row.intersects:
                in_bounds = True

        return in_bounds
