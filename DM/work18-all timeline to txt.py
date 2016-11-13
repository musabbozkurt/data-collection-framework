#!/usr/bin/env python
# encoding: utf-8
import os
import string
import pymongo
from pymongo import MongoClient
import tweepy #https://github.com/tweepy/tweepy
import json
import glob

from sklearn import cross_validation
from sklearn.feature_extraction.text import TfidfVectorizer
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.naive_bayes import MultinomialNB
from sklearn import cross_validation, svm


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

class TokenizationTextFile():
    def tokenTextFile(filepath):
        import re

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
            tokens = tokens_re.findall(s)
            if lowercase:
                tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
            return tokens

        filenames = glob.glob(filepath)
        tweets_data = []
        for file in filenames:
            with open(file) as f:
                for line in f:
                    try:
                        tweet = json.loads(line)
                        tweets_data.append(tweet)
                        tweet = json.loads(line)
                        tokens = NGrams.ngrams(tweet['text'],3)
                        # print(tokens)
                    except:
                        continue
            print(len(tweets_data))
            tweets = pd.DataFrame()
            tweets['text'] = map(lambda tweet: tweet['text'], tweets_data)
            tweets['location'] = map(lambda tweet: tweet['location'], tweets_data)
            tweets['lang'] = map(lambda tweet: tweet['lang'], tweets_data)
            tweets['country'] = map(lambda tweet: tweet['place']['country'] if tweet['place'] != None else None,tweets_data)
            tweets_by_lang = tweets['lang'].value_counts()
            tweets_by_location = tweets['location'].value_counts()

            fig, ax = plt.subplots()
            ax.tick_params(axis='x', labelsize=15)
            ax.tick_params(axis='y', labelsize=10)
            ax.set_xlabel('Languages', fontsize=15)
            ax.set_ylabel('Number of tweets', fontsize=15)
            ax.set_title('Top 5 languages', fontsize=15, fontweight='bold')
            # tweets_by_lang[:5].plot(ax=ax, kind='bar', color='red')
            tweets_by_location[:5].plot(ax=ax, kind='bar', color='red')
            plt.show()


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

                NGrams.ngrams(file_content, 2)
                fileNames.append(file_path)
                classLabels.append(subdir[15:])
        tfidf = TfidfVectorizer(tokenizer=NGrams.ngrams(file_content, 2), preprocessor=TermFrequency.preprocess, lowercase=True)
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

        import numpy as np
        X = np.array(X_train)
        y = np.array(y_train)
        X2 = np.array(X_test)
        y2 = np.array(y_test)

        print(X.shape, y.shape, X2.shape, y2.shape)

        from sklearn.model_selection import cross_val_score
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

        from sklearn import metrics
        scores = cross_val_score(clf, docTermMatrix, classLabels, cv=15, scoring='f1_macro')

        # test accuracy 1 0 arasi
        print('f1_macro scoring : ', scores)

        from sklearn.model_selection import ShuffleSplit
        n_samples = docTermMatrix.shape[0]
        cv = ShuffleSplit(n_splits=10, test_size=0.3, random_state=0)
        print(cross_val_score(clf, docTermMatrix, classLabels, cv=cv))

        from sklearn.model_selection import cross_val_predict
        predicted = cross_val_predict(clf, docTermMatrix, classLabels, cv=10)
        print('10-fold cross validation : ', metrics.accuracy_score(classLabels, predicted))


class NGrams():
    def ngrams(input, n):
        input = input.split(' ')
        output = {}
        for i in range(len(input) - n + 1):
            g = ' '.join(input[i:i + n])
            output.setdefault(g, 0)
            output[g] += 1
        # print(output)


if __name__ == '__main__':
    # pass in the username of the account you want to download

    # with open(AllVariableClass.ListOfUsernamefilepath,'r') as f:
        try:
    #         for line in f:
    #               for word in line.split():
    #                  TweetCollector.get_all_tweets(word)
    #                  FollowerCollector().write_on_file(word)
    #       CustomStreamListener.on_sapi(['ygs', 'indian'])
            TermFrequency.termfreq(AllVariableClass.filepathfortokenization)
        except:
    #         print(str(IOError))
            pass
    # MongoWriter.writetoMongo(AllVariableClass.filepathformongo)
    # CustomStreamListener.on_sapi(['ygs', 'indian'])
    # TokenizationTextFile.tokenTextFile(AllVariableClass.filepathformongo)
    # TermFrequency.termfreq(AllVariableClass.filepathfortokenization)
