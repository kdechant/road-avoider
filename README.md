# Road Avoider

This is a sample project using OpenStreetMap data to see if we can find the point on a given map that is furthest from a road.

This project uses an extract of the data from OSM and a few Python and PostgreSQL tools to do geometry-based calculations.

## Running the project

1. Install Python 3.4+, PostgreSQL, PostGIS, and osm2pgsql.
2. Set up virtual environment: `python3 -m venv flask`
3. Activate virtual environment: `source flask/bin/activate`
4. Install the python packages: `pip install -r requirements.txt`
5. Download the Oregon data set in PBF format from https://download.geofabrik.de/north-america/us/oregon.html
6. Create a database called "gis"
7. Use osm2pgsql to load the data into your local instance of PostgreSQL: `osm2pgsql --create --database gis oregon-latest.osm.pbf`
8. Configure your database username and password in config.py
9. From a terminal, run ./run.py to start the dev server
10. Go to http://127.0.0.1:5000/ to see the app
