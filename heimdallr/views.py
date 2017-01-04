import sys, os
from flask import Flask, Response, render_template
from pymongo import MongoClient, errors
from bson.json_util import loads, dumps

from heimdallr import app

db = MongoClient().heimdallr

@app.route("/")
def main():
    return app.send_static_file('main.html')


# Returns the full kill object
@app.route("/kill/<int:killID>", methods=['GET'])
def kill(killID):
    kill = db.kills.find_one({"killID": killID}, projection={"_id": False})
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
    projection = {
        "_id": True,
        "killID": True,
        "killmail.killTime": True,
        "killmail.solarSystem": True,
        "killmail.region": True,
        "killmail.attackerCount": True,
        "killmail.victim.alliance": True,
        "killmail.victim.corporation": True,
        "killmail.victim.character": True,
        "killmail.victim.shipType": True,
        "killmail.victim.damageTaken": True,
        "killmail.finalBlow": True,
        "zkb.totalValue": True,
    }

    # Decode the search params
    try:
        params = loads(params)
    except ValueError:
        return Response("[]", status=400, mimetype="application/json")

    # victimCharacter
    if "victimCharacter" in params:
        search['killmail.victim.character.id'] = {"$in": list(params['victimCharacter'])}

    # victimCorporation
    if "victimCorporation" in params:
        search['killmail.victim.corporation.id'] = {"$in": list(params['victimCorporation'])}

    # victimAlliance
    if "victimAlliance" in params:
        search['killmail.victim.alliance.id'] = {"$in": list(params['victimAlliance'])}

    # attackerCharacter
    if "attackerCharacter" in params:
        search['killmail.attackers.character.id'] = {"$in": list(params['attackerCharacter'])}

    # attackerCorporation
    if "attackerCorporation" in params:
        search['killmail.attackers.corporation.id'] = {"$in": list(params['attackerCorporation'])}

    # attackerAlliance
    if "attackerAlliance" in params:
        search['killmail.attackers.alliance.id'] = {"$in": list(params['attackerAlliance'])}

    # victimShipType
    if "victimShipType" in params:
        search['killmail.victim.shipType.id'] = {"$in": list(params['victimShipType'])}

    # carrying
    if "carrying" in params:
        search['killmail.victim.items.itemType.id'] = {"$in": list(params['carrying'])}

    # solarSystem
    if "solarSystem" in params:
        search['killmail.solarSystem.id'] = {"$in": list(params['solarSystem'])}

    # constellation
    if "constellation" in params:
        search['killmail.constellation.id'] = {"$in": list(params['constellation'])}

    # region
    if "region" in params:
        search['killmail.region.id'] = {"$in": list(params['region'])}

    # minimumValue
    if "minimumValue" in params:
        search['zkb.totalValue'] = {"$gte": params['minimumValue']}


    # Check we've generated search parameters before wasting the database's time
    #if search == {}:
    #    return Response("[]", status=400, mimetype="application/json")

    # Make sort order based on the existence of last mail received
    if "lastObj" in params:
        #sort = [("_id", -1)]
        sort = [("killmail.killTime", -1)]
    else:
        sort = [("killmail.killTime", -1)]


    # Perform search and return result if there are any kills provided
    r = db.kills.find(search, projection=projection, limit=50, sort=sort)
    return Response(response=dumps(r), status=200, mimetype="application/json")
