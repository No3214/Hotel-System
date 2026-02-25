import re
from datetime import datetime, timezone
import uuid


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def new_id():
    return str(uuid.uuid4())


def clean_doc(doc):
    if doc and "_id" in doc:
        doc = {k: v for k, v in doc.items() if k != "_id"}
    return doc


def clean_docs(docs):
    return [clean_doc(d) for d in docs]


def escape_regex(text: str) -> str:
    """Escape special regex characters to prevent regex injection."""
    return re.escape(text)
