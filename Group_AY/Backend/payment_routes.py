"""
Payment and subscription routes using Razorpay
"""

import os
import razorpay
import hmac
import hashlib
from flask import Blueprint, request, jsonify
from auth import require_auth
from subscription_manager import (
    get_pricing_info,
    get_user_subscription_info,
    upgrade_to_pro,
    add_credits,
    create_transaction,
    complete_transaction,
    get_user_transactions,
    PRICING,
    CREDIT_PACKAGES
)
import logging

logger = logging.getLogger(__name__)

# Initialize Razorpay client
RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID', '')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET', '')

razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Create blueprint
payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/api/pricing', methods=['GET'])
def get_pricing():
    """Get pricing information"""
    try:
        pricing = get_pricing_info()
        return jsonify({
            "success": True,
            "pricing": pricing
        }), 200
    except Exception as e:
        logger.error(f"Error fetching pricing: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch pricing"
        }), 500


@payment_bp.route('/api/subscription/status', methods=['GET'])
@require_auth
def get_subscription_status():
    """Get user's subscription status"""
    try:
        user_id = request.user.get('user_id')
        subscription_info = get_user_subscription_info(user_id)

        if not subscription_info:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        return jsonify({
            "success": True,
            "subscription": subscription_info
        }), 200
    except Exception as e:
        logger.error(f"Error fetching subscription status: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch subscription status"
        }), 500


@payment_bp.route('/api/payment/create-order', methods=['POST'])
@require_auth
def create_order():
    """Create Razorpay order for subscription or credits"""
    try:
        user_id = request.user.get('user_id')
        data = request.get_json()

        order_type = data.get('type')  # 'subscription' or 'credits'
        plan = data.get('plan')  # 'pro_monthly', 'pro_yearly' or credit package name

        if not order_type or not plan:
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400

        # Determine amount based on type
        if order_type == 'subscription':
            pricing = PRICING.get(plan)
            if not pricing:
                return jsonify({
                    "success": False,
                    "error": "Invalid plan"
                }), 400
            amount = pricing['price']
            currency = pricing['currency']
            description = f"Subscription: {pricing['name']}"

        elif order_type == 'credits':
            package = CREDIT_PACKAGES.get(plan)
            if not package:
                return jsonify({
                    "success": False,
                    "error": "Invalid credit package"
                }), 400
            amount = package['price']
            currency = package['currency']
            description = f"Credits: {package['name']}"

        else:
            return jsonify({
                "success": False,
                "error": "Invalid order type"
            }), 400

        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": amount * 100,  # Razorpay expects amount in paise
            "currency": currency,
            "receipt": f"{order_type}_{user_id}_{plan}",
            "notes": {
                "user_id": user_id,
                "type": order_type,
                "plan": plan
            }
        })

        # Create transaction record
        transaction_id = create_transaction(
            user_id=user_id,
            transaction_type=order_type,
            amount=amount,
            razorpay_order_id=razorpay_order['id'],
            description=description
        )

        return jsonify({
            "success": True,
            "order": {
                "id": razorpay_order['id'],
                "amount": amount,
                "currency": currency,
                "transaction_id": transaction_id
            },
            "razorpay_key": RAZORPAY_KEY_ID
        }), 200

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to create order"
        }), 500


