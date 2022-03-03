#from ace import pymongo
from pymongo import MongoClient
from os import getenv




#client = MongoClient(host=host,port=int(port),username=username,password=password)

client = None

def get_db_handle(username, password):
    host = getenv("MONGO_HOST")
    port = int(getenv("MONGO_PORT"))
    global client
    client = MongoClient(host=host,port=int(port),username=username,password=password)
    return client

#for db in client.list_databases():
#    print(db)

#db_handle, client = get_db_handle(db_name, host, port, username, password)


