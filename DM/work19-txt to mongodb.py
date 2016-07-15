from pymongo import MongoClient
import glob
import json


client = MongoClient()
db = client.twitter

 # and inside that DB, a collection called "files"

filenames = glob.glob("D:/PycharmProjects/timelines/MCGtimelines/*.txt")
i = 0;
for filename in filenames:
  with open(filename) as f:
    for line in f:
        db.timeline.insert_one(json.loads(line))


print(len(filenames))