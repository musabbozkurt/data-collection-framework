## Text menu in Python

def print_menu():  ## Your menu design here
    print(30 * "-", "MENU", 30 * "-")
    print("1. Tweet Collector according to username list or username")
    print("2. Follower collector according to username list or username")
    print("3. Store your data to Mongo Database")
    print("4. Analysis of collected tweets")
    print("5. Custom stream listener from twitter API")
    print("6. Find Term frequency")
    print("7. Semantic orientation of tweets json which are collected from Streaming API")
    print("8. Exit")
    print(67 * "-")
loop = True
while loop:  ## While loop which will keep going until loop = False
    print_menu()  ## Displays menu
    choice = int(input("Enter your choice [1-8]: "),10)

    from DM import Logging

    if choice == 1:
        try:
            while True:
                # your code
                cont = input("Do you want to give a username list with file path? yes/no > ")

                from DM import ConfigParser
                from DM.TweetCollector import TweetCollector

                tweetcollect = TweetCollector()

                while cont.lower() not in ("yes", "no"):
                    with open(ConfigParser.ListOfUsernamefilepath, 'r') as f:
                        for line in f:
                            for word in line.split():
                                tweetcollect.get_all_tweets(word, numberOfTweet)

                    cont = input("Do you want to give a username list with file path? yes/no > ")
                if cont == "no":
                        username=input("Please enter username : ")
                        numberOfTweet = int(input("How many tweets do you want to collect? : "), 10)
                        tweetcollect.get_all_tweets(username, numberOfTweet)
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        break
        ## You can add your code or functions here
    elif choice == 2:
        try:
            while True:
                # your code

                from DM.FollowerCollector import FollowerCollector
                from DM import ConfigParser

                followercollect = FollowerCollector()
                cont = input("Do you want to give a username list with file path? yes/no > ")
                while cont.lower() not in ("yes", "no"):
                    with open(ConfigParser.ListOfUsernamefilepath, 'r') as f:
                        for line in f:
                            for word in line.split():
                                followercollect.write_on_file(word)

                cont = input("Do you want to give a username list with file path? yes/no > ")
                if cont == "no":
                    username = input("Please enter username to collect followers: ")
                    followercollect.write_on_file(username)
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
            break

        ## You can add your code or functions here
    elif choice == 3:
        try:
            from DM.MongoWriter import MongoWriter
            from DM import ConfigParser

            mongoWrite = MongoWriter()
            mongoWrite.writetoMongo(ConfigParser.filepathformongo)

        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
    elif choice == 4:
        try:
            from DM.Analysis import Analysis
            from DM import ConfigParser

            analysis = Analysis()

            analysis.lang_analiz(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.country_analiz(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.location_analiz(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.timezone_analiz(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.tweet(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.create_at(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.user_id(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.id_str(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.username(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.screename(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.followers_count(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.friends_count(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.user_lang(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.retweet_count(ConfigParser.filepathformongo, Analysis.numberOfBar)
            analysis.favorite_count(ConfigParser.filepathformongo, Analysis.numberOfBar)
        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
    elif choice == 5:
        try:

            mongodbName = input("Please enter database name to store : ")

            mongodbCollectionName = input("Please enter collection name inside database : ")

            a = input("Enter a word, hashtag or something else or type stop to exit: ")
            sentence = []
            while a != ("stop"):
                sentence.append(a)
                a = input("Enter a word, hashtag or something else or type stop to exit: ")
            print(sentence)

            from DM.CustomStreamListener import CustomStreamListener
            from DM import AllVariableClass

            csl = CustomStreamListener(AllVariableClass.api)

            csl.on_sapi(sentence)

        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
    elif choice == 6:
        try:
            from DM.TermFrequency import TermFrequency
            tf = TermFrequency
            from DM import ConfigParser

            tf.termfreq(ConfigParser.filepathfortokenization)

        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        ## You can add your code or functions here
    elif choice == 7:
        try:
            from DM import SemanticOrientation

            SemanticOrientation.term_counter()
            SemanticOrientation.semantic('java', ConfigParser.streamingTxtFile)

        except:
            import sys
            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
    elif choice == 8:
        print("We hope you enjoyed our program...\nGoodbye...")

        ## You can add your code or functions here
        loop = False  # This will make the while loop to end as not value of loop is set to False
    else:
        # Any integer inputs other than values 1-5 we print an error message
        input("Wrong option selection. Enter any key to try again..")