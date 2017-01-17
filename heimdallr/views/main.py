from flask import Response
from pymongo import errors
from bson.json_util import loads, dumps

import base64

from heimdallr import app
from heimdallr.db import db
from heimdallr.views import projections

@app.route("/")
def main():
    return app.send_static_file('main.html')


# Returns the full kill object
@app.route("/kill/<int:killID>", methods=['GET'])
def kill(killID):
    kill = db.kills.find_one({"killID": killID}, projection=projections.nullID)
    if kill != None:
        return Response(response=dumps(kill), status=200, mimetype="application/json")
    else:
        return Response(response="null", status=404, mimetype="application/json")



# Searches the database for kills meeting the parameters provided
# and returns a minimised projection of that data
@app.route("/search/<string:params>", methods=['GET'])
def search(params):
    # Starting values
    search = {}
    params = base64.b64decode(params)

    # Decode the search params
    try:
        params = loads(params)
    except ValueError:
        return Response("[]", status=400, mimetype="application/json")

    # Base search object
    searchObj = {
        "$and": []
    }

    # $or accumulators
    victimObj = []
    victimShipObj = []
    attackerObj = []
    attackerShipObj = []
    locationObj = []

    # victimCharacter
    if "victimCharacter" in params:
        if len(params['victimCharacter']) > 0:
            victimObj.append({
                'killmail.victim.character.id': {"$in": list(params['victimCharacter'])},
            })

    # victimCorporation
    if "victimCorporation" in params:
        if len(params['victimCorporation']) > 0:
            victimObj.append({
                'killmail.victim.corporation.id': {"$in": list(params['victimCorporation'])},
            })

    # victimAlliance
    if "victimAlliance" in params:
        if len(params['victimAlliance']) > 0:
            victimObj.append({
                'killmail.victim.alliance.id': {"$in": list(params['victimAlliance'])},
            })

    # victimShipType
    if "victimShipType" in params:
        if len(params['victimShipType']) > 0:
            victimShipObj.append({
                'killmail.victim.shipType.id': {"$in": list(params['victimShipType'])},
            })

    # victimShipGroup
    if "victimShipGroup" in params:
        if len(params['victimShipGroup']) > 0:
            victimShipObj.append({
                'killmail.victim.shipGroup.id': {"$in": list(params['victimShipGroup'])},
            })

    # attackerCharacter
    if "attackerCharacter" in params:
        if len(params['attackerCharacter']) > 0:
            attackerObj.append({
                'killmail.attackers.character.id': {"$in": list(params['attackerCharacter'])}
            })

    # attackerCorporation
    if "attackerCorporation" in params:
        if len(params['attackerCorporation']) > 0:
            attackerObj.append({
                'killmail.attackers.corporation.id': {"$in": list(params['attackerCorporation'])}
            })

    # attackerAlliance
    if "attackerAlliance" in params:
        if len(params['attackerAlliance']) > 0:
            attackerObj.append({
                'killmail.attackers.alliance.id': {"$in": list(params['attackerAlliance'])}
            })

    # attackerShipType
    if "attackerShipType" in params:
        if len(params['attackerShipType']) > 0:
            attackerShipObj.append({
                'killmail.attackers.shipType.id': {"$in": list(params['attackerShipType'])},
            })

    # attackerShipGroup
    if "attackerShipGroup" in params:
        if len(params['attackerShipGroup']) > 0:
            attackerShipObj.append({
                'killmail.attackers.shipGroup.id': {"$in": list(params['attackerShipGroup'])},
            })

    # carrying
    if "carrying" in params:
        if len(params['carrying']) > 0:
            search['killmail.victim.items.itemType.id'] = {"$in": list(params['carrying'])}

    # solarSystem
    if "solarSystem" in params:
        if len(params['solarSystem']) > 0:
            locationObj.append({
                'killmail.solarSystem.id': {"$in": list(params['solarSystem'])},
            })

    # constellation
    if "constellation" in params:
        if len(params['constellation']) > 0:
            locationObj.append({
                'killmail.constellation.id': {"$in": list(params['constellation'])},
            })

    # region
    if "region" in params:
        if len(params['region']) > 0:
            locationObj.append({
                'killmail.region.id': {"$in": list(params['region'])},
            })

    # minimumValue
    if "minimumValue" in params:
        if params['minimumValue'] != None:
            search['zkb.totalValue'] = {"$gte": params['minimumValue']}


    # Build search object
    if len(victimObj) > 0:
        victimObj = { "$or": victimObj }
        searchObj["$and"].append(victimObj)

    if len(victimShipObj) > 0:
        victimShipObj = { "$or": victimShipObj }
        searchObj["$and"].append(victimShipObj)

    if len(attackerObj) > 0:
        attackerObj = { "$or": attackerObj }
        searchObj["$and"].append(attackerObj)

    if len(attackerShipObj) > 0:
        attackerShipObj = { "$or": attackerShipObj }
        searchObj["$and"].append(attackerShipObj)

    if len(locationObj) > 0:
        locationObj = { "$or": locationObj }
        searchObj["$and"].append(locationObj)

    # Add victim ship
    if "killmail.victim.shipType.id" in search:
        obj = {"killmail.victim.shipType.id": search['killmail.victim.shipType.id']}
        searchObj["$and"].append(obj)

    # Check we've generated search parameters before wasting the database's time
    if searchObj == { "$and": [] }:
        searchObj = {}

    # Make sort order based on the existence of last mail received
    if searchObj == {}:
        sort = [("_id", -1)]
    else:
        sort = [("killmail.killTime", -1)]


    # Perform search and return result if there are any kills provided
    r = db.kills.find(searchObj, projection=projections.killList, limit=50, sort=sort)
    return Response(response=dumps(r), status=200, mimetype="application/json")
