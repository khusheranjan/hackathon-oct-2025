"""
Subscription management and pricing logic
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from database import get_users_collection, get_subscriptions_collection, get_transactions_collection
from models import Subscription, Transaction, User
import logging

logger = logging.getLogger(__name__)

# Pricing configuration
PRICING = {
    "free": {
        "name": "Free",
        "price": 0,
        "currency": "INR",
        "features": {
            "videos_per_account": 1,
            "max_video_duration": 60,  # seconds
            "avatar_enabled": False,
            "advanced_features": False,
            "watermark": False
        }
    },
    "pro_monthly": {
        "name": "Pro Monthly",
        "price": 499,
        "currency": "INR",
        "billing_cycle": "monthly",
        "features": {
            "videos_per_month": 50,
            "max_video_duration": 600,  # 10 minutes
            "avatar_enabled": True,
            "advanced_features": True,
            "watermark": False,
            "priority_support": True
        }
    },
    "pro_yearly": {
        "name": "Pro Yearly",
        "price": 4999,
        "currency": "INR",
        "billing_cycle": "yearly",
        "features": {
            "videos_per_month": 50,
            "max_video_duration": 600,  # 10 minutes
            "avatar_enabled": True,
            "advanced_features": True,
            "watermark": False,
            "priority_support": True
        },
        "discount": "Save 17%"
    }
}

# Credit packages for hybrid model
CREDIT_PACKAGES = {
    "small": {
        "name": "10 Videos Pack",
        "credits": 10,
        "price": 299,
        "currency": "INR"
    },
    "medium": {
        "name": "25 Videos Pack",
        "credits": 25,
        "price": 699,
        "currency": "INR",
        "discount": "Save 7%"
    },
    "large": {
        "name": "100 Videos Pack",
        "credits": 100,
        "price": 2499,
        "currency": "INR",
        "discount": "Save 16%"
    }
}


def get_pricing_info() -> Dict:
    """Get all pricing information"""
    return {
        "subscriptions": PRICING,
        "credit_packages": CREDIT_PACKAGES
    }


def get_user_subscription_info(user_id: str) -> Dict:
    """Get user's current subscription and usage info"""
    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"google_id": user_id})

    if not user_doc:
        return None

    tier = user_doc.get("subscription_tier", "free")
    usage = user_doc.get("usage", {"videos_generated": 0})
    credits = user_doc.get("credits", 0)

    # Get tier limits
    tier_key = "free" if tier == "free" else "pro_monthly"
    tier_limits = PRICING.get(tier_key, PRICING["free"])

    # Check if monthly reset is needed
    last_reset = usage.get("last_reset_date")
    if tier != "free" and last_reset:
        if isinstance(last_reset, str):
            last_reset = datetime.fromisoformat(last_reset)

        # Reset monthly if more than 30 days have passed
        if datetime.utcnow() - last_reset > timedelta(days=30):
            usage["videos_generated"] = 0
            usage["last_reset_date"] = datetime.utcnow()
            users_collection.update_one(
                {"google_id": user_id},
                {"$set": {"usage": usage}}
            )

    return {
        "tier": tier,
        "status": user_doc.get("subscription_status", "active"),
        "credits": credits,
        "usage": usage,
        "limits": tier_limits["features"],
        "can_generate": check_can_generate_video(user_id)
    }


def check_can_generate_video(user_id: str, duration: int = 60, use_avatar: bool = False) -> Tuple[bool, str]:
    """
    Check if user can generate a video
    Returns: (can_generate: bool, reason: str)
    """
    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"google_id": user_id})

    if not user_doc:
        return False, "User not found"

    tier = user_doc.get("subscription_tier", "free")
    usage = user_doc.get("usage", {"videos_generated": 0})
    credits = user_doc.get("credits", 0)

    # Get tier limits
    tier_key = "free" if tier == "free" else "pro_monthly"
    tier_limits = PRICING.get(tier_key, PRICING["free"])["features"]

    # Check duration limit
    max_duration = tier_limits.get("max_video_duration", 60)
    if duration > max_duration:
        return False, f"Video duration exceeds limit. Max duration for {tier} tier: {max_duration}s"

    # Check avatar permission
    if use_avatar and not tier_limits.get("avatar_enabled", False):
        # Can still use avatar if they have credits
        if credits <= 0:
            return False, "Avatar feature requires Pro subscription or credits"

    # Check video count limits
    videos_generated = usage.get("videos_generated", 0)

    if tier == "free":
        # Free tier: 1 video per account (lifetime)
        if videos_generated >= tier_limits.get("videos_per_account", 1):
            if credits > 0:
                return True, "Using credit"
            return False, "Free tier limit reached. Upgrade to Pro or purchase credits."
    else:
        # Pro tier: monthly limit
        videos_per_month = tier_limits.get("videos_per_month", 50)
        if videos_generated >= videos_per_month:
            if credits > 0:
                return True, "Using credit"
            return False, f"Monthly limit of {videos_per_month} videos reached. Resets monthly or purchase additional credits."

    return True, "OK"


