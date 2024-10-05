import configparser
import os
import sys

this_folder = os.path.dirname(os.path.abspath(__file__))
print(this_folder)

config_file = os.path.join(this_folder, 'ConfigFile.config')
print(config_file)

configParser = configparser.RawConfigParser()
configParser.read(config_file)

sys_path = sys.path[1]
print(sys_path)

file_path_for_timeline_outputs = sys_path + configParser.get('your-config', 'file_path_for_timeline_outputs')
os.makedirs(file_path_for_timeline_outputs, exist_ok=True)
print(file_path_for_timeline_outputs)

file_path_for_followers_outputs = sys_path + configParser.get('your-config', 'file_path_for_followers_outputs')
os.makedirs(file_path_for_followers_outputs, exist_ok=True)
print(file_path_for_followers_outputs)

file_path_for_list_of_username = sys_path + configParser.get('your-config', 'file_path_for_list_of_username')
os.makedirs(file_path_for_list_of_username, exist_ok=True)
print(file_path_for_list_of_username)

file_path_for_mongo = sys_path + configParser.get('your-config', 'file_path_for_mongo')
os.makedirs(file_path_for_mongo, exist_ok=True)
print(file_path_for_mongo)

file_path_for_tokenization = sys_path + configParser.get('your-config', 'file_path_for_tokenization')
os.makedirs(file_path_for_tokenization, exist_ok=True)
print(file_path_for_tokenization)

file_path_for_cross_val = sys_path + configParser.get('your-config', 'file_path_for_cross_val')
os.makedirs(file_path_for_cross_val, exist_ok=True)
print(file_path_for_cross_val)

streaming_txt_file = sys_path + configParser.get('your-config', 'streaming_txt_file')
os.makedirs(streaming_txt_file, exist_ok=True)
print(streaming_txt_file)

streaming_db = sys_path + configParser.get('your-config', 'streaming_db')
os.makedirs(streaming_db, exist_ok=True)
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
