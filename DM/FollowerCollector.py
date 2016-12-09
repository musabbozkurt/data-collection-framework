import AllVariableClass
import GraduationProject


#
class FollowerCollector():
    def write_on_file(self,screenname):
        try:
            for follower in AllVariableClass.api.followers_ids(screenname):
                with open(AllVariableClass.filePathForFollowersOutputs + screenname + ".txt", "a") as f:
                    f.write(AllVariableClass.api.get_user(follower).screen_name + ' \n')
            GraduationProject.logger.info("FollowerCollector is collected followers of " + screenname + "and added to " + screenname + ".txt")
        except:
            print(screenname+str(IOError))
            GraduationProject.logger.error("Screen name : " + screenname + " with error " + str(Exception))
            pass

    def on_error(self, status_code):
        GraduationProject.logger.error("Don't kill the followerCollector. error status code : " + status_code)
        return True # Don't kill the followerCollector

    def on_timeout(self):
        GraduationProject.logger.error("Don't kill the followerCollector on timeouts")
        return True # Don't kill the followerCollector

