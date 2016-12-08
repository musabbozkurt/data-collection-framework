
import logging

def get_log():
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



from DM import ConfigParser,TweetCollector,FollowerCollector,MongoWriter
from DM import CustomStreamListener,Analysis,TermFrequency
from DM import SemanticOrientation

if __name__ == '__main__':
    # # pass in the username of the account you want to download
    #
    with open(ConfigParser.ListOfUsernamefilepath,'r') as f:
             for line in f:
                   for word in line.split():
                      TweetCollector.get_all_tweets(word)
                      FollowerCollector().write_on_file(word)
    MongoWriter.writetoMongo(ConfigParser.filepathformongo)
    CustomStreamListener.on_sapi(['#python','java','#java','javascript','#javascript'])
    Analysis.lang_analiz(ConfigParser.streamingTxtFile)
    Analysis.country_analiz(ConfigParser.streamingTxtFile)
    Analysis.location_analiz(ConfigParser.streamingTxtFile)
    Analysis.timezone_analiz(ConfigParser.streamingTxtFile)
    TermFrequency.termfreq(ConfigParser.filepathfortokenization)
    SemanticOrientation.term_counter()
    SemanticOrientation.semantic('java',ConfigParser.streamingTxtFile)
    Analysis.lang(ConfigParser.streamingTxtFile)
    Analysis.lang(ConfigParser.filepathfortokenization)
    Analysis.screename(ConfigParser.filepathfortokenization)
