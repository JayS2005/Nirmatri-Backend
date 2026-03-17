"""
MongoDB Collections Registry
Centralized access to all MongoDB collections
"""

from pymongo.collection import Collection

from .connection import db

# ===============================
# COLLECTIONS
# ===============================

users_collection: Collection = db["users"]
products_collection: Collection = db["products"]
orders_collection: Collection = db["orders"]
address_collection: Collection = db["addresses"]

# ===============================
# OPTIONAL ALIASES (SAFE)
# ===============================
# These are convenient shortcuts
users = users_collection
products = products_collection
orders = orders_collection
addresses = address_collection

# ===============================
# PUBLIC EXPORTS
# ===============================
__all__ = [
    "users_collection",
    "products_collection",
    "orders_collection",
    "users",
    "products",
    "orders",
]

from apps.db.mongo.connection import get_db

db = get_db()

users_collection = db["users"]
sellers_collection = db["sellers"]
products_collection = db["products"]
orders_collection = db["orders"]  
address_collection = db["addresses"]  
