# stremaming class collect tweets according to keywords which are in the array
import pymongo
import tweepy

from DM.AllVariableClass import AllVariableClass
from DM.menu import mongodbName, mongodbCollectionName, sentence

from DM import ConfigParser
from DM import Logging

class CustomStreamListener(tweepy.StreamListener):
    stweets = []
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

    def on_data(self, tweet):
        self.db = pymongo.MongoClient().__getattr__(mongodbName).__getattr__(mongodbCollectionName)
        Logging.log(mongodbName+" database has been created.")
        with open(ConfigParser.streamingTxtFile, 'a') as tf:
            tf.write(tweet)
            import json
            self.db.insert(json.loads(tweet))
        Logging.log("Tweets which are collecting from Streaming API added to " + ConfigParser.streamingTxtFile + " filepath")
        Logging.log("Tweets which are collecting from Streaming API added to mongodb ")
        return True

    def on_sapi(self,stwets):
        sapi = tweepy.streaming.Stream(AllVariableClass.auth, CustomStreamListener(AllVariableClass.api))
        sapi.filter(track=stwets)
        Logging.log("Getting Tweets json from Streaming API")

    def on_error(self, status_code):
        print("we have error")
        Logging.log("Don't kill the stream here status code : " + status_code)
        return True # Don't kill the stream

    def on_timeout(self):
        Logging.log("Don't kill the stream on timeouts")
        return True # Don't kill the stream
