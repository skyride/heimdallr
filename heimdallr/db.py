from pymongo import MongoClient
import records

db = MongoClient().heimdallr

def sdeFactory():
    return records.Database('mysql://heimdallr@127.0.0.1/oceanus')
