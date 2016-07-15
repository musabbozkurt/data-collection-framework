import pymongo
import csv

conn = pymongo.MongoClient()

db = conn.twitter

cursor = db.timeline.find({})


with open('asdxk.csv', 'w',encoding='utf-8') as outfile:
    fields = ['created_at', 'place', 'user', 'text', 'quoted_status','withheld_scope','withheld_copyright','withheld_in_countries', 'quoted_status_id', 'quoted_status_id_str','in_reply_to_user_id', 'in_reply_to_status_id', 'retweeted_status', 'in_reply_to_status_id_str', 'favorite_count', 'in_reply_to_user_id_str', 'contributors', 'geo', 'favorited', 'lang', 'in_reply_to_screen_name', 'id_str', 'extended_entities', '_id', 'retweeted', 'entities', 'possibly_sensitive', 'truncated', 'source', 'id', 'is_quote_status', 'coordinates', 'retweet_count']
    writer = csv.DictWriter(outfile, fieldnames=fields)
    writer.writeheader()
    for x in cursor:
         writer.writerow(x)