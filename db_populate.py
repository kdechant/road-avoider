#!flask/bin/python
from app import db
from app.models import TestPoint

# All Washington
# sw: 45.95,-124.085
# ne: 49.00, -116.92

lat1 = 45950
lng1 = -124085
lat2 = 49000
lng2 = -116920

for lat in range(lat1, lat2, 40):
    for lng in range(lng1, lng2, 40):
        print("{}, {}".format(lat / 1000, lng / 1000))
        p = TestPoint()
        p.lat = lat / 1000
        p.lng = lng / 1000
        p.excluded = False
        db.session.add(p)
        db.session.commit()
