# Payment Gateway Implementation - Razorpay Integration

This document describes the complete payment gateway integration for the AI Educational Video Generator using Razorpay.

## Overview

The application now includes a **hybrid pricing model** with:
- **Free Tier**: 1 video per account (lifetime), max 1 minute duration, no avatar
- **Pro Tier**: ₹499/month or ₹4999/year - 50 videos/month, up to 10 minutes, avatars enabled
- **Credit Packages**: Additional video credits that can be purchased (10, 25, or 100 videos)

## Features Implemented

### Backend (Flask/Python)

#### 1. **Database Models** (`models.py`)
Added subscription and payment tracking:
- **User Model** - Extended with:
  - `subscription_tier`: free/pro
  - `subscription_status`: active/cancelled/expired
  - `credits`: Additional video credits
  - `usage`: Track videos generated and reset dates

- **Subscription Model** - New model for tracking subscriptions
- **Transaction Model** - New model for payment history

#### 2. **Subscription Manager** (`subscription_manager.py`)
Core business logic:
- `get_pricing_info()`: Returns all pricing tiers and packages
- `check_can_generate_video()`: Validates if user can generate based on limits
- `increment_usage()`: Tracks video generation count or deducts credits
- `upgrade_to_pro()`: Activates Pro subscription
- `add_credits()`: Adds purchased credits to user account

**Pricing Configuration:**
```python
FREE_TIER = {
    "videos_per_account": 1,
    "max_video_duration": 60,  # seconds
    "avatar_enabled": False
}

PRO_TIER = {
    "price": 499,  # monthly
    "videos_per_month": 50,
    "max_video_duration": 600,  # 10 minutes
    "avatar_enabled": True
}
```

#### 3. **Payment Routes** (`payment_routes.py`)
RESTful API endpoints:

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/pricing` | GET | No | Get pricing information |
| `/api/subscription/status` | GET | Yes | Get user's subscription status |
| `/api/payment/create-order` | POST | Yes | Create Razorpay order |
| `/api/payment/verify` | POST | Yes | Verify payment signature |
| `/api/payment/webhook` | POST | No | Handle Razorpay webhooks |
| `/api/transactions` | GET | Yes | Get transaction history |
| `/api/subscription/cancel` | POST | Yes | Cancel subscription |

#### 4. **Updated API Server** (`api_server.py`)
- **Modified `/api/generate`** endpoint:
  - Now requires authentication (`@require_auth`)
  - Checks subscription limits before processing
  - Tracks usage after successful generation
  - Returns 403 if limits exceeded

- **Modified `/api/auth/me`** endpoint:
  - Now includes full subscription information

#### 5. **Environment Variables** (`.env.example`)
Added Razorpay configuration:
```bash
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
RAZORPAY_WEBHOOK_SECRET=your-razorpay-webhook-secret
```

### Frontend (React/TypeScript)

#### 1. **Pricing Page** (`src/pages/Pricing.tsx`)
Beautiful, responsive pricing page with:
- Free and Pro plan comparison
- Real-time subscription status display
- Credit package cards
- Razorpay checkout integration
- Automatic redirect after successful payment

**Features:**
- Shows current plan and usage
- "Upgrade Now" button for free users
- Credit purchase options
- Mobile-responsive design

#### 2. **Updated Header** (`src/components/home/header.tsx`)
Added subscription status display:
- Shows current tier (Free/Pro with crown icon)
- Displays usage count (e.g., "3/50")
- Clickable to navigate to pricing page

#### 3. **Updated Chat Container** (`src/components/home/chatContainer.tsx`)
Enhanced error handling:
- Sends Authorization header with API requests
- Catches 403 errors (subscription limit)
- Displays user-friendly error with upgrade link
- Shows markdown links to pricing page

#### 4. **Updated Landing Page** (`src/pages/Landing.tsx`)
- Added "Pricing" link to header
- Added pricing teaser section showing Free vs Pro
- Clear CTAs to view full pricing

#### 5. **Updated Routes** (`src/App.tsx`)
Added `/pricing` route accessible to all users

## Setup Instructions

### 1. Razorpay Account Setup

1. **Create Razorpay Account**
   - Go to https://dashboard.razorpay.com/signup
   - Complete registration and KYC verification

2. **Get API Keys**
   - Go to Settings → API Keys
   - Generate Test/Live keys
   - Copy `Key ID` and `Key Secret`

3. **Configure Webhook** (Optional, for recurring subscriptions)
   - Go to Settings → Webhooks
   - Add webhook URL: `https://yourdomain.com/api/payment/webhook`
   - Select events: `payment.captured`, `subscription.charged`, `subscription.cancelled`
   - Copy webhook secret

### 2. Backend Configuration

1. **Install Dependencies**
   ```bash
   cd Group_AY/Backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add:
   RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=your_secret_key
   RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
   ```

