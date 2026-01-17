"""
MongoDB Atlas Integration for Adaptive Identity Engine

Stores:
- User sessions with behavioral data
- Events (time-series collection)
- Variant performance metrics
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from typing import Optional, Dict, Any, List
import os
from datetime import datetime

class MongoDB:
    """MongoDB Atlas connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    db = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB Atlas"""
        mongodb_uri = os.getenv("MONGODB_URI")

        if not mongodb_uri:
            print("⚠️  MONGODB_URI not set - using in-memory storage")
            return None

        try:
            cls.client = AsyncIOMotorClient(mongodb_uri)
            # Test connection
            await cls.client.admin.command('ping')
            cls.db = cls.client.adaptive_identity

            # Create indexes
            await cls._create_indexes()

            print("✅ Connected to MongoDB Atlas")
            return cls.db

        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("   Falling back to in-memory storage")
            return None

    @classmethod
    async def _create_indexes(cls):
        """Create database indexes for performance"""
        if not cls.db:
            return

        # Sessions collection
        await cls.db.sessions.create_index("session_id", unique=True)
        await cls.db.sessions.create_index("user_id")
        await cls.db.sessions.create_index("created_at")

        # Events collection (time-series optimized)
        await cls.db.events.create_index([("session_id", 1), ("timestamp", -1)])
        await cls.db.events.create_index("event_name")
        await cls.db.events.create_index("timestamp")

        # Variants collection
        await cls.db.variants.create_index("variant_id", unique=True)
        await cls.db.variants.create_index("component_id")

        print("✅ MongoDB indexes created")

    @classmethod
    async def close(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")


class SessionStore:
    """Session storage using MongoDB Atlas"""

    def __init__(self, db):
        self.db = db
        self.collection = db.sessions if db else None
        # Fallback in-memory storage
        self.memory_store: Dict[str, Dict[str, Any]] = {}

    async def create_session(self, session_data: Dict[str, Any]) -> str:
        """Create a new session"""
        session_data["created_at"] = datetime.utcnow()
        session_data["updated_at"] = datetime.utcnow()

        if self.collection:
            await self.collection.insert_one(session_data)
        else:
            self.memory_store[session_data["session_id"]] = session_data

        return session_data["session_id"]

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        if self.collection:
            session = await self.collection.find_one({"session_id": session_id})
            return session
        else:
            return self.memory_store.get(session_id)

    async def update_session(self, session_id: str, update_data: Dict[str, Any]):
        """Update session data"""
        update_data["updated_at"] = datetime.utcnow()

        if self.collection:
            await self.collection.update_one(
                {"session_id": session_id},
                {"$set": update_data}
            )
        else:
            if session_id in self.memory_store:
                self.memory_store[session_id].update(update_data)


class EventStore:
    """Event storage using MongoDB Atlas time-series collection"""

    def __init__(self, db):
        self.db = db
        self.collection = db.events if db else None
        self.memory_store: List[Dict[str, Any]] = []

    async def insert_event(self, event_data: Dict[str, Any]):
        """Insert a single event"""
        if self.collection:
            await self.collection.insert_one(event_data)
        else:
            self.memory_store.append(event_data)

    async def get_session_events(self, session_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get events for a session"""
        if self.collection:
            cursor = self.collection.find(
                {"session_id": session_id}
            ).sort("timestamp", -1).limit(limit)
            return await cursor.to_list(length=limit)
        else:
            return [e for e in self.memory_store if e.get("session_id") == session_id][-limit:]


class VariantStore:
    """Variant storage with performance tracking"""

    def __init__(self, db):
        self.db = db
        self.collection = db.variants if db else None
        self.memory_store: Dict[str, Dict[str, Any]] = {}

    async def get_variants(self, component_id: str) -> List[Dict[str, Any]]:
        """Get all variants for a component"""
        if self.collection:
            cursor = self.collection.find({"component_id": component_id})
            return await cursor.to_list(length=100)
        else:
            return [v for v in self.memory_store.values() if v.get("component_id") == component_id]

    async def update_variant_performance(self, variant_id: str, metrics: Dict[str, float]):
        """Update variant performance metrics"""
        if self.collection:
            await self.collection.update_one(
                {"variant_id": variant_id},
                {"$set": {"performance_metrics": metrics, "updated_at": datetime.utcnow()}},
                upsert=True
            )
        else:
            if variant_id in self.memory_store:
                self.memory_store[variant_id]["performance_metrics"] = metrics
