
#
class FollowerCollector():
    def write_on_file(self,screenname):
        from DM.AllVariableClass import AllVariableClass
        from DM import GraduationProject
        from DM import ConfigParser
        import sys
        allclassvar=AllVariableClass()
        try:
            for follower in allclassvar.api.followers_ids(screenname):
                with open(ConfigParser.filePathForFollowersOutputs + screenname + ".txt", "a") as f:
                    f.write(allclassvar.api.get_user(follower).screen_name + ' \n')
            GraduationProject.logger.info("FollowerCollector is collected followers of " + screenname + "and added to " + screenname + ".txt")
        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)
            GraduationProject.logger.error("Screen name : " + screenname + " with error " + str(e))
            pass

    def on_error(self, status_code):
        from DM import GraduationProject

        GraduationProject.logger.error("Don't kill the followerCollector. error status code : " + status_code)
        return True # Don't kill the followerCollector

    def on_timeout(self):
        from DM import GraduationProject

        GraduationProject.logger.error("Don't kill the followerCollector on timeouts")
        return True # Don't kill the followerCollector

