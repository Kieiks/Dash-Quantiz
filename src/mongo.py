
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd

def append_to_mongo(df):
    uri = "mongodb+srv://kieiks:UHTZeD8BWLxkKnmb@fraldas.1gjvb.mongodb.net/?retryWrites=true&w=majority&appName=fraldas"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    database = client['dash_quantiz']
    collection = database['results']

    # query = {}
    # update_operation = { '$set': {'TAMANHO':'XG'}}
    # result = collection.update_many(query, update_operation)
    # collection.insert_many(data)
    # print("Data inserted successfully!")

    collection.insert_many(df.to_dict('records'))
    print("Data inserted successfully!")
    client.close()
