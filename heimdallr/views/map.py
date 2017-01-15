from flask import Response
from pymongo import errors
from bson.json_util import dumps

from heimdallr import app
from heimdallr.db import sdeFactory


# Returns all systems
@app.route("/map/systems", methods=['GET'])
def systems():
    # Get sde connection from factory
    sde = sdeFactory()

    # Query for ships
    rows = sde.query("SELECT solarSystemID as `id`, solarSystemName as `name`, \
                      mapConstellations.constellationName as `constellationName`, \
                      mapRegions.regionName as `regionName`, \
                      ROUND(mapSolarSystems.security, 3) as `security` \
                      FROM mapSolarSystems \
                      INNER JOIN mapConstellations ON mapConstellations.constellationID = mapSolarSystems.constellationID \
                      INNER JOIN mapRegions ON mapRegions.regionID = mapConstellations.regionID")

    return Response(response=rows.export('json'), status=200, mimetype="application/json")


# Returns all constellations for local autocomplete
@app.route("/map/constellations", methods=['GET'])
def constellations():
    # Get sde connection from factory
    sde = sdeFactory()

    # Query for constellations
    rows = sde.query("SELECT constellationID as `id`, constellationName as `name`, \
                      mapRegions.regionName as `regionName` \
                      FROM mapConstellations \
                      INNER JOIN mapRegions ON mapRegions.regionID = mapConstellations.regionID \
                      ORDER BY constellationName")

    return Response(response=rows.export('json'), status=200, mimetype="application/json")


# Returns all regions for local autocomplete
@app.route("/map/regions", methods=['GET'])
def regions():
    # Get sde connection from factory
    sde = sdeFactory()

    # Query for regions
    rows = sde.query("SELECT regionID as `id`, regionName as `name` \
                      FROM mapRegions \
                      ORDER BY regionName")

    return Response(response=rows.export('json'), status=200, mimetype="application/json")
