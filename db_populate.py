#!flask/bin/python
from app import db
from app.models import TestPoint

# SE Oregon
#43.25,-119.0
#42,00, -117.03

# Jefferson area
# NW 44.75, -121.95
# 44.50,-121.68

# three sisters wilderness area
# SW 43.8276, -122.179
# NE 44.2914,-121.6365

lat1 = 4383
lat2 = 4429
lng1 = -12218
lng2 = -12164

for lat in range(lat1, lat2, 5):
    for lng in range(lng1, lng2, 5):
        print("{}, {}".format(lat / 100, lng / 100))
        p = TestPoint()
        p.lat = lat / 100
        p.lng = lng / 100
        db.session.add(p)
        db.session.commit()
