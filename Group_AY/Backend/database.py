"""
MongoDB database connection and initialization
"""

import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
_client = None
_db = None


def get_mongodb_uri():
    """Get MongoDB URI from environment"""
    return os.getenv('MONGODB_URI', 'mongodb://admin:admin123@localhost:27017/eduvideo?authSource=admin')


def connect_to_mongodb():
    """Connect to MongoDB and return database instance"""
    global _client, _db

    if _db is not None:
        return _db

    try:
        mongodb_uri = get_mongodb_uri()
        _client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)

        # Test connection
        _client.admin.command('ping')

        # Get database
        _db = _client.eduvideo

        logger.info("Successfully connected to MongoDB")

        # Initialize collections and indexes
        initialize_collections()

        return _db

    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


def initialize_collections():
    """Create collections and indexes"""
    global _db

    if _db is None:
        return

    try:
        # Users collection
        users_collection = _db.users
        users_collection.create_index([("google_id", ASCENDING)], unique=True)
        users_collection.create_index([("email", ASCENDING)])
        users_collection.create_index([("subscription_tier", ASCENDING)])

        # Chats collection
        chats_collection = _db.chats
        chats_collection.create_index([("user_id", ASCENDING)])
        chats_collection.create_index([("updated_at", DESCENDING)])
        chats_collection.create_index([("user_id", ASCENDING), ("updated_at", DESCENDING)])

        # Messages collection
        messages_collection = _db.messages
        messages_collection.create_index([("chat_id", ASCENDING)])
        messages_collection.create_index([("chat_id", ASCENDING), ("timestamp", ASCENDING)])

        # Subscriptions collection
        subscriptions_collection = _db.subscriptions
        subscriptions_collection.create_index([("user_id", ASCENDING)])
        subscriptions_collection.create_index([("razorpay_subscription_id", ASCENDING)])
        subscriptions_collection.create_index([("status", ASCENDING)])

        # Transactions collection
        transactions_collection = _db.transactions
        transactions_collection.create_index([("user_id", ASCENDING)])
        transactions_collection.create_index([("razorpay_payment_id", ASCENDING)])
        transactions_collection.create_index([("razorpay_order_id", ASCENDING)])
        transactions_collection.create_index([("created_at", DESCENDING)])

        logger.info("Collections and indexes initialized successfully")

    except Exception as e:
        logger.warning(f"Error initializing collections: {e}")


def get_database():
    """Get database instance"""
    global _db

    if _db is None:
        return connect_to_mongodb()

    return _db


def get_collection(collection_name):
    """Get a specific collection"""
    db = get_database()
    return db[collection_name]


def close_connection():
    """Close MongoDB connection"""
    global _client, _db

    if _client:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")


# Collection getters
def get_users_collection():
    """Get users collection"""
    return get_collection('users')


def get_chats_collection():
    """Get chats collection"""
    return get_collection('chats')


def get_messages_collection():
    """Get messages collection"""
    return get_collection('messages')


def get_subscriptions_collection():
    """Get subscriptions collection"""
    return get_collection('subscriptions')


def get_transactions_collection():
    """Get transactions collection"""
    return get_collection('transactions')
