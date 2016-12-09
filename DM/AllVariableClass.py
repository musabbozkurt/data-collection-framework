import tweepy
from pymongo import MongoClient

import ConfigParser as conf


#from DM import GraduationProject as grad


class AllVariableClass:
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(conf.consumer_key, conf.consumer_secret)
    auth.set_access_token(conf.access_key, conf.access_secret)
    api = tweepy.API(auth)
    print(conf.access_key)

    # create mongodb database
    client = MongoClient()
    db = client.twitter3

    # Now, we can log to the root logger, or any other logger. First the root...
    #grad.logger.info('Variable has been called from AllClassVariable')

