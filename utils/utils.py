from bson import json_util

def cursorToJson(data):
    data = [doc for doc in data]
    return json_util.dumps(data)