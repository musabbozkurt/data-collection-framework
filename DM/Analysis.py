


# we will be using 4 Python libraries json for parsing the data, pandas for data manipulation,
# matplotlib for creating charts, adn re for regular expressions.
# The json and re libraries are installed by default in Python.
# You should install pandas and matplotlib if you don't have them in your machine.
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import GraduationProject


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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to language analysis: %s', file)

        # We can print the number of tweets using the command below. For the dataset that I prepared
        print(len(tweets_data))

        # Next, we will structure the tweets data into a pandas DataFrame to simplify the data manipulation.
        # We will start by creating an empty DataFrame called tweets using the following command.
        tweets = pd.DataFrame()

        GraduationProject.logger.info('Dataframe created to Analysis file According to language analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to location analysis: %s', file)
        print(len(tweets_data))

        tweets = pd.DataFrame()
        # print(tweets)

        GraduationProject.logger.info('Dataframe created to Analysis file According to country analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))

                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to location analysis: %s', file)

        print(len(tweets_data))

        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to location analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to timezone analysis: %s', file)

        print(len(tweets_data))

        tweets = pd.DataFrame()
        GraduationProject.logger.info('Dataframe created to Analysis file According to timezone analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to tweet analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to tweet analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to created at analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to created at analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to user id analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to user id analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to id str analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to id str analysis')

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
                            GraduationProject.logger.info('file : %s ' & line)
                            # tweet = json.loads(line)
                            # tokens = NGrams.ngrams(tweet['text'],3)
                            # print(tokens)
                        except Exception as e:
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to username analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to username analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to Screenname: %s', file)

        print(len(tweets_data))
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # Now, we can log to the root logger, or any other logger. First the root...
        GraduationProject.logger.info('Dataframe created to Analysis file According to Screenname')
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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to followers count analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to followers count analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to friends count analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)

        GraduationProject.logger.info('Dataframe created to Analysis file According to friends count analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to user language analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to user language analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to retweet count analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to retweet count analysis')

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
                            GraduationProject.logger.error("problem is ", str(e))
                            continue
                # Now, we can log to the root logger, or any other logger. First the root...
                GraduationProject.logger.info('Analizing file According to favorite count analysis: %s', file)
        print(len(tweets_data))
        tweets = pd.DataFrame()
        # print(tweets)
        GraduationProject.logger.info('Dataframe created to Analysis file According to favorite count analysis')

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

