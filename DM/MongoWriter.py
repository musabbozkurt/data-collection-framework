
# this class write all txt files which are in the filepath direction into mongodb database
import glob
import json

import AllVariableClass
from DM import GraduationProject


class MongoWriter():
    def writetoMongo(filepath):
         # and inside that DB, a collection called "files"
         filenames = glob.glob(filepath)
         i = 0;
         for filename in filenames:
           with open(filename) as f:
             for line in f:
                 AllVariableClass.db.timeline.insert_one(json.loads(line))
                 GraduationProject.logger.info("Filename " + filename + " added to mongodb collection name is files")
