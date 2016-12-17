import pymongo
from tweepy.streaming import StreamListener
from DM import Logging
from DM import ConfigParser

#this class helps us to use streaming API according to given date
class CustomStreamListener(StreamListener):
    def __init__(self, api, mongodbName, mongodbCollectionName, fileName, datenow, date2):
        self.api=api
        super(CustomStreamListener, self).__init__()
        #initializing our database name which is given by users as an input
        self.mongodbName=mongodbName
        #initializing our collection name which is given by users as an input
        self.mongodbCollectionName=mongodbCollectionName
        ##initializing our file name which is given by users as an input.
        #this file will contains tweets which will be collected from Streaming API
        self.fileName=fileName
        #we need datenow variable to get current time as hour and minute
        #  with year-month-day for example 2016-12-15 14:00
        self.datenow=datenow
        #we will use date2 variable as parameter which will be given by users
        # just like datenow variable
        self.date2=date2
    #this function controlling Streaming API according to date and adds our tweets into mongoDB
    def on_status(self, status):
        #this record variable will have some fields from tweets json
        record = {'Text': status.text, 'Created At': status.created_at}
        print(record)
        fmt = '%Y-%m-%d %H:%M:%S'
        from datetime import datetime
        #this if statement is controlling Streaming API according to date
        if ((datetime.strptime(self.date2 , fmt)-self.datenow).total_seconds()!=0) \
                and ((datetime.strptime(self.date2 , fmt)-self.datenow).total_seconds()>0):
            print((datetime.strptime(self.date2 , fmt)-self.datenow).total_seconds())
            self.datenow=datetime.strptime(datetime.now().strftime(fmt), fmt)
            # See Tweepy documentation to learn how to access other fields
            self.db = pymongo.MongoClient().__getattr__(self.mongodbName).__getattr__(self.mongodbCollectionName).insert(record)
            Logging.log(self.mongodbName + " database has been created. and insertion get started")
            Logging.log("Tweets which are collecting from Streaming API added to " + ConfigParser.streamingTxtFile + " filepath")
            Logging.log("Tweets which are collecting from Streaming API added to " + self.mongodbCollectionName + " inside " + self.mongodbName + "mongodb database")
            return True
        elif((datetime.strptime(self.date2 , fmt)-self.datenow).total_seconds()<=0):
            print((datetime.strptime(self.date2, fmt) - self.datenow).days)
            Logging.log("you have finished ")
            return False
        else:
            print((datetime.strptime(self.date2, fmt) - self.datenow).days)
            print("asdlkjasdjkalsd")
            return False
    #these message below will occur if Streaming API interrupts or limited or timeout
    def on_error(self, status):
        print ('Error on status', status)
        Logging.log('Error on status'+status)

    def on_limit(self, status):
        print ('Limit threshold exceeded', status)
        Logging.log('Limit threshold exceeded', status)

    def on_timeout(self, status):
        print ('Stream disconnected; continuing...')
        Logging.log('Stream disconnected; continuing...')

