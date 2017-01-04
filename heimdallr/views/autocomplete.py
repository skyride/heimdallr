from flask import Response
from pymongo import errors
from bson.json_util import dumps

from heimdallr import app
from heimdallr.db import db

# Returns autocomplete results for alliance search
@app.route("/autocomplete/alliance/<string:search>", methods=['GET'])
def alliance(search):
    # Build Mongo search object
    searchobj = {
        "$or": [
            {
                "name": {
                    "$regex": "^%s" % search,
                    '$options' : 'i',
                }
            }, {
                "ticker": {
                    "$regex": "^%s" % search,
                    '$options' : 'i',
                }
            }
        ]
    }

    projection = {"_id": False }
    r = db.alliances.find(searchobj, projection=projection, limit=50)
    return Response(response=dumps(r), status=200, mimetype="application/json")


# Returns autocomplete results for corporation search
@app.route("/autocomplete/corporation/<string:search>", methods=['GET'])
def corporation(search):
    # Build Mongo search object
    searchobj = {
        "$or": [
            {
                "name": {
                    "$regex": "^%s" % search,
                    '$options' : 'i',
                }
            }, {
                "ticker": {
                    "$regex": "^%s" % search,
                    '$options' : 'i',
                }
            }
        ]
    }

    projection = {"_id": False }
    r = db.corporations.find(searchobj, projection=projection, limit=50)
    return Response(response=dumps(r), status=200, mimetype="application/json")


# Returns autocomplete results for character search
@app.route("/autocomplete/character/<string:search>", methods=['GET'])
def character(search):
    # Build Mongo search object
    searchobj = {
        "name": {
            "$regex": "^%s" % search,
            '$options' : 'i',
        }
    }

    projection = {"_id": False }
    r = db.characters.find(searchobj, projection=projection, limit=50)
    return Response(response=dumps(r), status=200, mimetype="application/json")
