import configparser

configParser = configparser.RawConfigParser()
configFilePath = r'/enter your config file path'
configParser.read(configFilePath)

filePathForTimelineOutputs = configParser.get('your-config', 'filePathForTimelineOutputs')
# print(filePathForOutputs)

filePathForFollowersOutputs = configParser.get('your-config', 'filePathForFollowersOutputs')
# print(filePathForFollowersOutputs)

filePathForListOfUsername = configParser.get('your-config', 'filePathForListOfUsername')
# print(filePathForListOfUsername)

filePathForMongo = configParser.get('your-config', 'filePathForMongo')
# print(filePathForMongo)

filePathForTokenization = configParser.get('your-config', 'filePathForTokenization')
# print(filePathForTokenization)

streamingTxtFile = configParser.get('your-config', 'streamingTxtFile')
# print(streamingTxtFile)

consumer_key = configParser.get('your-config', 'consumer_key')
# print(consumer_key)

consumer_secret = configParser.get('your-config', 'consumer_secret')
# print(consumer_secret)

access_key = configParser.get('your-config', 'access_key')
# print(access_key)

access_secret = configParser.get('your-config', 'access_secret')
# print(access_secret)

streamingDB = configParser.get('your-config', 'streamingDB')
# print(streamingDB)

emoticons_str = configParser.get('your-config', 'emoticons_str')
# print(emoticons_str)

HTML_tags = configParser.get('your-config', 'HTML_tags')
# print(HTML_tags)

mentions = configParser.get('your-config', 'mentions')
# print(mentions)

hash_tags = configParser.get('your-config', 'hash_tags')
# print(hash_tags)

URLs = configParser.get('your-config', 'URLs')
# print(URLs)

numbers = configParser.get('your-config', 'numbers')
# print(numbers)

words_with = configParser.get('your-config', 'words_with')
# print(words_with)

other_words = configParser.get('your-config', 'other_words')
# print(other_words)

anything_else = configParser.get('your-config', 'anything_else')
# print(anything_else)

positive_vocab = configParser.get('your-config', 'positive_vocab')
# print(positive_vocab)

negative_vocab = configParser.get('your-config', 'negative_vocab')
# print(negative_vocab)

wordListForStreaming = configParser.get('your-config', 'wordListForStreaming')
# print(wordListForStreaming)

filePathForCrossVal = configParser.get('your-config', 'filePathForCrossVal')
