#!flask/bin/python
from app import db
from app.models import TestPoint

base_sql = """
select osm_id, name, highway, ref,
 ST_AsText(ST_Transform(ST_ClosestPoint(way, 'SRID=900913;POINT({lon} {lat})'::geometry), 4326)) as closest_point,
  ST_Distance(
   ST_Transform(way,2269),
   ST_Transform(ST_GeomFromText('POINT({lon} {lat})',4326), 2269)
 ) as distance
from planet_osm_line
where
  highway in ('motorway', 'primary', 'secondary', 'tertiary', 'trunk', 'road', 'residential')
order by distance
limit 1
"""

pts = TestPoint.query.filter(TestPoint.distance.is_(None))
for p in pts:
    print(p)
    sql = base_sql.format(**{'lat': p.lat, "lon": p.lng})
    result = db.engine.execute(sql)
    for row in result:
        p.distance = round(row['distance'], 1)
        db.session.add(p)
        db.session.commit()
