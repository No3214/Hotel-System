from datetime import datetime, timezone
import uuid


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def new_id():
    return str(uuid.uuid4())


def clean_doc(doc):
    if doc and "_id" in doc:
        del doc["_id"]
    return doc


def clean_docs(docs):
    return [clean_doc(d) for d in docs]
