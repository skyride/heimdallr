from pymongo import MongoClient, errors
import os
import traceback
import json, requests, datetime
import re
from bson.json_util import loads, dumps

from db import db, sdeFactory

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
    # Get sde connection from factory
    sde = sdeFactory()

    # Query for the group based on the typeID
    rows = sde.query("SELECT invGroups.groupID as `id`, groupName as `name`, categoryID \
                      FROM invTypes \
                      INNER JOIN invGroups ON invGroups.groupID = invTypes.groupID \
                      WHERE invTypes.typeID = :typeID", typeID=typeID)

    return loads(rows.export('json'))[0]


# Insert an alliance
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

def scrape():
    # Perform request and save it if it isn't null
    redisq = "https://redisq.zkillboard.com/listen.php"
    while 1 > 0:
        try:
            request = requests.get(url=redisq).text
            data = json.loads(request)['package']
            #print data
            if data != None:
                try:
                    # Add constellation and region
                    sysurl = "https://crest-tq.eveonline.com/solarsystems/%s/" % (data['killmail']['solarSystem']['id'])
                    system = json.loads(requests.get(url=sysurl).text)
                    constellation = json.loads(requests.get(url=system['constellation']['href']).text)
                    region = json.loads(requests.get(url=constellation['region']['href']).text)

                    data['killmail']['solarSystem']['securityStatus'] = system['securityStatus']

                    data['killmail']['constellation'] = {
                        "id": system['constellation']['id'],
                        "name": constellation['name'],
                    }

                    data['killmail']['region'] = {
                        "id": region['id'],
                        "name": region['name'],
                    }

                    # Put the final blow attacker as its own thing on the killmail
                    for attacker in data['killmail']['attackers']:
                        if attacker['finalBlow'] == True:
                            data['killmail']['finalBlow'] = attacker

                    # Prune useless data to save space
                    data = prune(data)

                    # Try insert the data to search indexes
                    # Alliances
                    if "alliance" in data['killmail']['victim']:
                        insertAlliance(data['killmail']['victim']['alliance']['id'])

                    # Corporations
                    if "corporation" in data['killmail']['victim']:
                        insertCorporation(data['killmail']['victim']['corporation']['id'])

                    # Characters
                    if "character" in data['killmail']['victim']:
                        insertCharacter(data['killmail']['victim']['character']['id'])

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
        except ValueError:
            print json
            traceback.print_exc()
        except Exception:
            pass


if os.path.basename(__file__) == "scraper.py":
    scrape()
    pass
