from flask import render_template
from app import app, db
from app.models import Point
import geopy, geopy.distance


@app.route('/')
@app.route('/index')
def index():
    place = ''

    result = db.engine.execute("SELECT name from planet_osm_polygon where boundary = 'administrative' and admin_level = '4'")
    for row in result:
        place = row['name']

    # get started with the first point
    # point = Point(45.51973, -122.67685)     # MT office
    # point = Point(45.51063, -122.59734)     # Mount Tabor
    # point = Point(45.51137, -122.69621)     # SW Portland
    # point = Point(45.44124, -122.75212)       # far SW Portland
    point = Point(45.5393, -122.4971)       # outer east side near gresham border - for testing edge detection
    point.find_nearest_road()
    points = [point]

    # A distance object we will use for moving the point around
    # (see https://stackoverflow.com/questions/24427828/calculate-point-based-on-distance-and-direction)
    mover = geopy.distance.VincentyDistance(feet=500)

    # look for points that are farther from the road
    for i in range(25):
        # try 5 new points: directly away from the road, and 45/90 deg to either side
        new_points = [
            mover.destination(point.geo, bearing=point.direction + 90),
            mover.destination(point.geo, bearing=point.direction + 135),
            mover.destination(point.geo, bearing=point.direction + 180),
            mover.destination(point.geo, bearing=point.direction + 225),
            mover.destination(point.geo, bearing=point.direction + 270)
        ]
        current_distance = point.distance
        best_point = point
        for p in new_points:
            pt = Point(p.latitude, p.longitude)
            if not pt.is_in_bounds():
                print("point " + str(pt) + " is out of bounds")
                continue
            pt.find_nearest_road()
            if pt.distance > current_distance:
                print("new point " + str(pt) + " is better")
                best_point = pt
                current_distance = pt.distance

        if current_distance == point.distance:
            print("can't do any better")
            break

        points.append(best_point)
        point = best_point

    return render_template('index.html',
                           title='Home',
                           place=place,
                           points=points)