3. **Initialize MongoDB**
   - The new collections (subscriptions, transactions) will be created automatically
   - Existing users will be migrated to free tier on first API call

### 3. Frontend Configuration

1. **No additional dependencies needed**
   - Razorpay SDK loaded via CDN in Pricing page

2. **Environment Variables**
   - Already configured in `.env` (VITE_URL for backend API)

### 4. Testing

#### Test Mode (Razorpay Test Keys)

1. **Test Payment**
   - Navigate to `/pricing`
   - Click "Upgrade to Pro"
   - Use Razorpay test cards:
     - Success: `4111 1111 1111 1111`
     - CVV: Any 3 digits
     - Expiry: Any future date

2. **Test Credit Purchase**
   - Click "Buy Credits" on any package
   - Complete payment with test card
   - Check header to see updated credit count

#### Production Mode

1. Replace test keys with live keys in `.env`
2. Enable live mode in Razorpay dashboard
3. Complete KYC verification
4. Test with real payment

## Usage Flow

### For Users

1. **Sign Up (Free)**
   - New users get Free tier automatically
   - Can generate 1 video (up to 1 minute)

2. **Upgrade to Pro**
   - Navigate to `/pricing`
   - Click "Upgrade to Pro"
   - Complete Razorpay checkout
   - Get 50 videos/month + avatar feature

3. **Purchase Credits** (Hybrid Model)
   - Buy credit packages at any time
   - Credits work across Free and Pro tiers
   - Credits deducted when monthly limit exhausted

4. **Generate Videos**
   - System checks limits before generation
   - Shows clear error if limit reached
   - Provides upgrade link

### For Admins

**View Transactions:**
```bash
# MongoDB query to see all transactions
db.transactions.find({}).sort({created_at: -1})
```

**Check User Subscription:**
```bash
# MongoDB query
db.users.findOne({email: "user@example.com"})
```

**Manual Subscription Update:**
```python
from subscription_manager import upgrade_to_pro
upgrade_to_pro(user_id="google_12345", billing_cycle="monthly")
```

## API Examples

### 1. Create Order (Subscription)
```bash
curl -X POST http://localhost:5000/api/payment/create-order \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "subscription",
    "plan": "pro_monthly"
  }'
```

### 2. Create Order (Credits)
```bash
curl -X POST http://localhost:5000/api/payment/create-order \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "credits",
    "plan": "medium"
  }'
```

### 3. Check Subscription Status
```bash
curl http://localhost:5000/api/subscription/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Security Considerations

✅ **Implemented:**
- Payment signature verification
- JWT token authentication
- User ownership validation
- HTTPS recommended for production
- Environment variable for secrets

⚠️ **Recommendations:**
- Enable rate limiting on payment endpoints
- Add request validation schemas
- Implement audit logging
- Use secure webhook secrets
- Enable CORS only for your domain
- Monitor for suspicious payment patterns

## Troubleshooting

### Payment Fails
- Check Razorpay dashboard for error details
- Verify API keys are correct
- Ensure webhook signature is valid

### Subscription Not Updated
- Check transaction status in database
- Verify payment webhook received
- Check Flask logs for errors

### Usage Not Tracked
- Ensure video generation completes successfully
- Check `increment_usage()` is called after generation
- Verify MongoDB connection

## File Structure

```
Group_AY/
├── Backend/
│   ├── models.py                    # Extended with Subscription & Transaction
│   ├── database.py                  # Added new collections
│   ├── subscription_manager.py      # NEW: Business logic
│   ├── payment_routes.py            # NEW: Payment API
│   ├── api_server.py                # Updated: Usage tracking
│   ├── requirements.txt             # Added: razorpay>=1.4.0
│   └── .env.example                 # Added: Razorpay keys
│
└── Client/
    ├── src/
    │   ├── pages/
    │   │   ├── Pricing.tsx          # NEW: Pricing page
    │   │   └── Landing.tsx          # Updated: Pricing teaser
    │   ├── components/
    │   │   └── home/
    │   │       ├── header.tsx       # Updated: Subscription status
    │   │       └── chatContainer.tsx # Updated: Error handling
    │   └── App.tsx                  # Updated: Added /pricing route
```

## Next Steps

1. **Customize Pricing**
   - Edit `PRICING` dict in `subscription_manager.py`
   - Update frontend `Pricing.tsx` to match

2. **Add Features**
   - Implement yearly subscription with auto-renewal
   - Add usage analytics dashboard
   - Email notifications for subscription events
   - Promo codes/coupons

3. **Production Deployment**
   - Switch to live Razorpay keys
   - Enable HTTPS
   - Set up monitoring
   - Configure backup payment methods

## Support

For issues or questions:
- Razorpay Docs: https://razorpay.com/docs/
- Razorpay Support: https://razorpay.com/support/

---

**Implementation Date:** 2025-11-14
**Version:** 1.0
**Payment Gateway:** Razorpay
**Currency:** INR (₹)
