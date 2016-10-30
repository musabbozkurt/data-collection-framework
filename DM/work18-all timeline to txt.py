#!/usr/bin/env python
# encoding: utf-8
import pymongo
from pymongo import MongoClient
import tweepy #https://github.com/tweepy/tweepy
import json
import glob

class AllVariableClass:
        # Twitter API credentials
        consumer_key = ""
        consumer_secret = ""
        access_key = ""
        access_secret = ""

        # authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)

        # files direction
        filePathForOutputs = "give path for user timelines which are stored as txt file"
        filePathForFollowersOutputs = "give a path followers txt file"
        ListOfUsernamefilepath = 'give a txt file path which contains username list '
        filepathformongo = "give a path which contains txt files waiting for to be added mongodb"

        # create mongodb database
        client = MongoClient()
        db = client.twitter3
        streamingdb = 'streamingdb'


# getting all tweets in users timeline according to their username.
class TweetCollector():
        def get_all_tweets(screen_name):
            #Twitter only allows access to a users most recent 3240 tweets with this method

            #initialize a list to hold all the tweepy Tweets
            alltweets = []

            #make initial request for most recent tweets (200 is the maximum allowed count)
            new_tweets = AllVariableClass.api.user_timeline(screen_name = screen_name,count=200)

            #save most recent tweets
            alltweets.extend(new_tweets)

            #save the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1

            #keep grabbing tweets until there are no tweets left to grab
            while (len(new_tweets) > 0):
                print ("getting tweets before %s" % (oldest))

                #all subsiquent requests use the max_id param to prevent duplicates
                new_tweets = AllVariableClass.api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

                #save most recent tweets
                alltweets.extend(new_tweets)

                #update the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1

                print ("...%s tweets downloaded so far" % (len(alltweets)))
                # control api to do not exceed the 1000 limits                
                if (len(alltweets)) == 1000:
                    break
            #write tweets to the txt files
            for tweet in alltweets:
                f = open(AllVariableClass.filePathForOutputs + screen_name + ".txt", "a")
                f.write(json.dumps(tweet._json) + "\n")
            print(screen_name+"'s tweets added to file")
            pass
# this class write all txt files which are in the filepath direction into mongodb database
class MongoWriter():
    def writetoMongo(filepath):
         # and inside that DB, a collection called "files"
         filenames = glob.glob(filepath)
         i = 0;
         for filename in filenames:
           with open(filename) as f:
             for line in f:
                 AllVariableClass.db.timeline.insert_one(json.loads(line))

# stremaming class collect tweets according to keywords which are in the array
class CustomStreamListener(tweepy.StreamListener):
    stweets = []
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()

        self.db = pymongo.MongoClient().streamingdb

    def on_data(self, tweet):
        self.db.tweets.insert(json.loads(tweet))

    def on_sapi(stwets):
        sapi = tweepy.streaming.Stream(AllVariableClass.auth, CustomStreamListener(AllVariableClass.api),q='geocode:"37.781157,-122.398720,1mi" since:2016-10-30 until:2016-10-31 include:retweets')
        sapi.filter(track=stwets)

    def on_error(self, status_code):
        return True # Don't kill the stream

    def on_timeout(self):
        return True # Don't kill the stream
#
class FollowerCollector():
    def write_on_file(self,screenname):
        for follower in AllVariableClass.api.followers_ids(screenname):
            try:
                with open(AllVariableClass.filePathForFollowersOutputs + screenname + ".txt", "a") as f:
                    f.write(AllVariableClass.api.get_user(follower).screen_name + ' \n')
            except:
                print(screenname+str(IOError))
                pass

if __name__ == '__main__':
    # pass in the username of the account you want to download

     with open(AllVariableClass.ListOfUsernamefilepath,'r') as f:
        try:
            for line in f:
                  for word in line.split():
                     TweetCollector.get_all_tweets(word)
                     FollowerCollector().write_on_file(word)

            MongoWriter.writetoMongo(AllVariableClass.filepathformongo)
            CustomStreamListener.on_sapi(['ygs', 'indian'])
        except:
            # print(str(IOError))
            pass
