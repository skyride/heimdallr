from pymongo import MongoClient, errors
import os
import traceback
import json, requests, datetime
import re
from bson.json_util import loads, dumps
from celery import Celery

from db import db, sdeFactory
sde = sdeFactory()

app = Celery('evething', backend='redis://127.0.0.1/', broker='redis://127.0.0.1/')


# Prunes instances of useless data from the object
def prune(obj):
    if isinstance(obj, dict):
        for key in obj.keys():
            if key == "href":
                obj.pop("href")
            else:
                m = re.search(r".*_str", key)
                if m:
                    obj.pop(key)
                else:
                    obj[key] = prune(obj[key])

    if isinstance(obj, list):
        for item in obj:
            item = prune(item)

    return obj


def getGroupObj(typeID):
    # Query for the group based on the typeID
    rows = sde.query("SELECT invGroups.groupID as `id`, groupName as `name`, categoryID \
                      FROM invTypes \
                      INNER JOIN invGroups ON invGroups.groupID = invTypes.groupID \
                      WHERE invTypes.typeID = :typeID", typeID=typeID)

    return loads(rows.export('json'))[0]


# Returns a dictionary with the system, constellation and region objects for the called system
def getMapData(solarSystemID):
    rows = sde.query("SELECT mapSolarSystems.solarSystemID, mapSolarSystems.solarSystemName, ROUND(mapSolarSystems.security, 3) as `security`, \
                        mapConstellations.constellationID, mapConstellations.constellationName, \
                        mapRegions.regionID, mapRegions.regionName \
                      FROM mapSolarSystems \
                      INNER JOIN mapConstellations ON mapConstellations.constellationID = mapSolarSystems.constellationID \
                      INNER JOIN mapRegions on mapRegions.regionID = mapConstellations.regionID \
                      WHERE mapSolarSystems.solarSystemID = :solarSystemID", solarSystemID=solarSystemID)
    row = rows[0]

    # Build return object
    ret = {
        "solarSystem": {
            "id": row['solarSystemID'],
            "securityStatus": row['security'],
            "name": row['solarSystemName'],
        },
        "constellation": {
            "id": row['constellationID'],
            "name": row['constellationName'],
        },
        "region": {
            "id": row['regionID'],
            "name": row['regionName'],
        }
    }

    return ret


# Insert an alliance
@app.task
def insertAlliance(id):
    # Search for the alliance in our database before we waste our time hitting CCP's API
    if db.alliances.find({"id": id}).count() > 0:
        return

    url = "https://esi.tech.ccp.is/latest/alliances/%s/" % id
    data = json.loads(requests.get(url=url).text)
    try:
        alliance = {
            "id": id,
            "name": data['alliance_name'],
            "ticker": data['ticker'],
            "startDate": data['date_founded'],
        }
    except KeyError:
        print "ESI API Error getting alliance ID: %s" % id
        return

    # try Insert
    try:
        id = db.alliances.insert_one(alliance).inserted_id
    except errors.DuplicateKeyError:
        pass


# Insert a corporation
@app.task
def insertCorporation(id):
    # Search for the corporation in our database before we waste our time hitting CCP's API
    if db.corporations.find({"id": id}).count() > 0:
        return

    url = "https://esi.tech.ccp.is/latest/corporations/%s/" % id
    data = json.loads(requests.get(url=url).text)
    try:
        corporation = {
            "id": id,
            "name": data['corporation_name'],
            "ticker": data['ticker'],
        }
    except KeyError:
        print "ESI API Error getting corporation ID: %s" % id
        return

    # try Insert
    try:
        id = db.corporations.insert_one(corporation).inserted_id
    except errors.DuplicateKeyError:
        pass


# Insert a character
@app.task
def insertCharacter(id):
    # Search for the character in our database before we waste our time hitting CCP's API
    if db.characters.find({"id": id}).count() > 0:
        return

    url = "https://esi.tech.ccp.is/latest/characters/%s/" % id
    data = json.loads(requests.get(url=url).text)
    try:
        character = {
            "id": id,
            "name": data['name'],
        }
    except KeyError:
        print "ESI API Error getting character ID: %s" % id
        return

    # try Insert
    try:
        id = db.characters.insert_one(character).inserted_id
    except errors.DuplicateKeyError:
        pass


@app.task
def insertKm(data):
    try:
        # Add map data
        mapData = getMapData(data['killmail']['solarSystem']['solarSystemID'])
        data.update(mapData)

        # Put the final blow attacker as its own thing on the killmail
        for attacker in data['killmail']['attackers']:
            if attacker['finalBlow'] == True:
                data['killmail']['finalBlow'] = attacker

        # Prune useless data to save space
        data = prune(data)

        # Try insert the data to search indexes
        # Alliances
        if "alliance" in data['killmail']['victim']:
            insertAlliance.delay(data['killmail']['victim']['alliance']['id'])

        # Corporations
        if "corporation" in data['killmail']['victim']:
            insertCorporation.delay(data['killmail']['victim']['corporation']['id'])

        # Characters
        if "character" in data['killmail']['victim']:
            insertCharacter.delay(data['killmail']['victim']['character']['id'])

        # Add ship group for victim
        if "shipType" in data['killmail']['victim']:
            data['killmail']['victim']['shipGroup'] = getGroupObj(data['killmail']['victim']['shipType']['id'])

        # Process Attackers
        for attacker in data['killmail']['attackers']:
            if "alliance" in attacker:
                insertAlliance(attacker['alliance']['id'])

            if "corporation" in attacker:
                insertCorporation(attacker['corporation']['id'])

            if "character" in attacker:
                insertCharacter(attacker['character']['id'])

            # Add Group
            if "shipType" in attacker:
                attacker['shipGroup'] = getGroupObj(attacker['shipType']['id'])

        # Insert the Kill
        id = db.kills.insert_one(data).inserted_id


        try:
            print "[%s]: %s (%s) %s's %s" % (datetime.datetime.now(), data['killmail']['killTime'], data['killID'], data['killmail']['victim']['corporation']['name'], data['killmail']['victim']['shipType']['name'])
        except Exception:
            print "[%s]: %s (%s) Non-ship mail" % (datetime.datetime.now(), data['killmail']['killTime'], data['killID'])
    except errors.DuplicateKeyError:
        print "DuplicateKeyError for KillID: %s" % data['killID']
    except KeyError:
        print dumps(data)
        traceback.print_exc()
