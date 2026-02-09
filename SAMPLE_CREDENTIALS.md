# Sample Login Credentials

## 🎯 Test Accounts for Different Plans

### 1. Free Plan (Guest User)
**No login required**
- Access: Direct website access
- Limit: 1 analysis per session
- Features: Basic analysis only
- No dashboard access

---

### 2. Basic Plan
**Email**: `basic@example.com`  
**Password**: `Basic@123`

**Plan Details:**
- Monthly Analyses: 10
- PDF Reports: ✅
- Dashboard Access: ✅
- Historical Data: Last 30 days
- AI Chat: 5 questions per analysis
- Priority Support: ❌
- API Access: ❌

---

### 3. Pro Plan
**Email**: `pro@example.com`  
**Password**: `Pro@123`

**Plan Details:**
- Monthly Analyses: 100
- PDF Reports: ✅
- Dashboard Access: ✅
- Historical Data: Unlimited
- AI Chat: Unlimited questions
- Competitor Analysis: ✅
- Priority Support: ✅
- API Access: ✅ (100 requests/day)
- Custom Branding: ❌

---

### 4. Enterprise Plan
**Email**: `enterprise@example.com`  
**Password**: `Enterprise@123`

**Plan Details:**
- Monthly Analyses: Unlimited
- PDF Reports: ✅
- Dashboard Access: ✅
- Historical Data: Unlimited
- AI Chat: Unlimited questions
- Competitor Analysis: ✅
- Multi-page Analysis: ✅
- Priority Support: ✅ (24/7)
- API Access: ✅ (Unlimited)
- Custom Branding: ✅
- White-label Solution: ✅
- Dedicated Account Manager: ✅
- Team Collaboration: ✅ (Up to 10 users)

---

## 🔐 Admin Account

**Email**: `admin@example.com`  
**Password**: `Admin@123`

**Admin Privileges:**
- View all users
- Manage subscriptions
- View system analytics
- Access logs
- Manage rate limits

---

## 📝 Notes

1. **Password Requirements:**
   - Minimum 8 characters
   - At least 1 uppercase letter
   - At least 1 lowercase letter
   - At least 1 number
   - At least 1 special character

2. **Security:**
   - These are sample credentials for development/testing only
   - Change all passwords in production
   - Use strong, unique passwords
   - Enable 2FA for production accounts

3. **Database Seeding:**
   - Run `python scripts/seed_users.py` to create these test accounts
   - Accounts will be created with proper plan assignments
   - Usage limits will be enforced based on plan

4. **Testing Workflow:**
   - Start with guest access (no login)
   - Test Basic plan limitations
   - Upgrade to Pro to test advanced features
   - Use Enterprise for full feature testing

---

## 🚀 Quick Test Commands

```bash
# Test Basic User Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"basic@example.com","password":"Basic@123"}'

# Test Pro User Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"pro@example.com","password":"Pro@123"}'

# Test Enterprise User Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"enterprise@example.com","password":"Enterprise@123"}'
```

---

**⚠️ IMPORTANT**: Never commit actual production credentials to version control!
