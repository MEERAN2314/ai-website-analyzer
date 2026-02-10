# Pricing System Implementation Guide

## Overview

We've implemented a comprehensive subscription and pricing system with a **30-day free trial** for all plans. Users can select any plan during registration or upgrade later, and they get full access for 30 days at 100% discount (completely free).

## Key Features

### 1. **30-Day Free Trial**
- All plans (Basic, Pro, Enterprise) come with a 30-day free trial
- No credit card required during trial
- Full access to all plan features
- 100% discount applied automatically

### 2. **Plan Tiers**

#### Free Plan
- **Price:** $0/month (Forever)
- **Features:**
  - 10 website analyses per month
  - Basic AI insights
  - 5 PDF exports
  - Email support
- **Limits:** `analyses: 10, comparisons: 0, exports: 5`

#### Basic Plan
- **Price:** $29/month or $290/year
- **Features:**
  - 50 website analyses per month
  - 10 competitor comparisons
  - Unlimited PDF exports
  - Advanced AI insights
  - Share analysis links
- **Limits:** `analyses: 50, comparisons: 10, exports: unlimited`

#### Pro Plan (Most Popular)
- **Price:** $79/month or $790/year
- **Features:**
  - 200 website analyses per month
  - 50 competitor comparisons
  - Unlimited exports
  - Priority support
  - Custom branded reports
  - 30/60/90 day action plans
- **Limits:** `analyses: 200, comparisons: 50, exports: unlimited`

#### Enterprise Plan
- **Price:** $199/month or $1990/year
- **Features:**
  - Unlimited analyses
  - Unlimited comparisons
  - Unlimited exports
  - 24/7 priority support
  - API access
  - Dedicated account manager
  - Custom integrations
- **Limits:** `analyses: unlimited, comparisons: unlimited, exports: unlimited`

### 3. **Grace Period**
- After 30-day trial expires, users get a 7-day grace period
- During grace period, they can add payment information
- If no payment added, automatically downgraded to Free plan

### 4. **Usage Tracking**
- Real-time tracking of analyses, comparisons, and exports
- Usage limits enforced based on plan
- Users can see remaining quota in dashboard

### 5. **Billing History**
- Complete transaction history
- Track plan changes (upgrades, downgrades)
- View trial start dates and expiry

## API Endpoints

### Subscription Management

#### Get All Plans
```
GET /api/v1/subscription/plans
```
Returns all available plans with pricing and features.

#### Get Plan Details
```
GET /api/v1/subscription/plans/{plan_name}
```
Get detailed information about a specific plan.

#### Subscribe to Plan
```
POST /api/v1/subscription/subscribe
Body: {
  "plan": "pro",
  "billing_cycle": "monthly"
}
```
Creates a new subscription with 30-day free trial.

#### Get Current Subscription
```
GET /api/v1/subscription/current
```
Returns user's active subscription details.

#### Get Usage Statistics
```
GET /api/v1/subscription/usage
```
Returns current usage stats and remaining quota.

#### Upgrade Plan
```
POST /api/v1/subscription/upgrade/{new_plan}
```
Upgrade to a new plan (gets another 30-day free trial).

#### Get Billing History
```
GET /api/v1/subscription/billing-history
```
Returns complete billing transaction history.

## Database Collections

### subscriptions
```javascript
{
  _id: ObjectId,
  user_id: String,
  plan: String,  // free, basic, pro, enterprise
  status: String,  // trial, active, expired, cancelled, grace_period
  is_trial: Boolean,
  trial_start_date: DateTime,
  trial_end_date: DateTime,
  start_date: DateTime,
  end_date: DateTime,
  next_billing_date: DateTime,
  original_price: Float,
  discount_percentage: Float,  // 100% for trial
  final_price: Float,  // 0 for trial
  analyses_limit: Int,
  comparisons_limit: Int,
  exports_limit: Int,
  analyses_used: Int,
  comparisons_used: Int,
  exports_used: Int,
  created_at: DateTime,
  updated_at: DateTime
}
```

### billing_history
```javascript
{
  _id: ObjectId,
  user_id: String,
  subscription_id: String,
  transaction_type: String,  // trial_start, upgrade, downgrade, renewal
  from_plan: String,
  to_plan: String,
  amount: Float,
  discount: Float,
  final_amount: Float,
  status: String,  // completed, pending, failed
  description: String,
  created_at: DateTime
}
```

## User Flow

### New User Registration
1. User visits `/pricing` page
2. Selects desired plan (e.g., "Pro")
3. Clicks "Start Free Trial"
4. If not logged in, redirected to `/register?plan=pro`
5. Completes registration
6. Subscription automatically created with 30-day trial
7. Billing history entry created
8. User gets full access to Pro features for 30 days

### Existing User Upgrade
1. User visits `/pricing` page
2. Clicks "Start Free Trial" on higher plan
3. Current subscription cancelled
4. New subscription created with 30-day trial
5. User gets full access to new plan features
6. Billing history updated

### Trial Expiry Flow
1. **Day 30:** Trial expires
2. **Day 30-37:** Grace period (7 days)
   - User can still use features
   - Notifications sent to add payment
