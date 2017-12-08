from flask import render_template
from app import app, db
from app.models import Point
from app.ai import *
import geopy, geopy.distance


@app.route('/')
@app.route('/index')
def index():
    place = ''

    result = db.engine.execute("SELECT name from planet_osm_polygon where boundary = 'administrative' and admin_level = '4'")
    for row in result:
        place = row['name']

    # set the starting point. Currently hard-coded but will eventually come from the front end via API call
    # starting_point = Point(45.51973, -122.67685),    # MT office
    starting_point = Point(45.475835, -122.685968)    # SW Portland near I-5 curve
    # starting_point = Point(45.51063, -122.59734),     # Mount Tabor
    # starting_point = Point(45.5393, -122.4971)       # outer east side near gresham border - for testing edge detection
    # point = Point(45.51973, -122.67685)     # MT office
    # point = Point(45.51063, -122.59734)     # Mount Tabor
    # point = Point(45.51137, -122.69621)     # SW Portland
    # point = Point(45.44124, -122.75212)       # far SW Portland

    ais = [
        SimpleAI(),
        SpreadAI(),
        WeightedAI()
    ]
    points = {}

    for ai in ais:

        points[ai.name] = [starting_point]

        # look for points that are farther from the road
        current = starting_point
        for i in range(3):
            next_point = ai.findNextPoint(current)

            if next_point.geo.latitude == current.geo.latitude and next_point.geo.longitude == current.geo.longitude:
                print("We're at the best point this AI can find")
                break

            points[ai.name].append(next_point)
            current = next_point

    print(points)

    return render_template('index.html',
                           title='Home',
                           place=place,
                           points=points)
