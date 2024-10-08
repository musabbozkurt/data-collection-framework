#!/usr/bin/env python3.8
import json
import os
import socket
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
parent_dir_path = os.path.abspath(os.path.join(dir_path, os.pardir))
sys.path.insert(0, parent_dir_path)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '127.0.0.1'
port = 5555
socksize = 1024
s.bind((host, port))

while True:
    from data_collection_framework import Logging
    from data_collection_framework.config import ConfigParser
    from data_collection_framework.TweetCollector import TweetCollector
    from data_collection_framework.FollowerCollector import FollowerCollector
    from data_collection_framework.MongoWriter import MongoWriter
    from data_collection_framework.Analysis import Analysis
    import tweepy
    from data_collection_framework.CustomStreamListener import CustomStreamListener
    from datetime import datetime
    from tweepy import Stream
    from data_collection_framework.CrossValidation import TermFrequency
    from data_collection_framework.TermFreqAndAllTerms import TermFreqAndAllTerms

    print("Now listening...\n")
    s.listen(5)
    conn, addr = s.accept()

    print('New connection from %s:%d' % (addr[0], addr[1]))
    data = conn.recv(socksize).decode("UTF-8")
    jsonResponse = (json.loads(data))
    print(jsonResponse)

    if (jsonResponse['msg0']) == "collecttweetfromuserlist":
        try:
            tweetcollect = TweetCollector()
            numberOfTweet = jsonResponse['msg1']
            with open(ConfigParser.file_path_for_list_of_username, 'r') as f:
                for line in f:
                    for word in line.split():
                        tweetcollect.get_all_tweets(word, int(numberOfTweet), mongodbName='CollectTweetFromUserList')
        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')
    elif (jsonResponse['msg0']) == "collecttweetfromusername":
        try:
            tweetcollect = TweetCollector()
            username = jsonResponse['msg1']
            numberOfTweet = int(jsonResponse['msg2'])
            tweetcollect.get_all_tweets(username, int(numberOfTweet), mongodbName='CollectTweetFromUsername')

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')
    elif (jsonResponse['msg0']) == 'collectfollowerfromuserlist':
        try:
            followercollect = FollowerCollector()
            with open(ConfigParser.file_path_for_list_of_username, 'r') as f:
                for line in f:
                    for word in line.split():
                        followercollect.write_on_file(word)
        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "collectfollowerfromusername":
        try:
            followercollect = FollowerCollector()
            username = jsonResponse['msg1']
            followercollect.write_on_file(username)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "storedata":
        try:
            mongodbName = jsonResponse['msg1']
            mongodbCollectionName = jsonResponse['msg2']

            mongoWrite = MongoWriter()
            mongoWrite.writetoMongo(ConfigParser.file_path_for_mongo, mongodbName, mongodbCollectionName)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotlanguage":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.lang_analiz(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotcountry":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.country_analiz(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotlocation":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.location_analiz(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plottimezone":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.timezone_analiz(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plottweet":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.tweet(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))

        count = 0
        conn.send(str(count))

    elif (jsonResponse['msg0']) == "plottweetcreatedat":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.create_at(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotuserid":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.user_id(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotstringofid":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.id_str(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotusername":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.username(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotscreenname":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.screename(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotfollowerscount":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.followers_count(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotfriendscount":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.friends_count(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotuserlanguage":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.user_lang(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotretweet":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.retweet_count(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "plotfavourite":
        try:
            analysis = Analysis()
            numberOfBar = int(jsonResponse['msg1'])
            analysis.favorite_count(ConfigParser.file_path_for_mongo, numberOfBar)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "streamfromlist":
        try:
            mongodbName = jsonResponse['msg1']
            mongodbCollectionName = jsonResponse['msg2']
            fileName = jsonResponse['msg3']

            auth = tweepy.OAuthHandler(ConfigParser.consumer_key, ConfigParser.consumer_secret)
            auth.set_access_token(ConfigParser.access_key, ConfigParser.access_secret)
            api = tweepy.API(auth)

            fmt = '%Y-%m-%d %H:%M:%S'
            now = datetime.strptime(datetime.now().strftime(fmt), fmt)
            print(now)
            date = jsonResponse['msg4']
            print(date)

            stream = Stream(auth, CustomStreamListener(api, mongodbName, mongodbCollectionName, fileName, now, date))
            stream.filter(track=ConfigParser.word_list_for_streaming)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "streamfrominput":
        try:
            mongodbName = jsonResponse['msg1']
            mongodbCollectionName = jsonResponse['msg2']
            fileName = jsonResponse['msg3']

            auth = tweepy.OAuthHandler(ConfigParser.consumer_key, ConfigParser.consumer_secret)
            auth.set_access_token(ConfigParser.access_key, ConfigParser.access_secret)
            api = tweepy.API(auth)

            fmt = '%Y-%m-%d %H:%M:%S'
            now = datetime.strptime(datetime.now().strftime(fmt), fmt)
            print(now)
            date = jsonResponse['msg4']
            print(date)

            a = jsonResponse['msg5']
            sentence = []
            sentence.append(a)
            print(sentence)

            stream = Stream(auth, CustomStreamListener(api, mongodbName, mongodbCollectionName, fileName, now, date))
            stream.filter(track=sentence)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "crossvalidation":
        try:
            tf = TermFrequency

            numofFold = int(jsonResponse['msg1'])
            Logging.log("N for cross validation " + str(numofFold))

            numofsplit = int(jsonResponse['msg2'])
            Logging.log("number of split " + str(numofsplit))

            testSize = float(jsonResponse['msg3'])
            Logging.log("number for test size between 0 and 1 " + str(testSize))

            randomState = int(jsonResponse['msg4'])
            Logging.log("random state " + str(randomState))

            testSizeforTraintest = float(jsonResponse['msg5'])
            Logging.log("number for test size between 0 and 1 " + str(testSizeforTraintest))

            cforKernel = int(jsonResponse['msg6'])
            Logging.log("Number for C for kernel in svc " + str(cforKernel))

            tf.termfreq(ConfigParser.file_path_for_cross_val, numofFold, numofsplit, testSize, randomState,
                        testSizeforTraintest, cforKernel)
        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "termfrequency":
        try:
            inputforMostCommon = int(jsonResponse['msg1'])
            termMax = int(jsonResponse['msg2'])
            a = jsonResponse['msg3']

            TermFreqAndAllTerms.term_counter(ConfigParser.streaming_txt_file, inputforMostCommon)
            TermFreqAndAllTerms.semantic(a, ConfigParser.streaming_txt_file, inputforMostCommon, termMax)
        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        conn.send(b'I did your job bro')

    elif (jsonResponse['msg0']) == "killserver":
        print("server is closed")
        conn.close()
        break
    else:
        print("process is not recognized")
        conn.send(b'I did your job bro')

# sys.exit()
