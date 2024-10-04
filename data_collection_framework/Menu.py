## Text menu in Python

def print_menu():  ## Your menu design here
    print(30 * "-", "WELCOME TO DATA COLLECTION FRAMEWORK", 30 * "-")
    print("1. Tweet Collector according to username list or username")
    print("2. Follower collector according to username list or username")
    print("3. Store your data to Mongo Database make sure your path is okay or change it from config file")
    print("4. Analysis of collected tweets for example plots which languages are used in text of tweets")
    print("5. Custom stream listener from Streaming API")
    print("6. Find Cross validation and f1 macro scoring")
    print("7. Find Term Frequency, the most common tokens, stop word, all Hastags etc...")
    print("8. Exit")
    print(67 * "-")


loop = True
while loop:  ## While loop which will keep going until loop = False
    print_menu()  ## Displays menu
    choice = int(input("Enter your choice [1-8]: "), 10)

    from data_collection_framework import Logging

    if choice == 1:
        try:
            loop2 = True
            while loop2:
                # your code
                print("Type any key to exit this option")
                cont = input("Do you want to give a username list with file path? yes/no > ")
                mongodbName = input("Please enter database name: ")
                from data_collection_framework.config import ConfigParser, ConfigParser as conf
                from data_collection_framework.TweetCollector import TweetCollector

                tweetcollect = TweetCollector()

                if cont == "yes":
                    numberOfTweet = int(input("How many tweets do you want to collect? : "), 10)
                    while cont == "yes":
                        with open(ConfigParser.file_path_for_list_of_username, 'r') as f:
                            for line in f:
                                for word in line.split():
                                    tweetcollect.get_all_tweets(word, numberOfTweet, mongodbName)

                        cont = input("\nType any key to cont \n ")
                elif cont == "no":
                    username = input("Please enter username : ")
                    numberOfTweet = int(input("How many tweets do you want to collect? : "), 10)
                    tweetcollect.get_all_tweets(username, numberOfTweet, mongodbName)
                else:
                    loop2 = False
                    print("You have exited from tweet collector succesfully...")

        except:
            import sys

            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
            continue
        ## You can add your code or functions here
    elif choice == 2:
        try:
            loop3 = True
            while loop3:
                # your code
                print("Type any key to exit this option")
                cont = input("Do you want to give a username list with file path? yes/no > ")

                from data_collection_framework.FollowerCollector import FollowerCollector
                from data_collection_framework import ConfigParser

                followercollect = FollowerCollector()
                if cont == "yes":
                    with open(ConfigParser.file_path_for_list_of_username, 'r') as f:
                        for line in f:
                            for word in line.split():
                                followercollect.write_on_file(word)

                    cont = input("Do you want to give a username list with file path? yes/no > ")
                elif cont == "no":
                    username = input("Please enter username to collect followers: ")
                    followercollect.write_on_file(username)
                else:
                    loop3 = False
                    print("You have exited from follower collector succesfully...")

        except:
            import sys

            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))

        ## You can add your code or functions here
    elif choice == 3:
        try:
            from data_collection_framework.MongoWriter import MongoWriter
            from data_collection_framework import ConfigParser

            mongodbName = input("Please enter database name to store : ")

            mongodbCollectionName = input("Please enter collection name inside database : ")

            mongoWrite = MongoWriter()
            mongoWrite.writetoMongo(ConfigParser.file_path_for_mongo, mongodbName, mongodbCollectionName)

        except:
            import sys

            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
    elif choice == 4:
        try:
            def print_menu2():  ## Your menu design here
                print(30 * "-", "MENU", 30 * "-")
                print("1. If you want to plot Language analysis please press 1")
                print("2. If you want to plot Country analysis please press 2")
                print("3. If you want to plot Location analysis please press 3")
                print("4. If you want to plot Timezone analysis please press 4")
                print("5. If you want to plot Tweet analysis please press 5")
                print("6. If you want to plot Tweet Create at analysis please press 6")
                print("7. If you want to plot User ID analysis please press 7")
                print("8. If you want to plot String of ID analysis please press 8")
                print("9. If you want to plot Username analysis please press 9")
                print("10. If you want to plot ScreenName analysis please press 10")
                print("11. If you want to plot Followers_Count analysis please press 11")
                print("12. If you want to plot Friends_Count analysis please press 12")
                print("13. If you want to plot User Language analysis please press 13")
                print("14. If you want to plot Retweet Count analysis please press 14")
                print("15. If you want to plot Favorite Count analysis please press 15")
                print("16. Exit")
                print(67 * "-")


            loop1 = True

            while loop1:  ## While loop which will keep going until loop = False
                print_menu2()  ## Displays menu
                choice = int(input("Enter your choice [1-16]: "))

                from data_collection_framework.Analysis import Analysis
                from data_collection_framework import ConfigParser

                analysis = Analysis()

                if choice == 1:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    ## You can add your code or functions here
                    analysis.lang_analiz(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 2:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.country_analiz(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 3:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.location_analiz(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 4:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.timezone_analiz(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 5:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.tweet(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 6:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.create_at(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 7:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.user_id(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 8:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.id_str(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 9:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.username(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 10:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.screename(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 11:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.followers_count(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 12:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.friends_count(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 13:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.user_lang(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 14:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.retweet_count(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 15:
                    numberOfBar = int(input("How many bars do you want to see in your plot? : "), 10)
                    analysis.favorite_count(ConfigParser.file_path_for_mongo, numberOfBar)
                elif choice == 16:
                    print("You have exited from analysis succesfully...")
                    ## You can add your code or functions here
                    loop1 = False  # This will make the while loop to end as not value of loop is set to False
                else:
                    # Any integer inputs other than values 1-5 we print an error message
                    input("Wrong option selection. Enter any key to try again..")
        except:
            import sys

            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
    elif choice == 5:
        try:
            mongodbName = input("Please enter database name to store : ")
            mongodbCollectionName = input("Please enter collection name inside database : ")
            fileName = input("Please enter file name : ")

            import tweepy
            from data_collection_framework.CustomStreamListener import CustomStreamListener

            auth = tweepy.OAuthHandler(conf.consumer_key, conf.consumer_secret)
            auth.set_access_token(conf.access_key, conf.access_secret)
            api = tweepy.API(auth)

            from datetime import datetime

            fmt = '%Y-%m-%d %H:%M:%S'
            now = datetime.strptime(datetime.now().strftime(fmt), fmt)
            print(now)
            date = input("Enter date which is greater than " + now.strftime(fmt) + " which is current time : ")
            print(date)

            a = input("Enter a word, hashtag or something else or type STOP to start colleting tweets: ")
            sentence = []
            # while a != ("stop"):
            sentence.append(a)
            #    a = input("Enter a word, hashtag or something else or type STOP to start colleting tweets: ")
            print(sentence)
            print(conf.word_list_for_streaming)

            from tweepy import Stream

            stream = Stream(auth, CustomStreamListener(api, mongodbName, mongodbCollectionName, fileName, now, date))
            stream.filter(track=conf.word_list_for_streaming)

        except:
            import sys

            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
    elif choice == 6:
        try:
            from data_collection_framework.CrossValidation import TermFrequency

            tf = TermFrequency
            from data_collection_framework import ConfigParser

            numofFold = int(input("Enter number for N for cross validation? : "), 10)
            Logging.log("N for cross validation " + str(numofFold))
            numofsplit = int(input("Enter number of split? : "), 10)
            Logging.log("number of split " + str(numofsplit))
            testSize = float(input("Enter number for test size between 0 and 1? it might be 0.3 : "))
            Logging.log("number for test size between 0 and 1 " + str(testSize))
            randomState = int(input("Enter random state you might enter 0(zero)? : "), 10)
            Logging.log("random state " + str(randomState))
            testSizeforTraintest = float(
                input("Enter number for test size between 0 and 1? you might enter 0.4 or 0.6 : "))
            Logging.log("number for test size between 0 and 1 " + str(testSizeforTraintest))
            cforKernel = int(input("Enter number for C for kernel in svc you might enter 1(one)? : "), 10)
            Logging.log("Number for C for kernel in svc " + str(cforKernel))

            tf.termfreq(ConfigParser.file_path_for_cross_val, numofFold, numofsplit, testSize, randomState,
                        testSizeforTraintest, cforKernel)

        except:
            import sys

            e = sys.exc_info()[1]
            print("Error: %s" % e)
            Logging.log(str(e))
        ## You can add your code or functions here
    elif choice == 7:
        try:
            from data_collection_framework.TermFreqAndAllTerms import TermFreqAndAllTerms
            from data_collection_framework import ConfigParser

            inputforMostCommon = int(
                input("Enter number to display the most frequent words (or tokens), are not exactly meaningful: "))
            termMax = int(input("Enter number to print top of maximum term : "))

            a = input("Enter a word, hashtag or something else to find Co-occurrence or type stop to exit: ")

            TermFreqAndAllTerms.term_counter(ConfigParser.streaming_txt_file, inputforMostCommon)
            TermFreqAndAllTerms.semantic(a, ConfigParser.streaming_txt_file, inputforMostCommon, termMax)

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
