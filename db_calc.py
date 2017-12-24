#!flask/bin/python
from app import db
from app.models import TestPoint

state_sql = """
select name
from planet_osm_polygon
where
 boundary = 'administrative' and
 admin_level = '4'
 and ST_Intersects(
    ST_GeomFromText('POINT({lon} {lat})', 4326),
    ST_Transform(way, 4326)
)
"""

city_sql = """
select name
from planet_osm_polygon
where
 boundary = 'administrative' and
 admin_level = '8'
 and ST_Intersects(
    ST_GeomFromText('POINT({lon} {lat})', 4326),
    ST_Transform(way, 4326)
)
"""

main_road_distance_sql = """
select osm_id, name, highway, ref,
  ST_Distance(
   way2269,
   ST_Transform(ST_GeomFromText('POINT({lon} {lat})',4326), 2269)
 ) as distance
from roads
where highway in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'road', 'service', 'unclassified', 'track', 'residential')
order by distance
limit 1
"""

road_distance_sql = """
select osm_id, name, highway, ref,
  ST_Distance(
   way2269,
   ST_Transform(ST_GeomFromText('POINT({lon} {lat})',4326), 2269)
 ) as distance 
from roads
where highway in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'road', 'service', 'unclassified', 'track', 'residential')
order by distance
limit 1
"""

point_distance_sql = """
UPDATE test_point set excluded = true, exclude_reason = 3
WHERE distance_track IS NULL AND 
ST_Distance(way, ST_Transform(ST_GeomFromText('POINT({lon} {lat})',4326), 2269)) < 9000
"""

for i in range(0,1000):
    pts = TestPoint.query.filter(
        TestPoint.distance_track.is_(None),
        TestPoint.excluded == False
    ).limit(1)
    for p in pts:
        print(p)

        # find out which state it's in
        sql = state_sql.format(**{'lat': p.lat, 'lon': p.lng})
        result = db.engine.execute(sql)
        for row in result:
            p.state = row['name'][:2]

        # if not in a known state, exclude it
        if not p.state:
            print("is outside the state")
            p.excluded = True
            p.exclude_reason = 1

        # exclude if it's in an incorporated city
        sql = city_sql.format(**{'lat': p.lat, 'lon': p.lng})
        result = db.engine.execute(sql)
        for row in result:
            print("is in " + row['name'])
            p.excluded = True
            p.exclude_reason = 2

        if not p.excluded:
            # distance from any road
            sql = road_distance_sql.format(**{'lat': p.lat, "lon": p.lng})
            result = db.engine.execute(sql)
            for row in result:
                p.distance_track = round(row['distance'], 1)
                print(str(p.distance_track) + " ft")

                if p.distance_track < 3000:
                    # for oregon/washington, we don't care about points < 2 mi
                    # from a road; if this point is close to a road, exclude
                    # any points within a mile of it (to save processing time)
                    print("excluding nearby points")
                    q = point_distance_sql.format(**{'lat': p.lat, "lon": p.lng})
                    db.engine.execute(q)

        db.session.add(p)
        db.session.commit()


# refinement ideas
# 1. select any point with a distance > 30000
# 2. look for points within 5 miles with a higher distance. if one is found, skip the current point
# 3. reduce distance increment by half and plot points in all directions - 0, 45, 90, 135, 180, 225, 270, 315
# 4. check each of those points and see if it's farther
# 5. (or use the AI from the demo, set to avoid all roads)