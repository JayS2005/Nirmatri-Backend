"""
MongoDB Database Module
Production-ready MongoDB implementation
Central export point for database layer
"""

# ===============================
# CONNECTION
# ===============================
from apps.db.mongo.db_collections import sellers_collection
from .connection import mongo_connection, db, client


# ===============================
# COLLECTIONS
# ===============================
from .db_collections import (
    address_collection,
    users_collection,
    products_collection,
    orders_collection,
    users,
    products,
    orders,
)


# ===============================
# UTILITIES
# ===============================
from .utils import (
    serialize_doc,
    serialize_docs,
    validate_object_id,
    create_object_id,
    build_filter_from_params,
    paginate_query,
    sanitize_user_data,
    sanitize_product_data,
    log_database_operation,
    DatabaseError,
    ValidationError,
)


# ===============================
# MODELS / SCHEMAS
# ===============================
from .models import (
    UserModel,
    ProductModel,
    OrderModel,
    DATABASE_SCHEMAS,
    get_collection_schema,
    validate_document_schema,
)


# ===============================
# PUBLIC EXPORTS
# ===============================
__all__ = [
    # Connection
    "mongo_connection",
    "db",
    "client",

    # Collections
    "users_collection",
    "products_collection",
    "orders_collection",
    "users",
    "products",
    "orders",

    # Utilities
    "serialize_doc",
    "serialize_docs",
    "validate_object_id",
    "create_object_id",
    "build_filter_from_params",
    "paginate_query",
    "sanitize_user_data",
    "sanitize_product_data",
    "log_database_operation",
    "DatabaseError",
    "ValidationError",

    # Models
    "UserModel",
    "ProductModel",
    "OrderModel",
    "DATABASE_SCHEMAS",
    "get_collection_schema",
    "validate_document_schema",
]
