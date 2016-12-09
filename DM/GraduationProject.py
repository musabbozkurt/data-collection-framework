def get_log():
    import logging

    logger = logging.getLogger('PyPro')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('pypro.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)

    # create formatter and add it to the handlers
    fhFormatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    chFormatter = logging.Formatter('%(levelname)s - %(filename)s - Line: %(lineno)d - %(message)s')
    fh.setFormatter(fhFormatter)
    ch.setFormatter(chFormatter)

    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    logger.info("-----------------------------------")
    logger.info("Log system successfully initialised")
    logger.info("-----------------------------------")

    return logger

logger = get_log()


if __name__ == '__main__':
    try:
        from DM import ConfigParser
        from DM.TweetCollector import TweetCollector
        from DM.FollowerCollector import FollowerCollector

        # from DM import CustomStreamListener,Analysis,TermFrequency
        # from DM import SemanticOrientation
        # # pass in the username of the account you want to download
        #
        tweetcollect = TweetCollector()
        followercollect= FollowerCollector()

        numberOfTweet=int(input("How many tweets do you want to collect? : "),10)

        with open(ConfigParser.ListOfUsernamefilepath, 'r') as f:
                 for line in f:
                       for word in line.split():
        #                  tweetcollect.get_all_tweets(word, numberOfTweet)
                          followercollect.write_on_file(word)
        #MongoWriter.writetoMongo(ConfigParser.filepathformongo)
        #CustomStreamListener.on_sapi(['#python','java','#java','javascript','#javascript'])
        #Analysis.lang_analiz(ConfigParser.streamingTxtFile)
        #Analysis.country_analiz(ConfigParser.streamingTxtFile)
        #Analysis.location_analiz(ConfigParser.streamingTxtFile)
        #Analysis.timezone_analiz(ConfigParser.streamingTxtFile)
        #TermFrequency.termfreq(ConfigParser.filepathfortokenization)
        #SemanticOrientation.term_counter()
        #SemanticOrientation.semantic('java',ConfigParser.streamingTxtFile)
        #Analysis.lang(ConfigParser.streamingTxtFile)
        #Analysis.lang(ConfigParser.filepathfortokenization)
        #Analysis.screename(ConfigParser.filepathfortokenization)
    except:
        import sys
        e = sys.exc_info()[0]
        print("Error: %s" % e)
        logger.error(str(e))
