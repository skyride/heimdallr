from pymongo import MongoClient, errors
import json, requests, datetime
from bson.json_util import loads, dumps

client = MongoClient()
kills = client.heimdallr.kills

# Perform request and save it if it isn't null
url = "https://redisq.zkillboard.com/listen.php"
while 1 > 0:
    data = json.loads(requests.get(url=url).text)['package']
    #print data
    if data != None:
        try:
            # Add constellation and region
            system = json.loads(requests.get(url=data['killmail']['solarSystem']['href']).text)
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

            id = kills.insert_one(data).inserted_id
            try:
                print "[%s]: %s (%s) %s's %s" % (datetime.datetime.now(), data['killmail']['killTime'], data['killID'], data['killmail']['victim']['corporation']['name'], data['killmail']['victim']['shipType']['name'])
            except Exception:
                print "[%s]: %s (%s) Non-ship mail" % (datetime.datetime.now(), data['killmail']['killTime'], data['killID'])
        except errors.DuplicateKeyError:
            print "DuplicateKeyError for KillID: %s" % data['killID']
        except KeyError:
            print dumps(data)
