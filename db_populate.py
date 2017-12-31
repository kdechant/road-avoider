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
# SW 43.827, -122.179
# NE 44.291,-121.636

lat1 = 43800
lng1 = -122200
lat2 = 44300
lng2 = -121500

# kalmiopsis wilderness
# sw 42.0325,-124.0865
# ne 42.4427,-123.8132

# diablo mountain area
# sw 42.7500,-120.6560
# ne 43.1771,-120.0394

# whole state
# sw: 42.0, -124.5
# ne: 46.25, -116.46

# wallowas 1
# sw: 45.12 -117.44
# ne: 45.18 -117.22
#
lat1 = 45121
lng1 = -117441
lat2 = 45181
lng2 = -117221

for lat in range(lat1, lat2, 5):
    for lng in range(lng1, lng2, 5):
        print("{}, {}".format(lat / 1000, lng / 1000))
        p = TestPoint()
        p.lat = lat / 1000
        p.lng = lng / 1000
        p.excluded = False
        db.session.add(p)
        db.session.commit()
