#!flask/bin/python
from app import db
from app.models import TestPoint

base_sql = """
select osm_id, name, highway, ref,
  ST_Distance(
   ST_Transform(way,2269),
   ST_Transform(ST_GeomFromText('POINT({lon} {lat})',4326), 2269)
 ) as distance
from planet_osm_line
where
  highway in ('motorway', 'primary', 'secondary', 'tertiary', 'trunk', 'road', 'residential', 'service', 'unclassified')
order by distance
limit 1
"""

pts = TestPoint.query.filter(TestPoint.distance.is_(None))
# pts = TestPoint.query.filter(TestPoint.id==277)
for p in pts:
    print(p)
    sql = base_sql.format(**{'lat': p.lat, "lon": p.lng})
    result = db.engine.execute(sql)
    for row in result:
        p.distance = round(row['distance'], 1)
        print(str(p.distance) + " ft")
        db.session.add(p)
        db.session.commit()
