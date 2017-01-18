import json, requests, traceback

from tasks import insertKm

# Perform request and save it if it isn't null
redisq = "https://redisq.zkillboard.com/listen.php"
while 1 > 0:
    try:
        request = requests.get(url=redisq).text
        data = json.loads(request)['package']
        #print data
        if data != None:
            insertKm.delay(data)
            print data['killID']

    except ValueError:
        print json
        traceback.print_exc()
    except Exception:
        pass
