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

    starting_points = [
        # Point(45.51973, -122.67685),    # MT office
        Point(45.475835, -122.685968)    # SW Portland near I-5 curve
        # Point(45.51063, -122.59734),     # Mount Tabor
        # Point(45.5393, -122.4971)       # outer east side near gresham border - for testing edge detection
    ]

    for starting_point in starting_points:

        # get started with the first point
        # point = Point(45.51973, -122.67685)     # MT office
        # point = Point(45.51063, -122.59734)     # Mount Tabor
        # point = Point(45.51137, -122.69621)     # SW Portland
        # point = Point(45.44124, -122.75212)       # far SW Portland
        starting_point.find_nearest_road()
        points = [starting_point]

        # Which searching algorithm to use: 'simple', 'fan', 'weighted'
        algorithm = 'fan'

        # A distance object we will use for moving the point around
        # (see https://stackoverflow.com/questions/24427828/calculate-point-based-on-distance-and-direction)
        mover = geopy.distance.VincentyDistance(feet=1000)

        # look for points that are farther from the road
        current = starting_point
        for i in range(20):
            best_point = current
            if algorithm == 'simple':
                print(current)
                print("moving in simple direction: " + str(current.direction + 180))
                new_point = mover.destination(current.geo, bearing=current.direction + 180)
                best_point = Point(new_point.latitude, new_point.longitude)
                best_point.find_nearest_road()

            elif algorithm == 'fan':
                # try 5 new points: directly away from the road, and 45/90 deg to either side
                new_points = [
                    mover.destination(current.geo, bearing=current.direction + 90),
                    mover.destination(current.geo, bearing=current.direction + 135),
                    mover.destination(current.geo, bearing=current.direction + 180),
                    mover.destination(current.geo, bearing=current.direction + 225),
                    mover.destination(current.geo, bearing=current.direction + 270)
                ]
                for p in new_points:
                    pt = Point(p.latitude, p.longitude)
                    if pt.is_better_than(best_point):
                        best_point = pt

                if best_point.distance == current.distance:
                    print("can't do any better")
                    break

            elif algorithm == 'weighted':
                new_dir = current.find_weighted_direction()
                print("moving in weighted direction: " + str(new_dir))
                new_point = mover.destination(current.geo, bearing=new_dir)

                pt = Point(new_point.latitude, new_point.longitude)
                if pt.is_better_than(best_point):
                    best_point = pt

            points.append(best_point)
            current = best_point

    return render_template('index.html',
                           title='Home',
                           place=place,
                           points=points)
