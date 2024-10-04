import configparser
import sys

configParser = configparser.RawConfigParser()
configParser.read('ConfigFile.config')
sys_path = sys.path[1]
print(sys_path)

file_path_for_timeline_outputs = sys_path + configParser.get('your-config', 'file_path_for_timeline_outputs')
print(file_path_for_timeline_outputs)

file_path_for_followers_outputs = sys_path + configParser.get('your-config', 'file_path_for_followers_outputs')
print(file_path_for_followers_outputs)

file_path_for_list_of_username = sys_path + configParser.get('your-config', 'file_path_for_list_of_username')
print(file_path_for_list_of_username)

file_path_for_mongo = sys_path + configParser.get('your-config', 'file_path_for_mongo')
print(file_path_for_mongo)

file_path_for_tokenization = sys_path + configParser.get('your-config', 'file_path_for_tokenization')
print(file_path_for_tokenization)

file_path_for_cross_val = sys_path + configParser.get('your-config', 'file_path_for_cross_val')
print(file_path_for_cross_val)

streaming_txt_file = sys_path + configParser.get('your-config', 'streaming_txt_file')
print(streaming_txt_file)

streaming_db = sys_path + configParser.get('your-config', 'streaming_db')
print(streaming_db)

consumer_key = configParser.get('your-config', 'consumer_key')
print(consumer_key)

consumer_secret = configParser.get('your-config', 'consumer_secret')
print(consumer_secret)

access_key = configParser.get('your-config', 'access_key')
print(access_key)

access_secret = configParser.get('your-config', 'access_secret')
print(access_secret)

word_list_for_streaming = configParser.get('your-config', 'word_list_for_streaming')
print(word_list_for_streaming)

emoticons_str = configParser.get('your-config', 'emoticons_str')
print(emoticons_str)

html_tags = configParser.get('your-config', 'html_tags')
print(html_tags)

mentions = configParser.get('your-config', 'mentions')
print(mentions)

hash_tags = configParser.get('your-config', 'hash_tags')
print(hash_tags)

urls = configParser.get('your-config', 'urls')
print(urls)

numbers = configParser.get('your-config', 'numbers')
print(numbers)

words_with = configParser.get('your-config', 'words_with')
print(words_with)

other_words = configParser.get('your-config', 'other_words')
print(other_words)

anything_else = configParser.get('your-config', 'anything_else')
print(anything_else)

positive_vocab = configParser.get('your-config', 'positive_vocab')
print(positive_vocab)

negative_vocab = configParser.get('your-config', 'negative_vocab')
print(negative_vocab)
