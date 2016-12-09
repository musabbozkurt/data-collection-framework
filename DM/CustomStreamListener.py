# stremaming class collect tweets according to keywords which are in the array
import pymongo
import tweepy

from DM import AllVariableClass
from DM import ConfigParser
from DM import GraduationProject


class CustomStreamListener(tweepy.StreamListener):
    stweets = []
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        self.db = pymongo.MongoClient().streamingdb
        GraduationProject.logger.info("Database has been created.")

    def on_data(self, tweet):
        with open(ConfigParser.streamingTxtFile, 'a') as tf:
            tf.write(tweet)
        GraduationProject.logger.info("Tweets which are collecting from Streaming API added to " + ConfigParser.streamingTxtFile + " filepath")
        return True
        self.db.tweets.insert(json.loads(tweet))
        logger.info("Tweets which are collecting from Streaming API added to mongodb ")

    def on_sapi(stwets):
        sapi = tweepy.streaming.Stream(AllVariableClass.auth, CustomStreamListener(AllVariableClass.api))
        sapi.filter(track=stwets)
        GraduationProject.logger.info("Getting Tweets json from Streaming API")

    def on_error(self, status_code):
        GraduationProject.logger.error("Don't kill the stream here status code : " + status_code)
        return True # Don't kill the stream

    def on_timeout(self):
        GraduationProject.logger.error("Don't kill the stream on timeouts")
        return True # Don't kill the stream
