# this class write all txt files which are in the filepath direction into mongodb database


class MongoWriter():
    def writetoMongo(self, filepath, mongodbName, mongodbCollectionName):
        import glob
        import json

        from DM import Logging

        # create mongodb database
        from pymongo import MongoClient

        client = MongoClient()
        db = client.__getattr__(mongodbName).__getattr__(mongodbCollectionName)

        # and inside that DB, a collection called "files"
        filenames = glob.glob(filepath)
        for filename in filenames:
            with open(filename) as f:
                for line in f:
                    db.insert_one(json.loads(line))
            Logging.log("Filename " + filename + " was added to mongodb collection name is files")
