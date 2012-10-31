from linkedin import settings

class MongoDBClient(object):
    def __init__(self, col):
        import pymongo
        connection = pymongo.Connection(settings.MONGODB_SERVER, settings.MONGODB_PORT)
        self.db = connection[settings.MONGODB_DB]
        self.collection = self.db[col]
        
    