from pymongo import MongoClient, errors
import json, requests, datetime

client = MongoClient()
kills = client.heimdallr.kills

# Perform request and save it if it isn't null
url = "https://redisq.zkillboard.com/listen.php"
while 1 > 0:
    data = json.loads(requests.get(url=url).text)['package']
    #print data
    if data != None:
        try:
            id = kills.insert_one(data).inserted_id
            try:
                print "[%s]: %s (%s) %s's %s" % (datetime.datetime.now(), data['killmail']['killTime'], data['killID'], data['killmail']['victim']['corporation']['name'], data['killmail']['victim']['shipType']['name'])
            except Exception:
                print "[%s]: %s (%s) Non-ship mail" % (datetime.datetime.now(), data['killmail']['killTime'], data['killID'])
        except errors.DuplicateKeyError:
            print "DuplicateKeyError for KillID: %s" % data['killID']
