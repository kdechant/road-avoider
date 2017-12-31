from flask import render_template, request, jsonify
from app import app, db
from app.models import TestPoint
from app.ai import *


@app.route('/')
@app.route('/index')
def index():

    return render_template('index.html')


@app.route('/api')
def api():

    lat = request.args.get('lat')
    lng = request.args.get('lng')
    starting_point = Point(lat, lng)

    result = db.engine.execute("SELECT name from planet_osm_polygon where boundary = 'administrative' and admin_level = '4'")
    for row in result:
        place = row['name']

    ais = [
        SimpleAI(),
        SpreadAI(),
        WeightedAI()
    ]
    points = {}

    for ai in ais:

        points[ai.name] = [starting_point.to_json()]

        # look for points that are farther from the road
        current = starting_point
        for i in range(10):
            next_point = ai.findNextPoint(current)

            if next_point.geo.latitude == current.geo.latitude and next_point.geo.longitude == current.geo.longitude:
                print("We're at the best point this AI can find")
                break

            points[ai.name].append(next_point.to_json())
            current = next_point

    return jsonify(points)


@app.route('/api/points')
def api_points():
    pts = TestPoint.query.filter(TestPoint.distance_track.isnot(None), TestPoint.excluded==False).order_by(TestPoint.distance_track.desc()).limit(500)
    json_points = []
    for pt in pts:
        json_points.append(pt.to_json())

    return jsonify(json_points)
