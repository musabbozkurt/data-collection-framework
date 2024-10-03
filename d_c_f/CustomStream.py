# stremaming class collect tweets according to keywords which are in the array
import pymongo
import tweepy

from d_c_f.config.TwitterConfigSetter import TwitterConfigSetter

from d_c_f.config import ConfigParser
from d_c_f import Logging


class CustomStream(tweepy.StreamListener):
    stweets = []

    def __init__(self, api, mongodbName, mongodbCollectionName, fileName, numOfStreamTweet):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        self.num_tweets = 0
        self.mongodbName = mongodbName
        self.mongodbCollectionName = mongodbCollectionName
        self.fileName = fileName
        self.numOfStreamTweet = numOfStreamTweet

    def on_data(self, tweet):
        with open(ConfigParser.streamingTxtFile + self.fileName, 'a') as tf:
            tf.write(tweet)
            import json
            self.db = pymongo.MongoClient().__getattr__(self.mongodbName).__getattr__(self.mongodbCollectionName)
            Logging.log(self.mongodbName + " database has been created.")
            self.db.insert(json.loads(tweet))

        Logging.log(
            "Tweets which are collecting from Streaming API added to " + ConfigParser.streamingTxtFile + " filepath")
        Logging.log(
            "Tweets which are collecting from Streaming API added to " + self.mongodbCollectionName + " inside " + self.mongodbName + "mongodb database")
        return True

    def on_sapi(self, stwets):
        self.num_tweets += 1
        if self.num_tweets < self.numOfStreamTweet:
            sapi = tweepy.streaming.Stream(TwitterConfigSetter.auth,
                                           CustomStream(TwitterConfigSetter.api,
                                                        self.mongodbName,
                                                        self.mongodbCollectionName,
                                                        self.fileName, self.numOfStreamTweet))
            sapi.filter(track=stwets)

            self.db = pymongo.MongoClient().__getattr__(self.mongodbName).__getattr__(
                self.mongodbCollectionName).insert(stwets)
            return True
        else:
            return False
        Logging.log("Getting Tweets json from Streaming API")

    def on_error(self, status_code):
        print("we have error")
        Logging.log("Don't kill the stream here status code : " + status_code)
        return True  # Don't kill the stream

    def on_timeout(self):
        Logging.log("Don't kill the stream on timeouts")
        return True  # Don't kill the stream