@payment_bp.route('/api/payment/verify', methods=['POST'])
@require_auth
def verify_payment():
    """Verify Razorpay payment signature and complete transaction"""
    try:
        user_id = request.user.get('user_id')
        data = request.get_json()

        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_signature = data.get('razorpay_signature')
        transaction_id = data.get('transaction_id')
        order_type = data.get('type')
        plan = data.get('plan')

        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature, transaction_id]):
            return jsonify({
                "success": False,
                "error": "Missing required fields"
            }), 400

        # Verify signature
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode(),
            f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != razorpay_signature:
            return jsonify({
                "success": False,
                "error": "Invalid payment signature"
            }), 400

        # Payment verified - complete transaction
        complete_transaction(transaction_id)

        # Apply the benefit based on type
        if order_type == 'subscription':
            billing_cycle = 'monthly' if plan == 'pro_monthly' else 'yearly'
            success = upgrade_to_pro(user_id, billing_cycle, razorpay_order_id)

            if success:
                return jsonify({
                    "success": True,
                    "message": "Subscription activated successfully",
                    "subscription": get_user_subscription_info(user_id)
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to activate subscription"
                }), 500

        elif order_type == 'credits':
            package = CREDIT_PACKAGES.get(plan)
            if package:
                success = add_credits(user_id, package['credits'], transaction_id)

                if success:
                    return jsonify({
                        "success": True,
                        "message": f"Added {package['credits']} credits successfully",
                        "subscription": get_user_subscription_info(user_id)
                    }), 200

        return jsonify({
            "success": False,
            "error": "Failed to process payment"
        }), 500

    except Exception as e:
        logger.error(f"Error verifying payment: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to verify payment"
        }), 500


@payment_bp.route('/api/payment/webhook', methods=['POST'])
def razorpay_webhook():
    """Handle Razorpay webhooks for payment events"""
    try:
        # Get the webhook signature from headers
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = os.getenv('RAZORPAY_WEBHOOK_SECRET', '')

        if not webhook_signature or not webhook_secret:
            return jsonify({
                "success": False,
                "error": "Missing signature or secret"
            }), 400

        # Verify webhook signature
        request_body = request.get_data().decode('utf-8')
        expected_signature = hmac.new(
            webhook_secret.encode(),
            request_body.encode(),
            hashlib.sha256
        ).hexdigest()

        if webhook_signature != expected_signature:
            logger.warning("Invalid webhook signature")
            return jsonify({
                "success": False,
                "error": "Invalid signature"
            }), 400

        # Process webhook event
        event = request.get_json()
        event_type = event.get('event')

        logger.info(f"Received webhook: {event_type}")

        # Handle different event types
        if event_type == 'payment.captured':
            # Payment successful
            payment_entity = event.get('payload', {}).get('payment', {}).get('entity', {})
            logger.info(f"Payment captured: {payment_entity.get('id')}")

        elif event_type == 'subscription.charged':
            # Recurring subscription payment
            subscription_entity = event.get('payload', {}).get('subscription', {}).get('entity', {})
            logger.info(f"Subscription charged: {subscription_entity.get('id')}")

        elif event_type == 'subscription.cancelled':
            # Subscription cancelled
            subscription_entity = event.get('payload', {}).get('subscription', {}).get('entity', {})
            logger.info(f"Subscription cancelled: {subscription_entity.get('id')}")

        return jsonify({"success": True}), 200

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({
            "success": False,
            "error": "Webhook processing failed"
        }), 500


@payment_bp.route('/api/transactions', methods=['GET'])
@require_auth
def get_transactions():
    """Get user's transaction history"""
    try:
        user_id = request.user.get('user_id')
        limit = int(request.args.get('limit', 10))

        transactions = get_user_transactions(user_id, limit)

        return jsonify({
            "success": True,
            "transactions": transactions
        }), 200

    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch transactions"
        }), 500


@payment_bp.route('/api/subscription/cancel', methods=['POST'])
@require_auth
def cancel_subscription():
    """Cancel user's subscription"""
    try:
        user_id = request.user.get('user_id')
        from database import get_users_collection
        from datetime import datetime

        users_collection = get_users_collection()
        user_doc = users_collection.find_one({"google_id": user_id})

        if not user_doc:
            return jsonify({
                "success": False,
                "error": "User not found"
            }), 404

        razorpay_subscription_id = user_doc.get('razorpay_subscription_id')

        # Cancel on Razorpay if subscription ID exists
        if razorpay_subscription_id:
            try:
                razorpay_client.subscription.cancel(razorpay_subscription_id)
            except Exception as e:
                logger.warning(f"Failed to cancel Razorpay subscription: {e}")

        # Update user status
        users_collection.update_one(
            {"google_id": user_id},
            {
                "$set": {
                    "subscription_status": "cancelled",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return jsonify({
            "success": True,
            "message": "Subscription cancelled successfully"
        }), 200

    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to cancel subscription"
        }), 500
