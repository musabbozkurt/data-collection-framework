import configparser

configParser = configparser.RawConfigParser()
configFilePath = r'/Users/musabbozkurt/PycharmProjects/DM/abc.config'
configParser.read(configFilePath)

filePathForOutputs = configParser.get('your-config', 'filePathForOutputs')
print(filePathForOutputs)

filePathForFollowersOutputs = configParser.get('your-config', 'filePathForFollowersOutputs')
print(filePathForFollowersOutputs)

ListOfUsernamefilepath = configParser.get('your-config', 'ListOfUsernamefilepath')
print(ListOfUsernamefilepath)

filepathformongo = configParser.get('your-config', 'filepathformongo')
print(filepathformongo)

filepathfortokenization = configParser.get('your-config', 'filepathfortokenization')
print(filepathfortokenization)

streamingTxtFile = configParser.get('your-config', 'streamingTxtFile')
print(streamingTxtFile)

consumer_key = configParser.get('your-config', 'consumer_key')
print(consumer_key)

consumer_secret = configParser.get('your-config', 'consumer_secret')
print(consumer_secret)

access_key = configParser.get('your-config', 'access_key')
print(access_key)

access_secret = configParser.get('your-config', 'access_secret')
print(access_secret)

streamingdb = configParser.get('your-config', 'streamingdb')
print(streamingdb)

emoticons_str = configParser.get('your-config', 'emoticons_str')
print(emoticons_str)

regex_str = configParser.get('your-config', 'regex_str')
print(regex_str)

positive_vocab = configParser.get('your-config', 'positive_vocab')
print(positive_vocab)

negative_vocab = configParser.get('your-config', 'negative_vocab')
print(negative_vocab)