def increment_usage(user_id: str, used_credit: bool = False) -> bool:
    """Increment user's video generation count or deduct credit"""
    users_collection = get_users_collection()
    user_doc = users_collection.find_one({"google_id": user_id})

    if not user_doc:
        return False

    if used_credit:
        # Deduct credit
        credits = user_doc.get("credits", 0)
        if credits > 0:
            users_collection.update_one(
                {"google_id": user_id},
                {"$inc": {"credits": -1}}
            )
            logger.info(f"Deducted 1 credit from user {user_id}. Remaining: {credits - 1}")
            return True
    else:
        # Increment usage count
        users_collection.update_one(
            {"google_id": user_id},
            {
                "$inc": {"usage.videos_generated": 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        logger.info(f"Incremented usage for user {user_id}")
        return True

    return False


def upgrade_to_pro(user_id: str, billing_cycle: str = "monthly", razorpay_subscription_id: str = None) -> bool:
    """Upgrade user to Pro tier"""
    users_collection = get_users_collection()
    subscriptions_collection = get_subscriptions_collection()

    tier_key = f"pro_{billing_cycle}"
    pricing = PRICING.get(tier_key)

    if not pricing:
        return False

    now = datetime.utcnow()
    end_date = now + timedelta(days=365 if billing_cycle == "yearly" else 30)

    # Update user document
    update_result = users_collection.update_one(
        {"google_id": user_id},
        {
            "$set": {
                "subscription_tier": "pro",
                "subscription_status": "active",
                "subscription_start_date": now,
                "subscription_end_date": end_date,
                "razorpay_subscription_id": razorpay_subscription_id,
                "updated_at": now,
                "usage.videos_generated": 0,
                "usage.last_reset_date": now
            }
        }
    )

    if update_result.modified_count > 0:
        # Create subscription record
        subscription_doc = Subscription.create(
            user_id=user_id,
            tier="pro",
            razorpay_subscription_id=razorpay_subscription_id,
            amount=pricing["price"],
            currency=pricing["currency"],
            billing_cycle=billing_cycle
        )
        subscriptions_collection.insert_one(subscription_doc)
        logger.info(f"Upgraded user {user_id} to Pro ({billing_cycle})")
        return True

    return False


def add_credits(user_id: str, credits: int, transaction_id: str = None) -> bool:
    """Add credits to user account"""
    users_collection = get_users_collection()

    result = users_collection.update_one(
        {"google_id": user_id},
        {
            "$inc": {"credits": credits},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    if result.modified_count > 0:
        logger.info(f"Added {credits} credits to user {user_id}")
        return True

    return False


def create_transaction(
    user_id: str,
    transaction_type: str,
    amount: float,
    razorpay_payment_id: str = None,
    razorpay_order_id: str = None,
    razorpay_signature: str = None,
    description: str = ""
) -> Optional[str]:
    """Create a transaction record"""
    transactions_collection = get_transactions_collection()

    transaction_doc = Transaction.create(
        user_id=user_id,
        transaction_type=transaction_type,
        amount=amount,
        razorpay_payment_id=razorpay_payment_id,
        razorpay_order_id=razorpay_order_id,
        razorpay_signature=razorpay_signature,
        status="pending",
        description=description
    )

    result = transactions_collection.insert_one(transaction_doc)
    return str(result.inserted_id)


def complete_transaction(transaction_id: str) -> bool:
    """Mark transaction as completed"""
    from bson import ObjectId
    transactions_collection = get_transactions_collection()

    result = transactions_collection.update_one(
        {"_id": ObjectId(transaction_id)},
        {
            "$set": {
                "status": "completed",
                "updated_at": datetime.utcnow()
            }
        }
    )

    return result.modified_count > 0


def get_user_transactions(user_id: str, limit: int = 10) -> list:
    """Get user's transaction history"""
    transactions_collection = get_transactions_collection()

    transactions = transactions_collection.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(limit)

    return [Transaction.to_dict(t) for t in transactions]
