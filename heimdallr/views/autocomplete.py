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
                "killmail.victim.alliance.name": {
                    "$regex": "%s.*" % search
                }
    }

    r = db.kills.find(searchobj)
    return Response(response=dumps(r), status=200, mimetype="application/json")