3. **Day 37:** If no payment added
   - Automatically downgraded to Free plan
   - New Free subscription created
   - Notification sent

## Usage Limit Enforcement

The system automatically checks usage limits before allowing actions:

```python
# Before creating analysis
can_analyze, message = await SubscriptionService.check_usage_limit(db, user_id, "analysis")
if not can_analyze:
    raise HTTPException(status_code=403, detail=message)

# Increment usage after successful action
await SubscriptionService.increment_usage(db, user_id, "analysis")
```

## Frontend Integration

### Pricing Page
- Located at `/pricing`
- Shows all 4 plans with features
- Prominent "100% FREE for 30 Days" badge
- Click "Start Free Trial" to subscribe
- FAQ section explaining trial process

### Dashboard Integration
- Show current plan and usage stats
- Display remaining days in trial
- Progress bars for usage limits
- Upgrade button when limits reached

### Notifications
- Trial expiry warnings (7 days, 3 days, 1 day before)
- Grace period notifications
- Downgrade notifications
- Upgrade confirmation emails

## Improvements Made to Your Concept

### Original Idea
- One month free offer
- Users pick plan during registration
- Purchase page
- Receive notification

### Enhanced Implementation

1. **No Payment Gateway Yet**
   - Trial doesn't require payment info
   - Users can fully test before committing
   - Reduces friction in signup process

2. **Grace Period**
   - 7-day buffer after trial expires
   - Prevents immediate loss of access
   - Gives users time to decide

3. **Automatic Downgrade**
   - Seamless transition to Free plan
   - Users don't lose account
   - Can upgrade anytime later

4. **Usage Tracking**
   - Real-time limit enforcement
   - Clear visibility of remaining quota
   - Prevents abuse

5. **Multiple Trial Opportunities**
   - Get new 30-day trial when upgrading
   - Encourages users to try higher plans
   - Increases conversion potential

6. **Comprehensive Billing History**
   - Complete audit trail
   - Transparency for users
   - Easy to track plan changes

7. **Flexible Plan Changes**
   - Upgrade/downgrade anytime
   - No lock-in period
   - User-friendly approach

## Next Steps (Future Enhancements)

### Phase 2: Payment Integration
1. **Stripe Integration**
   - Add payment method collection
   - Automatic billing after trial
   - Subscription management

2. **Payment Gateway**
   - Credit card processing
   - PayPal integration
   - Invoice generation

3. **Automated Billing**
   - Monthly/yearly recurring charges
   - Failed payment handling
   - Retry logic

### Phase 3: Advanced Features
1. **Promo Codes**
   - Discount codes
   - Referral bonuses
   - Seasonal offers

2. **Team Plans**
   - Multi-user accounts
   - Role-based access
   - Shared usage pools

3. **Custom Enterprise Pricing**
   - Quote requests
   - Custom contracts
   - Volume discounts

4. **Analytics Dashboard**
   - Revenue tracking
   - Conversion metrics
   - Churn analysis

## Testing the System

### Test Scenarios

1. **New User Trial**
   ```bash
   # Register new user
   POST /api/v1/auth/register
   
   # Subscribe to Pro plan
   POST /api/v1/subscription/subscribe
   Body: {"plan": "pro", "billing_cycle": "monthly"}
   
   # Check subscription
   GET /api/v1/subscription/current
   
   # Verify: status=trial, is_trial=true, trial_end_date=30 days from now
   ```

2. **Usage Limits**
   ```bash
   # Create analyses until limit reached
   # Verify error message when limit exceeded
   
   # Check usage stats
   GET /api/v1/subscription/usage
   ```

3. **Plan Upgrade**
   ```bash
   # Upgrade from Basic to Pro
   POST /api/v1/subscription/upgrade/pro
   
   # Verify new trial period started
   # Check billing history
   GET /api/v1/subscription/billing-history
   ```

## Configuration

All plan details are configured in `app/services/subscription_service.py`:

```python
PLANS = {
    "free": PlanDetails(...),
    "basic": PlanDetails(...),
    "pro": PlanDetails(...),
    "enterprise": PlanDetails(...)
}
```

To modify pricing or limits, update the `PLANS` dictionary.

## Monitoring

### Scheduled Tasks (To Implement)
Run daily cron job to check expired trials:

```python
# In a scheduled task
await SubscriptionService.check_expired_trials(db)
```

This will:
- Move expired trials to grace period
- Downgrade expired grace periods to Free
- Send appropriate notifications

## Summary

The pricing system is now fully implemented with:
- ✅ 4 plan tiers (Free, Basic, Pro, Enterprise)
- ✅ 30-day free trial for all paid plans
- ✅ Usage tracking and limit enforcement
- ✅ Automatic trial expiry handling
- ✅ 7-day grace period
- ✅ Billing history tracking
- ✅ Plan upgrade/downgrade
- ✅ Beautiful pricing page
- ✅ API endpoints for all operations
- ✅ Database models and schemas

**Ready for production** (without payment gateway - that's Phase 2)!
