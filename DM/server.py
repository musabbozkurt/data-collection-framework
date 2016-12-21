#!/usr/bin/env python
import sys
import tweepy
import json
import socket

import time
import argparse
import string

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host= '127.0.0.1'
port=5555
socksize=1024
s.bind((host,port))


while True:
    from DM import Logging
    from DM import ConfigParser
    from DM.TweetCollector import TweetCollector
    from DM.FollowerCollector import FollowerCollector
    from DM.MongoWriter import MongoWriter
    from DM.Analysis import Analysis
    import tweepy
    from DM import ConfigParser as conf
    from DM.CustomStreamListener import CustomStreamListener
    from datetime import datetime
    from tweepy import Stream
    from DM.CrossValidation import TermFrequency
    from DM.TermFreqAndAllTerms import TermFreqAndAllTerms

    print("Now listening...\n")
    s.listen(5)
    conn, addr = s.accept()

    print ('New connection from %s:%d' % (addr[0], addr[1]))
    data = conn.recv(socksize)
    jsonResponse=(json.loads(data))
    print(jsonResponse)

    
    if (jsonResponse['msg0'])=="collecttweetfromuserlist":
        try:
            tweetcollect = TweetCollector()
            numberOfTweet = jsonResponse['msg1']
            with open(ConfigParser.ListOfUsernamefilepath, 'r') as f:
                for line in f:
                    for word in line.split():
                        tweetcollect.get_all_tweets(word, numberOfTweet)
        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        count=0
        conn.send(str(count))
        print("server works: data="+data)
    elif (jsonResponse['msg0'])=="collecttweetfromusername":
        try:
            tweetcollect = TweetCollector()
            username = jsonResponse['msg1']
            numberOfTweet = jsonResponse['msg2']
            tweetcollect.get_all_tweets(username, numberOfTweet)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        count=0
        conn.send(str(count))
    elif (jsonResponse['msg0']) == 'collectfollowerfromuserlist':
        try:
            followercollect = FollowerCollector()
            with open(ConfigParser.ListOfUsernamefilepath, 'r') as f:
                for line in f:
                    for word in line.split():
                        followercollect.write_on_file(word)
        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="collectfollowerfromusername":
        try:
            followercollect = FollowerCollector()
            username = jsonResponse['msg1']
            followercollect.write_on_file(username)

        except:
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="storedata":
        try:
                mongodbName = jsonResponse['msg1']
                mongodbCollectionName = jsonResponse['msg2']

                mongoWrite = MongoWriter()
                mongoWrite.writetoMongo(ConfigParser.filepathformongo,mongodbName,mongodbCollectionName)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))
        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotlanguage":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.lang_analiz(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotcountry":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.country_analiz(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotlocation":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.location_analiz(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plottimezone":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.timezone_analiz(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plottweet":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.tweet(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plottweetcreatedat":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.create_at(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotuserid":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.user_id(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotstringofid":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.id_str(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotusername":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.username(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotscreenname":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.screename(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotfollowerscount":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.followers_count(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotfriendscount":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.friends_count(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotuserlanguage":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.user_lang(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotretweet":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.retweet_count(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="plotfavourite":
        try:
                analysis = Analysis()
                numberOfBar = jsonResponse['msg1']
                analysis.favorite_count(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="stream":
        try:
                mongodbName = jsonResponse['msg1']
                mongodbCollectionName = jsonResponse['msg2']
                fileName = jsonResponse['msg3']

                auth = tweepy.OAuthHandler(conf.consumer_key, conf.consumer_secret)
                auth.set_access_token(conf.access_key, conf.access_secret)
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

                stream = Stream(auth,CustomStreamListener(api, mongodbName, mongodbCollectionName, fileName, now, date))
                stream.filter(track=sentence)


                analysis.favorite_count(ConfigParser.filepathformongo, numberOfBar)

        except:
                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))

        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="crossvalidation":
        #gerekli fonsiyon
        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="termfrequency":
        #gerekli fonsiyon
        count=0
        conn.send(str(count))

    elif (jsonResponse['msg0'])=="killserver":
        print("server is closed")
        conn.close()
        break
    else:
        print("process is not recognized")
    print(data)
    conn.send(str("process is not recognized"))

#sys.exit()
