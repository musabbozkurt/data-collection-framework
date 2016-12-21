
#this class collecting users followers
class FollowerCollector():
    #this method writes users followers to the file and file name is named by screen name of the user
    def write_on_file(self,screenname,mongodbName="Followers"):
        from DM.AllVariableClass import AllVariableClass
        from DM import Logging
        from DM import ConfigParser
        import sys
        try:
            for follower in AllVariableClass.api.followers_ids(screenname):
                with open(ConfigParser.filePathForFollowersOutputs + screenname + ".txt", "a") as f:
                    try:
                        follower_name = {'Follower of '+screenname: AllVariableClass.api.get_user(follower).screen_name}
                        f.write(AllVariableClass.api.get_user(follower).screen_name + ' \n')
                        import pymongo
                        self.db = pymongo.MongoClient().__getattr__(mongodbName).__getattr__(screenname).insert(follower_name)
                    except:
                        import sys
                        e = sys.exc_info()[1]
                        print("Error: %s" % e)
                        Logging.log(str(e))
                        pass
            Logging.log("FollowerCollector collected followers of " + screenname + " and added to " + screenname + ".txt")
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)
            Logging.log("Screen name : " + screenname + " with error " + str(e))
            pass

    def on_error(self, status_code):
        from DM import Logging

        Logging.log("Don't kill the followerCollector. error status code : " + status_code)
        return True # Don't kill the followerCollector

    def on_timeout(self):
        from DM import Logging

        Logging.log("Don't kill the followerCollector on timeouts")
        return True # Don't kill the followerCollector

