import pymongo


CLIENT = pymongo.MongoClient('localhost', 27017)
DATABASE = "movies_data"


def save_in_mongo(data, collection):
    db = CLIENT[DATABASE]
    coll = db[collection]
    return coll.insert_one(data).inserted_id
