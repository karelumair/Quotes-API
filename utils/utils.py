import json

def cursorToJson(data):
    data = [doc.to_json() for doc in data]
    return data

def objectToJson(obj):
    return json.dumps(obj, default=str)
