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
    limit 1
    """

    def __init__(self, lat, lon):
        self.geo = geopy.Point(latitude=lat, longitude=lon)
        self.distance = 0
        self.direction = 0

    def __str__(self):
        return str(self.geo.latitude) + ", " + str(self.geo.longitude)

    def find_nearest_road(self):
        sql = self.base_sql.format(**{'lat': self.geo.latitude, "lon": self.geo.longitude})
        result = db.engine.execute(sql)
        for row in result:
            self.distance = round(row['distance'],1)
            self.direction = round(row['azimuth'],1)

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
        where admin_level = '8' and name = 'Portland'
        """
        in_bounds = False
        result = db.engine.execute(sql.format(**{'lat': self.geo.latitude, "lon": self.geo.longitude}))
        for row in result:
            if row.intersects:
                in_bounds = True

        return in_bounds
