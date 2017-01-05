from flask import Response
from pymongo import errors
from bson.json_util import dumps

from heimdallr import app
from heimdallr.db import sdeFactory


# Returns all systems
@app.route("/autocomplete/systems", methods=['GET'])
def systems():
    # Get sde connection from factory
    sde = sdeFactory()

    # Query for ships
    rows = sde.query("SELECT solarSystemID as `id`, solarSystemName as `name`, \
                      mapConstellations.constellationName as `constellationName`, \
                      mapRegions.regionName as `regionName`, \
                      mapSolarSystems.security as `security` \
                      FROM mapSolarSystems \
                      INNER JOIN mapConstellations ON mapConstellations.constellationID = mapSolarSystems.constellationID \
                      INNER JOIN mapRegions ON mapRegions.regionID = mapConstellations.regionID")

    return Response(response=rows.export('json'), status=200, mimetype="application/json")
