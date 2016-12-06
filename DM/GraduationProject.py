#!/usr/bin/env python
# encoding: utf-8
import operator
import os
import nltk
import pymongo
from pymongo import MongoClient
import tweepy #https://github.com/tweepy/tweepy
import glob
from collections import Counter
from nltk.corpus import stopwords
import string

from sklearn.feature_extraction.text import TfidfVectorizer
# We will start first by uploading json and pandas using the commands below:
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.naive_bayes import MultinomialNB
from sklearn import cross_validation, svm
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn import metrics
from sklearn.model_selection import ShuffleSplit
from sklearn.model_selection import cross_val_predict
import re

import logging

def get_log():
    logger = logging.getLogger('PyPro')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('pypro.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # create formatter and add it to the handlers
    fhFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    chFormatter = logging.Formatter('%(levelname)s - %(filename)s - Line: %(lineno)d - %(message)s')
    fh.setFormatter(fhFormatter)
    ch.setFormatter(chFormatter)

    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info("-----------------------------------")
    logger.info("Log system successfully initialised")
    logger.info("-----------------------------------")

    return logger

logger = get_log()

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
        filePathForOutputs = ""
        filePathForFollowersOutputs = ""
        ListOfUsernamefilepath = ''
        filepathformongo = ""
        filepathfortokenization = ""
        streamingTxtFile = ""

        # create mongodb database
        client = MongoClient()
        db = client.twitter3
        streamingdb = 'streamingdb'


        # Now, we can log to the root logger, or any other logger. First the root...
        logger.info('Variable has been called from AllClassVariable')


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
                if (len(alltweets)) >= 1000:
                    logger.info("1000 tweets have been collected")
                    break
            #write tweets to the txt files
            for tweet in alltweets:
                f = open(AllVariableClass.filePathForOutputs + screen_name + ".txt", "a")
                f.write(json.dumps(tweet._json) + "\n")
            print(screen_name+"'s tweets added to file")
            logger.info("Tweets have been added to "+screen_name+".txt")
            pass

        def on_error(self, status_code):
            logger.error("Don't kill the collector here status code is : " +status_code)
            return True  # Don't kill the collector

        def on_timeout(self):
            logger.error("Don't kill the collector on timeouts.")
            return True  # Don't kill the collector

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
           logger.info("Filename "+filename+" added to mongodb collection name is files")

# stremaming class collect tweets according to keywords which are in the array
class CustomStreamListener(tweepy.StreamListener):
    stweets = []
    def __init__(self, api):
        self.api = api
        super(tweepy.StreamListener, self).__init__()
        self.db = pymongo.MongoClient().streamingdb
        logger.info("Database has been created.")

    def on_data(self, tweet):
        with open(AllVariableClass.streamingTxtFile, 'a') as tf:
            tf.write(tweet)
        logger.info("Tweets which are collecting from Streaming API added to "+AllVariableClass.streamingTxtFile+ " filepath")
        return True
        self.db.tweets.insert(json.loads(tweet))
        logger.info("Tweets which are collecting from Streaming API added to mongodb ")

    def on_sapi(stwets):
        sapi = tweepy.streaming.Stream(AllVariableClass.auth, CustomStreamListener(AllVariableClass.api))
        sapi.filter(track=stwets)
        logger.info("Getting Tweets json from Streaming API")

    def on_error(self, status_code):
        logger.error("Don't kill the stream here status code : "+status_code)
        return True # Don't kill the stream

    def on_timeout(self):
        logger.error("Don't kill the stream on timeouts")
        return True # Don't kill the stream
#
class FollowerCollector():
    def write_on_file(self,screenname):
        for follower in AllVariableClass.api.followers_ids(screenname):
            try:
                with open(AllVariableClass.filePathForFollowersOutputs + screenname + ".txt", "a") as f:
                    f.write(AllVariableClass.api.get_user(follower).screen_name + ' \n')
                logger.info("FollowerCollector is collected followers of "+screenname+"and added to "+screenname+".txt")
            except:
                print(screenname+str(IOError))
                logger.error("Screen name : " +screenname+" with error "+str(Exception))
                pass

    def on_error(self, status_code):
        logger.error("Don't kill the followerCollector. error status code : "+status_code)
        return True # Don't kill the followerCollector

    def on_timeout(self):
        logger.error("Don't kill the followerCollector on timeouts")
        return True # Don't kill the followerCollector

class TokenizationTextFile():
        emoticons_str = r"""
            (?:
                [:=;] # Eyes
                [oO\-]? # Nose (optional)
                [D\)\]\(\]/\\OpP] # Mouth
            )"""

        regex_str = [
            emoticons_str,
            r'<[^>]+>',  # HTML tags
            r'(?:@[\w_]+)',  # @-mentions
            r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
            r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

            r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
            r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
            r'(?:[\w_]+)',  # other words
            r'(?:\S)'  # anything else
        ]

        tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
        emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)

        def preprocess(s, lowercase=False):
            tokens = TokenizationTextFile.tokens_re.findall(s)
            if lowercase:
                tokens = [token if TokenizationTextFile.emoticon_re.search(token) else token.lower() for token in tokens]
                logger.info("Preprocess function is called it preserves eyes,nose,urls mouth ... etc")
            return tokens

