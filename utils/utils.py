import json

def cursorToJson(data):
    data = [doc for doc in data]
    return json.dumps(data, default=str)

def objectToJson(obj):
    return json.dumps(obj, default=str)
