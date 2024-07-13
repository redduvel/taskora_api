import datetime
from bson import ObjectId    

def serialize_document(document):
    if document is None:
        return None

    def serialize_value(value):
        if isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, datetime.datetime):
            return value.isoformat()
        elif isinstance(value, list):
            return [serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return serialize_document(value)
        else:
            return value

    serialized = {}
    for key, value in document.items():
        serialized[key] = serialize_value(value)

    return serialized

def serialize_cursor(cursor):
    return [serialize_document(doc) for doc in cursor]