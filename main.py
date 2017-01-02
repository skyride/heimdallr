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
    }

    # Decode the search params
    try:
        params = loads(params)
    except ValueError:
        return Response("[]", status=500, mimetype="application/json")

    # victimCharacter
    if "victimCharacter" in params:
        search['killmail.victim.character.id'] = params['victimCharacter']


    # Perform search and return result
    r = db.kills.find(search, projection=projection, limit=50)
    return Response(response=dumps(r), status=200, mimetype="application/json")



if __name__ == "__main__":
    app.run(debug=True)
