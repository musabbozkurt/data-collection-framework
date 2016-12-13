import tweepy
from DM import ConfigParser as conf
from DM import Logging

class AllVariableClass:
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(conf.consumer_key, conf.consumer_secret)
    auth.set_access_token(conf.access_key, conf.access_secret)
    api = tweepy.API(auth)
    #print(conf.access_key)

    # Now, we can log to the root logger, or any other logger. First the root...
    Logging.log('Variable has been called from AllClassVariable')

