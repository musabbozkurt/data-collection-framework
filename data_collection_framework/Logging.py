def log(msg):
    from pymongo import MongoClient
    from pymongo import ASCENDING
    from datetime import datetime

    client = MongoClient()
    db = client.my_logs
    log_collection = db.log
    log_collection.ensure_index([("timestamp", ASCENDING)])

    """Log `msg` to MongoDB log"""

    log_collection.insert({'timestamp': str(datetime.now()), 'msg': msg})
