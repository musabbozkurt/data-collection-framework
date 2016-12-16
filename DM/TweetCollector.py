
# getting all tweets in users timeline according to their username.

class TweetCollector():
        def get_all_tweets(self,screen_name,input):
            try:
                import json

                from DM import Logging
                from DM import ConfigParser
                from DM.AllVariableClass import AllVariableClass

                allclassvar=AllVariableClass()
                #Twitter only allows access to a users most recent 3240 tweets with this method

                #initialize a list to hold all the tweepy Tweets
                alltweets = []

                #make initial request for most recent tweets (200 is the maximum allowed count)
                new_tweets = allclassvar.api.user_timeline(screen_name = screen_name, count=200)

                #save most recent tweets
                alltweets.extend(new_tweets)

                #save the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1

                #keep grabbing tweets until there are no tweets left to grab
                while (len(new_tweets) > 0):
                    print ("getting tweets before %s" % (oldest))

                    #all subsiquent requests use the max_id param to prevent duplicates
                    new_tweets = allclassvar.api.user_timeline(screen_name = screen_name, count=200, max_id=oldest)

                    #save most recent tweets
                    alltweets.extend(new_tweets)

                    #update the id of the oldest tweet less one
                    oldest = alltweets[-1].id - 1

                    print ("...%s tweets downloaded so far" % (len(alltweets)))
                    if (len(alltweets)) >= input:
                        Logging.log(str(input)+" tweets have been collected")
                        break
                #write tweets to the txt files
                for tweet in alltweets:
                    f = open(ConfigParser.filePathForOutputs + screen_name + ".txt", "a")
                    f.write(json.dumps(tweet._json) + "\n")
                print(screen_name+"'s tweets added to file")
                Logging.log("Tweets have been added to " + screen_name + ".txt")
                pass
            except:
                import sys

                e = sys.exc_info()[1]
                print("Error: %s" % e)
                Logging.log(str(e))
                pass

        def on_error(self, status_code):
            from DM import Logging
            Logging.log("Don't kill the collector here status code is : " + status_code)
            return True  # Don't kill the collector

        def on_timeout(self):
            from DM import Logging

            Logging.log("Don't kill the collector on timeouts.")
            return True  # Don't kill the collector

