#from ace import pymongo
from pymongo import MongoClient
from os import getenv
from pymongo.errors import PyMongoError

#client = MongoClient(host=host,port=int(port),username=username,password=password)

clientpool = {}

def get_collection_instance(clientInstance, db, collection):
    
    return clientInstance[db][collection]


def get_db_handle(username, password):
    host = getenv("MONGO_HOST")
    port = int(getenv("MONGO_PORT"))
    client = MongoClient(host=host, port=int(
        port), username=username, password=password)

    try:
        client.admin.command("ismaster")
        return client
    except PyMongoError:
        return None


# for db in client.list_databases():
#    print(db)

#db_handle, client = get_db_handle(db_name, host, port, username, password)
