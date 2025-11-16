"""
MongoDB models and helper functions
"""

from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId


class User:
    """User model"""

    @staticmethod
    def create(google_id: str, email: str, name: str, picture: str = "") -> dict:
        """Create a new user document"""
        return {
            "google_id": google_id,
            "email": email,
            "name": name,
            "picture": picture,
            "subscription_tier": "free",  # free, pro
            "subscription_status": "active",  # active, cancelled, expired
            "subscription_start_date": None,
            "subscription_end_date": None,
            "razorpay_subscription_id": None,
            "credits": 0,  # Additional credits for hybrid model
            "usage": {
                "videos_generated": 0,
                "last_reset_date": datetime.utcnow()
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    @staticmethod
    def to_dict(user_doc: dict) -> dict:
        """Convert MongoDB document to dict"""
        if not user_doc:
            return None

        return {
            "id": str(user_doc["_id"]),
            "google_id": user_doc["google_id"],
            "email": user_doc["email"],
            "name": user_doc["name"],
            "picture": user_doc.get("picture", ""),
            "subscription_tier": user_doc.get("subscription_tier", "free"),
            "subscription_status": user_doc.get("subscription_status", "active"),
            "subscription_start_date": user_doc.get("subscription_start_date").isoformat() if user_doc.get("subscription_start_date") and isinstance(user_doc.get("subscription_start_date"), datetime) else user_doc.get("subscription_start_date"),
            "subscription_end_date": user_doc.get("subscription_end_date").isoformat() if user_doc.get("subscription_end_date") and isinstance(user_doc.get("subscription_end_date"), datetime) else user_doc.get("subscription_end_date"),
            "credits": user_doc.get("credits", 0),
            "usage": user_doc.get("usage", {"videos_generated": 0}),
            "created_at": user_doc["created_at"].isoformat() if isinstance(user_doc["created_at"], datetime) else user_doc["created_at"],
            "updated_at": user_doc["updated_at"].isoformat() if isinstance(user_doc["updated_at"], datetime) else user_doc["updated_at"]
        }


class Chat:
    """Chat model"""

    @staticmethod
    def create(user_id: str, title: str = "New Chat") -> dict:
        """Create a new chat document"""
        now = datetime.utcnow()
        return {
            "user_id": user_id,
            "title": title,
            "message_count": 0,
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    def to_dict(chat_doc: dict, include_messages: bool = False) -> dict:
        """Convert MongoDB document to dict"""
        if not chat_doc:
            return None

        result = {
            "id": str(chat_doc["_id"]),
            "user_id": chat_doc["user_id"],
            "title": chat_doc["title"],
            "message_count": chat_doc.get("message_count", 0),
            "created_at": chat_doc["created_at"].isoformat() if isinstance(chat_doc["created_at"], datetime) else chat_doc["created_at"],
            "updated_at": chat_doc["updated_at"].isoformat() if isinstance(chat_doc["updated_at"], datetime) else chat_doc["updated_at"]
        }

        if include_messages and "messages" in chat_doc:
            result["messages"] = chat_doc["messages"]

        return result

    @staticmethod
    def to_summary(chat_doc: dict) -> dict:
        """Convert to summary (without messages)"""
        if not chat_doc:
            return None

        return {
            "id": str(chat_doc["_id"]),
            "title": chat_doc["title"],
            "message_count": chat_doc.get("message_count", 0),
            "created_at": chat_doc["created_at"].isoformat() if isinstance(chat_doc["created_at"], datetime) else chat_doc["created_at"],
            "updated_at": chat_doc["updated_at"].isoformat() if isinstance(chat_doc["updated_at"], datetime) else chat_doc["updated_at"]
        }


class Message:
    """Message model"""

    @staticmethod
    def create(chat_id: str, role: str, content: str) -> dict:
        """Create a new message document"""
        now = datetime.utcnow()
        return {
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "timestamp": now
        }

    @staticmethod
    def to_dict(message_doc: dict) -> dict:
        """Convert MongoDB document to dict"""
        if not message_doc:
            return None

        return {
            "id": str(message_doc["_id"]),
            "chat_id": message_doc["chat_id"],
            "role": message_doc["role"],
            "content": message_doc["content"],
            "timestamp": message_doc["timestamp"].isoformat() if isinstance(message_doc["timestamp"], datetime) else message_doc["timestamp"]
        }


class Subscription:
    """Subscription model for tracking user subscriptions"""

    @staticmethod
    def create(
        user_id: str,
        tier: str,
        razorpay_subscription_id: str = None,
        razorpay_plan_id: str = None,
        amount: float = 0,
        currency: str = "INR",
        billing_cycle: str = "monthly"
    ) -> dict:
        """Create a new subscription document"""
        now = datetime.utcnow()
        return {
            "user_id": user_id,
            "tier": tier,  # free, pro
            "status": "active",  # active, cancelled, expired, paused
            "razorpay_subscription_id": razorpay_subscription_id,
            "razorpay_plan_id": razorpay_plan_id,
            "amount": amount,
            "currency": currency,
            "billing_cycle": billing_cycle,  # monthly, yearly
            "start_date": now,
            "end_date": None,
            "next_billing_date": None,
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    def to_dict(subscription_doc: dict) -> dict:
        """Convert MongoDB document to dict"""
        if not subscription_doc:
            return None

        return {
            "id": str(subscription_doc["_id"]),
            "user_id": subscription_doc["user_id"],
            "tier": subscription_doc["tier"],
            "status": subscription_doc["status"],
            "amount": subscription_doc.get("amount", 0),
            "currency": subscription_doc.get("currency", "INR"),
            "billing_cycle": subscription_doc.get("billing_cycle", "monthly"),
            "start_date": subscription_doc["start_date"].isoformat() if isinstance(subscription_doc["start_date"], datetime) else subscription_doc["start_date"],
            "end_date": subscription_doc.get("end_date").isoformat() if subscription_doc.get("end_date") and isinstance(subscription_doc.get("end_date"), datetime) else subscription_doc.get("end_date"),
            "next_billing_date": subscription_doc.get("next_billing_date").isoformat() if subscription_doc.get("next_billing_date") and isinstance(subscription_doc.get("next_billing_date"), datetime) else subscription_doc.get("next_billing_date"),
            "created_at": subscription_doc["created_at"].isoformat() if isinstance(subscription_doc["created_at"], datetime) else subscription_doc["created_at"],
            "updated_at": subscription_doc["updated_at"].isoformat() if isinstance(subscription_doc["updated_at"], datetime) else subscription_doc["updated_at"]
        }


class Transaction:
    """Transaction model for tracking payments"""

    @staticmethod
    def create(
        user_id: str,
        transaction_type: str,
        amount: float,
        currency: str = "INR",
        razorpay_payment_id: str = None,
        razorpay_order_id: str = None,
        razorpay_signature: str = None,
        status: str = "pending",
        description: str = ""
    ) -> dict:
        """Create a new transaction document"""
        now = datetime.utcnow()
        return {
            "user_id": user_id,
            "transaction_type": transaction_type,  # subscription, credit_purchase, one_time
            "amount": amount,
            "currency": currency,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_order_id": razorpay_order_id,
            "razorpay_signature": razorpay_signature,
            "status": status,  # pending, completed, failed, refunded
            "description": description,
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    def to_dict(transaction_doc: dict) -> dict:
        """Convert MongoDB document to dict"""
        if not transaction_doc:
            return None

        return {
            "id": str(transaction_doc["_id"]),
            "user_id": transaction_doc["user_id"],
            "transaction_type": transaction_doc["transaction_type"],
            "amount": transaction_doc["amount"],
            "currency": transaction_doc.get("currency", "INR"),
            "razorpay_payment_id": transaction_doc.get("razorpay_payment_id"),
            "razorpay_order_id": transaction_doc.get("razorpay_order_id"),
            "status": transaction_doc["status"],
            "description": transaction_doc.get("description", ""),
            "created_at": transaction_doc["created_at"].isoformat() if isinstance(transaction_doc["created_at"], datetime) else transaction_doc["created_at"],
            "updated_at": transaction_doc["updated_at"].isoformat() if isinstance(transaction_doc["updated_at"], datetime) else transaction_doc["updated_at"]
        }


def str_to_objectid(id_str: str) -> Optional[ObjectId]:
    """Convert string ID to ObjectId"""
    try:
        return ObjectId(id_str)
    except Exception:
        return None
