from flask import Flask, Response
from pymongo import MongoClient, errors
from bson.json_util import loads, dumps

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/kill/<int:killID>")
def kill(killID):
    kills = MongoClient().heimdallr.kills
    kill = kills.find_one({"killID": killID}, projection={"_id": False})
    return Response(response=dumps(kill), status=200, mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)
