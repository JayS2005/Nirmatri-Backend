"""
MongoDB Connection Manager - Singleton Pattern
Production-ready MongoDB connection with safe lazy initialization
"""

import os
import logging
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ConfigurationError
from dotenv import load_dotenv
import certifi


MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["nirmatriDB"]

# ✅ ADD THIS
users_collection = db["users"]

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoDBConnection:
    """
    Singleton class for MongoDB connection management
    Connection is created lazily (only when required)
    """

    _instance: Optional["MongoDBConnection"] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> None:
        """Establish MongoDB connection if not already connected"""
        if self._client is not None:
            return  # already connected

        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri:
                raise ConfigurationError("MONGO_URI not found in environment variables")

            db_name = os.getenv("MONGO_DB_NAME", "nirmatriDB")

            # ✅ MongoDB Client
            self._client = MongoClient(
                mongo_uri,
                tls=True,
                tlsCAFile=certifi.where(),

                # Connection Pool
                maxPoolSize=50,
                minPoolSize=5,

                # Stable timeouts (fix background cancel error)
                maxIdleTimeMS=60000,
                serverSelectionTimeoutMS=20000,
                connectTimeoutMS=20000,
                heartbeatFrequencyMS=10000,

                retryWrites=True,
                w="majority",
            )

            # Test connection
            self._client.admin.command("ping")

            self._db = self._client[db_name]

            logger.info(f" MongoDB connected successfully → DB: {db_name}")

        except ConnectionFailure as e:
            logger.error(f" MongoDB connection failed: {e}")
            raise
        except Exception as e:
            logger.error(f" Unexpected MongoDB error: {e}")
            raise

    def get_database(self) -> Database:
        """Return database instance (connect if needed)"""
        if self._db is None:
            self.connect()
        return self._db

    def get_client(self) -> MongoClient:
        """Return client instance (connect if needed)"""
        if self._client is None:
            self.connect()
        return self._client

    def close(self) -> None:
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("🔒 MongoDB connection closed")

    def is_connected(self) -> bool:
        """Check MongoDB connection health"""
        try:
            if self._client is None:
                return False
            self._client.admin.command("ping")
            return True
        except Exception:
            return False


# -----------------------------
# Public shared instance
# -----------------------------
mongo_connection = MongoDBConnection()


# Lazy-safe exports
def get_db() -> Database:
    return mongo_connection.get_database()


def get_client() -> MongoClient:
    return mongo_connection.get_client()


# Backward compatibility (safe)
db = get_db()
client = get_client()


users_collection = db["users"]
superadmin_collection = db["superadmins"]
sellers_collection = db["sellers"]
addresses_collection = db["addresses"]