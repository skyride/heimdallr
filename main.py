from flask import Flask, jsonify
from pymongo import MongoClient, errors
from bson.json_util import loads, dumps

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/kill/<int:killID>")
def kill(killID):
    kills = MongoClient().heimdallr.kills
    kill = kills.find_one({"killID": killID})
    return jsonify(kill)

if __name__ == "__main__":
    app.run(debug=True)
