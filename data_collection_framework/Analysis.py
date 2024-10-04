# we will be using 4 Python libraries json for parsing the data, pandas for data manipulation,
# matplotlib for creating charts, adn re for regular expressions.
# The json and re libraries are installed by default in Python.
# You should install pandas and matplotlib if you don't have them in your machine.
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from data_collection_framework import Logging


class Analysis():
    # in this  function analysis of languages from text file which contains json data of tweets
    # it means plot top numbOfBar tweet language
    def lang_analiz(self, filepath, numOfBar):

        # Next we will read the data in into an array that we call tweets.
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)

                        # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to language analysis: %s' + filename)

            # We can print the number of tweets using the command below. For the dataset that I prepared
            print(len(tweets_data))

            # Next, we will structure the tweets data into a pandas DataFrame to simplify the data manipulation.
            # We will start by creating an empty DataFrame called tweets using the following command.
            tweets = pd.DataFrame()

            Logging.log('Dataframe created to Analysis file According to language analysis')

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
            ax.set_title('Top ' + str(numOfBar) + ' languages', fontsize=15, fontweight='bold')
            tweets_by_lang[:numOfBar].plot(ax=ax, kind='bar', color='red')
            # print(tweets)

            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def country_analiz(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to location analysis: %s' + filename)
            print(len(tweets_data))

            tweets = pd.DataFrame()
            # print(tweets)

            Logging.log('Dataframe created to Analysis file According to country analysis')

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
            ax.set_title('Top ' + str(numOfBar) + ' countries', fontsize=15, fontweight='bold')
            tweets_by_country[:numOfBar].plot(ax=ax, kind='bar', color='blue')

            plt.show()

        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    # this function plot according to location
    def location_analiz(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)

                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to location analysis: %s' + filename)

            print(len(tweets_data))

            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to location analysis')

            tweets['location'] = [tweet['place']['country'] if "place" in tweet and tweet['place']
                                  else np.nan for tweet in tweets_data]

            tweets_by_loc = tweets['location'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('Time zone', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' location', fontsize=15, fontweight='bold')
            tweets_by_loc[:numOfBar].plot(ax=ax, kind='bar', color='blue')

            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    # this function plots according to timezone
    def timezone_analiz(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)

                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to timezone analysis: %s' + filename)

            print(len(tweets_data))

            tweets = pd.DataFrame()
            Logging.log('Dataframe created to Analysis file According to timezone analysis')

            # print(tweets)
            tweets['time_zone'] = [tweet["user"]['time_zone'] if "user" in tweet and tweet["user"]['time_zone']
                                   else np.nan for tweet in tweets_data]
            tweets_by_time_zone = tweets['time_zone'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('Timezone', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' Timezone', fontsize=15, fontweight='bold')
            tweets_by_time_zone[:numOfBar].plot(ax=ax, kind='bar', color='blue')

            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    # the function below is plotting the most tweet text
    def tweet(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)

                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to tweet analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to tweet analysis')

            tweets['tweet'] = [tweet['text'] if 'text' in tweet else np.nan for tweet in tweets_data]

            tweets_by = tweets['tweet'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('Tweet', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' Tweet', fontsize=15, fontweight='bold')
            tweets_by[:numOfBar].plot(ax=ax, kind='bar', color='blue')

            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def create_at(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)

                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to created at analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to created at analysis')

            tweets['created_at'] = [tweet['created_at'] if 'created_at' in tweet else np.nan for tweet in tweets_data]

            tweets_by_created_at = tweets['created_at'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('created_at', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' created_at', fontsize=15, fontweight='bold')
            tweets_by_created_at[:numOfBar].plot(ax=ax, kind='bar', color='blue')

            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def user_id(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)

                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to user id analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to user id analysis')

            tweets['user_id'] = [tweet['user']['id'] if 'user' in tweet else np.nan for tweet in tweets_data]

            tweets_by_user_id = tweets['user_id'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('user_id', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' user_id', fontsize=15, fontweight='bold')
            tweets_by_user_id[:numOfBar].plot(ax=ax, kind='bar', color='blue')

            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def id_str(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)

                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to id str analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to id str analysis')

            tweets['id_str'] = [tweet['user']['id_str'] if 'user' in tweet else np.nan for tweet in tweets_data]
            tweets_by_id_str = tweets['id_str'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('id_str', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' id_str', fontsize=15, fontweight='bold')
            tweets_by_id_str[:numOfBar].plot(ax=ax, kind='bar', color='blue')
            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def username(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # Now, we can log to the root logger, or any other logger. First the root...
                        # Logging.log('file : %s ' & line)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to username analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to username analysis')

            tweets['username'] = [tweet['user']['name'] if 'user' in tweet else np.nan for tweet in tweets_data]
            tweets_by_username = tweets['username'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('username', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' username', fontsize=15, fontweight='bold')
            tweets_by_username[:numOfBar].plot(ax=ax, kind='bar', color='blue')
            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s " + str(e))

    def screename(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to Screenname: %s' + filename)

            print(len(tweets_data))
            tweets = pd.DataFrame()
            # Now, we can log to the root logger, or any other logger. First the root...
            Logging.log('Dataframe created to Analysis file According to Screenname')
            # print(tweets)

            tweets['screen_name'] = [tweet['user']['screen_name'] if 'user' in tweet else np.nan for tweet in
                                     tweets_data]
            tweets_by_screen_name = tweets['screen_name'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('screen_name', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' screen_name', fontsize=15, fontweight='bold')
            tweets_by_screen_name[:numOfBar].plot(ax=ax, kind='bar', color='blue')
            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s " + str(e))

    def followers_count(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to followers count analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to followers count analysis')

            tweets['followers_count'] = [tweet['user']['followers_count'] if 'user' in tweet else np.nan for tweet in
                                         tweets_data]
            tweets_by_followers_count = tweets['followers_count'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('followers_count', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' followers_count', fontsize=15, fontweight='bold')
            tweets_by_followers_count[:numOfBar].plot(ax=ax, kind='bar', color='blue')
            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def friends_count(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to friends count analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)

            Logging.log('Dataframe created to Analysis file According to friends count analysis')

            tweets['friends_count'] = [tweet['user']['friends_count'] if 'user' in tweet else np.nan for tweet in
                                       tweets_data]
            tweets_by_friends_count = tweets['friends_count'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('friends_count', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' friends_count', fontsize=15, fontweight='bold')
            tweets_by_friends_count[:numOfBar].plot(ax=ax, kind='bar', color='blue')
            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def user_lang(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to user language analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to user language analysis')

            tweets['user_lang'] = [tweet['user']['lang'] if 'user' in tweet else np.nan for tweet in tweets_data]
            tweets_by_user_lang = tweets['user_lang'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('user_lang', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' user_lang', fontsize=15, fontweight='bold')
            tweets_by_user_lang[:numOfBar].plot(ax=ax, kind='bar', color='blue')
            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def retweet_count(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to retweet count analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to retweet count analysis')

            tweets['retweet_count'] = [tweet['retweet_count'] for tweet in tweets_data]
            tweets_by_retweet_count = tweets['retweet_count'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('retweet_count', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' retweet_count', fontsize=15, fontweight='bold')
            tweets_by_retweet_count[:numOfBar].plot(ax=ax, kind='bar', color='blue')
            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))

    def favorite_count(self, filepath, numOfBar):
        tweets_data = []
        try:
            import glob
            filenames = glob.glob(filepath)
            for filename in filenames:
                with open(filename) as f:
                    for line in f:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        # tweet = json.loads(line)
                        # tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                # Now, we can log to the root logger, or any other logger. First the root...
                Logging.log('Analizing file According to favorite count analysis: %s' + filename)
            print(len(tweets_data))
            tweets = pd.DataFrame()
            # print(tweets)
            Logging.log('Dataframe created to Analysis file According to favorite count analysis')

            tweets['favorite_count'] = [tweet['favorite_count'] for tweet in tweets_data]
            tweets_by_favorite_count = tweets['favorite_count'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('favorite_count', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top ' + str(numOfBar) + ' favorite_count', fontsize=15, fontweight='bold')
            tweets_by_favorite_count[:numOfBar].plot(ax=ax, kind='bar', color='blue')
            plt.show()
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log("problem is %s" + str(e))
