import os
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, DB_NAME

# Mock client for testing without MongoDB
class MockCollection:
    def __init__(self, name):
        self.name = name
    async def find_one(self, *args, **kwargs): return None
    def find(self, *args, **kwargs):
        class MockCursor:
            async def to_list(self, *args, **kwargs): return []
            def sort(self, *args, **kwargs): return self
            def limit(self, *args, **kwargs): return self
            def skip(self, *args, **kwargs): return self
        return MockCursor()
    async def insert_one(self, *args, **kwargs):
        class MockInsertResult:
            inserted_id = "mock_id"
        return MockInsertResult()
    async def update_one(self, *args, **kwargs):
        class MockUpdateResult:
            matched_count = 1
            modified_count = 1
        return MockUpdateResult()
    async def delete_one(self, *args, **kwargs):
        class MockDeleteResult:
            deleted_count = 1
        return MockDeleteResult()
    async def delete_many(self, *args, **kwargs):
        class MockDeleteResult:
            deleted_count = 1
        return MockDeleteResult()
    async def count_documents(self, *args, **kwargs): return 0
    async def aggregate(self, *args, **kwargs):
        class MockCursor:
            async def to_list(self, *args, **kwargs): return []
        return MockCursor()
    async def create_index(self, *args, **kwargs): return None

class MockDB:
    def __getattr__(self, name):
        return MockCollection(name)
    async def command(self, *args, **kwargs): return {"ok": 1}

class MockClient:
    def __getitem__(self, name): return MockDB()
    def close(self): pass

if os.environ.get("MOCK_DB") == "true":
    client = MockClient()
    db = MockDB()
else:
    if not MONGO_URL:
        raise ValueError("MONGO_URL environment variable is not set and MOCK_DB is not enabled")
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
