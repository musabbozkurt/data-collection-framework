def log(msg):
    from pymongo import MongoClient
    from pymongo import ASCENDING
    from datetime import datetime

    client = MongoClient()
    db = client.my_logs
    log_collection = db.log
    log_collection.ensure_index([("timestamp", ASCENDING)])

    """Log `msg` to MongoDB log"""

    entry = {}
    entry['timestamp'] = str(datetime.now())
    entry['msg'] = msg
    log_collection.insert(entry)
