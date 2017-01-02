from flask import Flask, Response
from pymongo import MongoClient, errors
from bson.json_util import loads, dumps

app = Flask(__name__)
db = MongoClient().heimdallr

@app.route("/")
def hello():
    return "Hello World!"



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
        "_id": False,
        "killID": True,
        "killmail.killTime": True,
        "killmail.solarSystem": True,
        "killmail.attackerCount": True,
        "killmail.victim.alliance": True,
        "killmail.victim.corporation": True,
        "killmail.victim.character": True,
        "killmail.victim.shipType": True,
        "killmail.victim.damageTaken": True,
        "zkb.totalValue": True,
    }

    # Decode the search params
    try:
        params = loads(params)
    except ValueError:
        return Response("[]", status=500, mimetype="application/json")

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

    # solarSystem
    if "solarSystem" in params:
        search['killmail.solarSystem.id'] = {"$in": list(params['solarSystem'])}

    # carrying
    if "carrying" in params:
        search['killmail.victim.items.itemType.id'] = {"$in": list(params['carrying'])}


    # Perform search and return result if there are any kills provided
    r = db.kills.find(search, projection=projection, limit=50, sort=[("killmail.killTime", -1)])
    return Response(response=dumps(r), status=200, mimetype="application/json")



if __name__ == "__main__":
    app.run(debug=True)
