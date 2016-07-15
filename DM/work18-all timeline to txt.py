#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import json

#Twitter API credentials
consumer_key = "consumer key "
consumer_secret = ""
access_key = ""
access_secret = ""

filepath = "directory of the output .txt files"
usernamefilepath = 'file which contains username of the users'

def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method

    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    #initialize a list to hold all the tweepy Tweets
    alltweets = []

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    #save most recent tweets
    alltweets.extend(new_tweets)

    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print ("getting tweets before %s" % (oldest))

        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

        #save most recent tweets
        alltweets.extend(new_tweets)

        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print ("...%s tweets downloaded so far" % (len(alltweets)))

    #write tweets to the txt files
    for tweet in alltweets:
        f = open(filepath+screen_name+".txt","a")
        f.write(json.dumps(tweet._json) + "\n")
    print(screen_name+"'s tweets added to file")
    pass


if __name__ == '__main__':
    #pass in the username of the account you want to download
    with open(usernamefilepath,'r') as f:
        for line in f:
            for word in line.split():
                get_all_tweets(word)