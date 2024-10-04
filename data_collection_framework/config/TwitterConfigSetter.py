import tweepy
from data_collection_framework.config import ConfigParser as Config
from data_collection_framework import Logging


class TwitterConfigSetter:
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(Config.consumer_key, Config.consumer_secret)
    auth.set_access_token(Config.access_key, Config.access_secret)
    api = tweepy.API(auth)
    # print(conf.access_key)

    # Now, we can log to the root logger, or any other logger. First the root...
    Logging.log('Variable has been called from AllClassVariable')