# we will be using 4 Python libraries json for parsing the data, pandas for data manipulation,
# matplotlib for creating charts, adn re for regular expressions.
# The json and re libraries are installed by default in Python.
# You should install pandas and matplotlib if you don't have them in your machine.
class Analiz():
    # in this  function analysis of languages from text file which contains json data of tweets
    # it means plot top 5 tweet language
    def lang_analiz(filepath):
        # Next we will read the data in into an array that we call tweets.
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to language analysis: %s', file)

        # We can print the number of tweets using the command below. For the dataset that I prepared
        print(len(tweets_data))

        # Next, we will structure the tweets data into a pandas DataFrame to simplify the data manipulation.
        # We will start by creating an empty DataFrame called tweets using the following command.
        tweets = pd.DataFrame()

        logger.info('Dataframe created to Analysis file According to language analysis')

        # print(tweets)
        # tweets['text'] = map(lambda tweet: tweet['text'], tweets_data)

        # Next, we will add 1 columns to the tweets DataFrame called  lang
        # lang column contains the language in which the tweet was written,
        tweets['lang'] = [tweet["user"]['lang'] if "user" in tweet and tweet["user"]['lang']
                          else np.nan for tweet in tweets_data]

        tweets_by_lang = tweets['lang'].value_counts()

        # Next, we will create a chart: it is describing the Top 5 languages in which the tweets were written,

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('Languages', fontsize=10)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 languages', fontsize=15, fontweight='bold')
        tweets_by_lang[:5].plot(ax=ax, kind='bar', color='red')
        # print(tweets)

        plt.show()

    def country_analiz(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to location analysis: %s', file)
        print(len(tweets_data))

        tweets = pd.DataFrame()
        # print(tweets)

        logger.info('Dataframe created to Analysis file According to country analysis')

        # and country the country from which the tweet was sent.
        tweets['country'] = [tweet['place']['country'] if "place" in tweet and tweet['place']
                             else np.nan for tweet in tweets_data]

        tweets_by_country = tweets['country'].value_counts()

        #   the Top 5 countries from which the tweets were sent.
        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('Countries', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 countries', fontsize=15, fontweight='bold')
        tweets_by_country[:5].plot(ax=ax, kind='bar', color='blue')

        plt.show()

    # this function plot according to location
    def location_analiz(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))

                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to location analysis: %s', file)

        print(len(tweets_data))

        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to location analysis')

        tweets['location'] = [tweet['place']['country'] if "place" in tweet and tweet['place']
                              else np.nan for tweet in tweets_data]

        tweets_by_loc = tweets['location'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('Time zone', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 location', fontsize=15, fontweight='bold')
        tweets_by_loc[:5].plot(ax=ax, kind='bar', color='blue')

        plt.show()

    # this function plots according to timezone
    def timezone_analiz(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to timezone analysis: %s', file)

        print(len(tweets_data))

        tweets = pd.DataFrame()
        logger.info('Dataframe created to Analysis file According to timezone analysis')

        # print(tweets)
        tweets['time_zone'] = [tweet["user"]['time_zone'] if "user" in tweet and tweet["user"]['time_zone']
                               else np.nan for tweet in tweets_data]
        tweets_by_time_zone = tweets['time_zone'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('Timezone', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 Timezone', fontsize=15, fontweight='bold')
        tweets_by_time_zone[:5].plot(ax=ax, kind='bar', color='blue')

        plt.show()

    def tweet(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to tweet analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to tweet analysis')

        tweets['tweet'] = [tweet['text'] if 'text' in tweet else  np.nan for tweet in tweets_data]

        tweets_by = tweets['tweet'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('Tweet', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 Tweet', fontsize=15, fontweight='bold')
        tweets_by[:5].plot(ax=ax, kind='bar', color='blue')

        plt.show()

    def create_at(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to created at analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to created at analysis')

        tweets['created_at'] = [tweet['created_at'] if 'created_at' in tweet else np.nan for tweet in tweets_data]

        tweets_by_created_at = tweets['created_at'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('created_at', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 created_at', fontsize=15, fontweight='bold')
        tweets_by_created_at[:5].plot(ax=ax, kind='bar', color='blue')

        plt.show()

    def user_id(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to user id analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to user id analysis')

        tweets['user_id'] = [tweet['user']['id'] if 'user' in tweet else np.nan for tweet in tweets_data]

        tweets_by_user_id = tweets['user_id'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('user_id', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 user_id', fontsize=15, fontweight='bold')
        tweets_by_user_id[:5].plot(ax=ax, kind='bar', color='blue')

        plt.show()

    def id_str(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to id str analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to id str analysis')

        tweets['id_str'] = [tweet['user']['id_str'] if 'user' in tweet else np.nan for tweet in tweets_data]
        tweets_by_id_str = tweets['id_str'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('id_str', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 id_str', fontsize=15, fontweight='bold')
        tweets_by_id_str[:5].plot(ax=ax, kind='bar', color='blue')
        plt.show()

    def username(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # Now, we can log to the root logger, or any other logger. First the root...
                            logging.info('file : %s ' & line)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to username analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to username analysis')

        tweets['username'] =[tweet['user']['name'] if 'user' in tweet else np.nan for tweet in tweets_data]
        tweets_by_username = tweets['username'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('username', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 username', fontsize=15, fontweight='bold')
        tweets_by_username[:5].plot(ax=ax, kind='bar', color='blue')
        plt.show()

    def screename(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is " ,str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to Screenname: %s' , file)

        print(len(tweets_data))
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # Now, we can log to the root logger, or any other logger. First the root...
        logger.info('Dataframe created to Analysis file According to Screenname')
        # print(tweets)

        tweets['screen_name'] = [tweet['user']['screen_name'] if 'user' in tweet else np.nan for tweet in tweets_data]
        tweets_by_screen_name = tweets['screen_name'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('screen_name', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 screen_name', fontsize=15, fontweight='bold')
        tweets_by_screen_name[:5].plot(ax=ax, kind='bar', color='blue')
        plt.show()

    def followers_count(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to followers count analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to followers count analysis')

        tweets['followers_count'] = [tweet['user']['followers_count'] if 'user' in tweet else np.nan for tweet in tweets_data]
        tweets_by_followers_count = tweets['followers_count'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('followers_count', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 followers_count', fontsize=15, fontweight='bold')
        tweets_by_followers_count[:5].plot(ax=ax, kind='bar', color='blue')
        plt.show()

    def friends_count(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to friends count analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)

        logger.info('Dataframe created to Analysis file According to friends count analysis')

        tweets['friends_count'] = [tweet['user']['friends_count'] if 'user' in tweet else np.nan for tweet in tweets_data]
        tweets_by_friends_count = tweets['friends_count'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('friends_count', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 friends_count', fontsize=15, fontweight='bold')
        tweets_by_friends_count[:5].plot(ax=ax, kind='bar', color='blue')
        plt.show()

    def  user_lang(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to user language analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to user language analysis')

        tweets['user_lang'] = [tweet['user']['lang'] if 'user' in tweet else np.nan for tweet in tweets_data]
        tweets_by_user_lang = tweets['user_lang'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('user_lang', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 user_lang', fontsize=15, fontweight='bold')
        tweets_by_user_lang[:5].plot(ax=ax, kind='bar', color='blue')
        plt.show()

    #
    # def geo_of_tweet(filepath):
    #     filenames = glob.glob(filepath)
    #     tweets_data = []
    #     for file in filenames:
    #         with open(file) as f:
    #             for line in f:
    #                 try:
    #                     tweet = json.loads(line)
    #                     tweets_data.append(tweet)
    #                     # tweet = json.loads(line)
    #                     # tokens = NGrams.ngrams(tweet['text'],3)
    #                     # print(tokens)
    #                 except:
    #                     continue
    #     print(len(tweets_data))
    #     print(len(tweets_data))
    #     tweets = pd.DataFrame()
    #     # print(tweets)
    #
    #     tweets['geo'] = [tweet['geo'] for tweet in tweets_data]
    #     tweets_by_geo = tweets['geo'].value_counts()
    #
    #     fig, ax = plt.subplots()
    #     ax.tick_params(axis='x', labelsize=15)
    #     ax.tick_params(axis='y', labelsize=10)
    #     ax.set_xlabel('geo', fontsize=15)
    #     ax.set_ylabel('Number of tweets', fontsize=15)
    #     ax.set_title('Top 5 geo', fontsize=15, fontweight='bold')
    #     tweets_by_geo[:5].plot(ax=ax, kind='bar', color='blue')
    #     plt.show()

    def retweet_count(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to retweet count analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to retweet count analysis')

        tweets['retweet_count'] = [tweet['retweet_count'] for tweet in tweets_data]
        tweets_by_retweet_count = tweets['retweet_count'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('retweet_count', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 retweet_count', fontsize=15, fontweight='bold')
        tweets_by_retweet_count[:5].plot(ax=ax, kind='bar', color='blue')
        plt.show()

    def favorite_count(filepath):
        tweets_data = []
        for subdir, dirs, files in os.walk(filepath):
            for file in files:
                file_path = subdir + os.path.sep + file
                with open(file_path) as f:
                    for line in f:
                        try:
                            tweet = json.loads(line)
                            tweets_data.append(tweet)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                logger.info('Analizing file According to favorite count analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        logger.info('Dataframe created to Analysis file According to favorite count analysis')

        tweets['favorite_count'] = [tweet['favorite_count'] for tweet in tweets_data]
        tweets_by_favorite_count = tweets['favorite_count'].value_counts()

        fig, ax = plt.subplots()
        ax.tick_params(axis='x', labelsize=15)
        ax.tick_params(axis='y', labelsize=10)
        ax.set_xlabel('favorite_count', fontsize=15)
        ax.set_ylabel('Number of tweets', fontsize=15)
        ax.set_title('Top 5 favorite_count', fontsize=15, fontweight='bold')
        tweets_by_favorite_count[:5].plot(ax=ax, kind='bar', color='blue')
        plt.show()

class SemanticOrientation():
    emoticons_str = r"""
                (?:
                    [:=;] # Eyes
                    [oO\-]? # Nose (optional)
                    [D\)\]\(\]/\\OpP] # Mouth
                )"""

    regex_str = [
        emoticons_str,
        r'<[^>]+>',  # HTML tags
        r'(?:@[\w_]+)',  # @-mentions
        r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
        r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',  # URLs

        r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
        r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
        r'(?:[\w_]+)',  # other words
        r'(?:\S)'  # anything else
    ]

    tokens_re = re.compile(r'(' + '|'.join(regex_str) + ')', re.VERBOSE | re.IGNORECASE)
    emoticon_re = re.compile(r'^' + emoticons_str + '$', re.VERBOSE | re.IGNORECASE)

    def preprocess(s, lowercase=False):
        tokens = SemanticOrientation.tokens_re.findall(s)
        if lowercase:
            tokens = [token if SemanticOrientation.emoticon_re.search(token) else token.lower() for token in tokens]
        return tokens


    def term_counter(*args,**kwargs):
        fname = AllVariableClass.streamingTxtFile
        with open(fname, 'r') as f:
            count_all = Counter()
            for line in f:
                tweet = json.loads(line)
                # Create a list with all the terms
                terms_all = [term for term in SemanticOrientation.preprocess(tweet['text'])]
                # Update the counter
                count_all.update(terms_all)
            # Print the first 5 most frequent words
            # print(count_all)
            print('Top 5 ')
            print(count_all.most_common(5))


        punctuation = list(string.punctuation)
        stop = stopwords.words('english') + punctuation + ['rt', 'via']
        terms_stop = [term for term in SemanticOrientation.preprocess(tweet['text']) if term not in stop]
        print('Stop terms ')
        print(terms_stop)

        # Count terms only once, equivalent to Document Frequency
        terms_single = set(terms_all)
        print('terms_single ')
        print(terms_single)

        # Count hashtags only
        terms_hash = [term for term in SemanticOrientation.preprocess(tweet['text'])
                      if term.startswith('#')]
        print('terms_hash ')
        print(terms_hash)

        # Count terms only (no hashtags, no mentions)
        terms_only = [term for term in SemanticOrientation.preprocess(tweet['text'])
                      if term not in stop and
                      not term.startswith(('#', '@'))]

        print('terms_only ')
        print(terms_only)


    def semantic(search_word,fname):

        from collections import defaultdict
        # remember to include the other import from the previous post

        com = defaultdict(lambda: defaultdict(int))
        punctuation = list(string.punctuation)
        stop = stopwords.words('english') + punctuation + ['rt', 'via']

        # f is the file pointer to the JSON data set
        with open(fname, 'r') as f:
            count_all = Counter()
            for line in f:
                tweet = json.loads(line)
                # Create a list with all the terms
                terms_all = [term for term in SemanticOrientation.preprocess(tweet['text'])]
                # Update the counter
                count_all.update(terms_all)
                terms_only = [term for term in SemanticOrientation.preprocess(tweet['text'])
                              if term not in stop
                              and not term.startswith(('#', '@'))]
                print('All terms ' )
                print(terms_only)

                # Build co-occurrence matrix
                for i in range(len(terms_only) - 1):
                    for j in range(i + 1, len(terms_only)):
                        w1, w2 = sorted([terms_only[i], terms_only[j]])
                        if w1 != w2:
                            com[w1][w2] += 1

                com_max = []

                # For each term, look for the most common co-occurrent terms
                for t1 in com:
                    t1_max_terms = sorted(com[t1].items(), key=operator.itemgetter(1), reverse=True)[:5]
                    for t2, t2_count in t1_max_terms:
                        com_max.append(((t1, t2), t2_count))

                # Get the most frequent co-occurrences
                terms_max = sorted(com_max, key=operator.itemgetter(1), reverse=True)
                print('the most frequent co-occurrences ')
                print(terms_max[:5])

                # search_word  # pass a term as a command-line argument
                count_search = Counter()
                for line in f:
                    tweet = json.loads(line)
                    terms_only = [term for term in SemanticOrientation.preprocess(tweet['text'])
                                  if term not in stop
                                  and not term.startswith(('#', '@'))]
                    if search_word in terms_only:
                        count_search.update(terms_only)

                print("Co-occurrence for %s:" % search_word)
                print(count_search.most_common(20))

                names, values = zip(*terms_max)
                ind = np.arange(len(terms_max))  # the x locations for the groups
                width = 0.70  # the width of the bars

                fig, ax = plt.subplots()
                rects1 = ax.bar(ind, values, width, color='r')

                # add some text for labels, title and axes ticks
                ax.set_ylabel('Count')
                ax.set_xticks(ind + width / 2.)
                ax.set_xticklabels(names)

                def autolabel(rects):
                    # attach some text labels
                    for rect in rects:
                        height = rect.get_height()
                        ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                                '%d' % int(height),
                                ha='center', va='bottom')

                autolabel(rects1)

                plt.show()


                # n_docs is the total n. of tweets
                p_t = terms_all
                p_t_com = nltk.defaultdict(lambda: nltk.defaultdict(int))
                positive_vocab = [
                    'good', 'nice', 'great', 'awesome', 'outstanding',
                    'fantastic', 'terrific', ':)', ':-)', 'like', 'love',
                    # shall we also include game-specific terms?
                    # 'triumph', 'triumphal', 'triumphant', 'victory', etc.
                ]
                negative_vocab = [
                    'bad', 'terrible', 'crap', 'useless', 'hate', ':(', ':-(',
                    # 'defeat', etc.
                ]

class TermFrequency:
    def preprocess(term):
        return term.lower().translate(string.punctuation)

    # returns the distinct elements from a list
    def distinct(myList):
        seen = set()
        seen_add = seen.add
        return [x for x in myList if not (x in seen or seen_add(x))]
    def termfreq(fpath):
        classLabels = []
        fileNames = []
        for subdir, dirs, files in os.walk(fpath):
            for file in files:
                file_path = subdir + os.path.sep + file
                file_content = open(file_path).read()
                # NGrams.ngrams(file_content, 2)
                fileNames.append(file_path)
                classLabels.append(subdir[15:])
        tfidf = TfidfVectorizer(tokenizer=TokenizationTweet.tokenize, preprocessor=TermFrequency.preprocess, lowercase=True)
        # tfidf = TfidfVectorizer(tokenizer=TokenizationTextFile.tokenTextFile, preprocessor=TermFrequency.preprocess,lowercase=True)
        docTermMatrix = tfidf.fit_transform((open(f).read() for f in fileNames))

        print(docTermMatrix.shape)
        print(classLabels)

        # test on training set
        X_train = docTermMatrix
        y_train = classLabels
        X_test = docTermMatrix
        y_test = classLabels

        classifier = MultinomialNB().fit(X_train, y_train)
        predictions = classifier.predict(X_test)
        evalReport = classification_report(y_test, predictions,target_names=classifier.classes_)  # distinct(classLabels))
        print(evalReport)

        cm = confusion_matrix(classLabels, predictions)
        print("Confusion matrix:")
        print(cm)

        # train-test split 60%-40%
        X_train, X_test, y_train, y_test = cross_validation.train_test_split(docTermMatrix, classLabels, test_size=0.4,random_state=0)

        classifier = MultinomialNB().fit(X_train, y_train)
        predictions = classifier.predict(X_test)
        accuracy = classifier.score(X_test, y_test)
        print(accuracy)

        evalReport = classification_report(y_test, predictions, target_names=TermFrequency.distinct(classLabels))
        print(evalReport)

        cm = confusion_matrix(y_test, predictions)
        print("Confusion matrix:")
        print(cm)

        X = np.array(X_train)
        y = np.array(y_train)
        X2 = np.array(X_test)
        y2 = np.array(y_test)

        print(X.shape, y.shape, X2.shape, y2.shape)

        # support vector machines sklearn svc is one of the classfiers
        clf = svm.SVC(kernel='linear', C=1)
        scores = cross_val_score(clf, docTermMatrix, classLabels, cv=10)
        print('scores : ', scores)

        mean_score = scores.mean()
        print('mean_score : ', mean_score)

        # calculation of  area under  curve
        std_dev = scores.std()
        std_error = scores.std() / np.math.sqrt(scores.shape[0])
        ci = 2.262 * std_error
        lower_bound = mean_score - ci
        upper_bound = mean_score + ci
        print("Score is %f +/-  %f" % (mean_score, ci))
        print('95 percent probability that if this experiment were repeated over and over the average score would be between %f and %f' % (lower_bound, upper_bound))
        print("Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))

        scores = cross_val_score(clf, docTermMatrix, classLabels, cv=15, scoring='f1_macro')

        # test accuracy 1 0 arasi
        print('f1_macro scoring : ', scores)
        n_samples = docTermMatrix.shape[0]
        cv = ShuffleSplit(n_splits=10, test_size=0.3, random_state=0)

        print(cross_val_score(clf, docTermMatrix, classLabels, cv=cv))
        predicted = cross_val_predict(clf, docTermMatrix, classLabels, cv=10)
        print('10-fold cross validation : ', metrics.accuracy_score(classLabels, predicted))

# word ngrams technique (split text into word group)
class NGrams():
    def ngrams(input, n):
        input = input.split(' ')
        output = {}
        for i in range(len(input) - n + 1):
            g = ' '.join(input[i:i + n])
            output.setdefault(g, 0)
            output[g] += 1
        print(output)

# character ngrams technique (split word into character group)
class CharNGrams():
    def charNGrams(input, n):
        input = input.split(' ')
        output = {}
        for i in range(len(input) - n + 1):
            g = ' '.join(input[i:i + n])
            asd = [g[i:i + n] for i in range(len(g) - n + 1)]
            # print(asd)
            output.setdefault(g, 0)
            output[g] += 1
            # print(output)

class TokenizationTweet():
    # kelime koku
    def stemmerTrFps6(term):
        return term[:6]

    def stem_tokens(tokens, stemmer):
        stemmed = []
        for item in tokens:
            stemmed.append(stemmer(item))
        return stemmed

    def tokenize(text):
        stemmer = TokenizationTweet.stemmerTrFps6
        tokens = nltk.word_tokenize(text)
        stems = TokenizationTweet.stem_tokens(tokens, stemmer)
        return stems

if __name__ == '__main__':
    # # pass in the username of the account you want to download
    #
    with open(AllVariableClass.ListOfUsernamefilepath,'r') as f:
             for line in f:
                   for word in line.split():
                      TweetCollector.get_all_tweets(word)
                      FollowerCollector().write_on_file(word)
    # MongoWriter.writetoMongo(AllVariableClass.filepathformongo)
    # CustomStreamListener.on_sapi(['#python','java','#java','javascript','#javascript'])
    # Analiz.lang_analiz(AllVariableClass.streamingTxtFile)
    # Analiz.country_analiz(AllVariableClass.streamingTxtFile)
    # Analiz.location_analiz(AllVariableClass.streamingTxtFile)
    # Analiz.timezone_analiz(AllVariableClass.streamingTxtFile)
    # TermFrequency.termfreq(AllVariableClass.filepathfortokenization)
    # SemanticOrientation.term_counter()
    # SemanticOrientation.semantic('java',AllVariableClass.streamingTxtFile)
    # Analiz.lang(AllVariableClass.streamingTxtFile)
    # Analiz.lang(AllVariableClass.filepathfortokenization)
    #Analiz.screename(AllVariableClass.filepathfortokenization)
