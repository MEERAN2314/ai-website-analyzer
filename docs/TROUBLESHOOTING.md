# Troubleshooting Guide

## Common Issues and Solutions

### 1. Registration Not Working

**Symptoms:**
- Signup form doesn't submit
- No error messages shown
- Console shows errors

**Solutions:**
1. Check MongoDB connection:
   ```bash
   python check_mongodb.py
   ```

2. Verify password requirements:
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one number
   - At least one special character
   - Example: `Test@123456`

3. Check server logs for errors:
   - Look for `Registration error:` messages
   - Check for MongoDB connection issues

4. Verify `.env` configuration:
   - `MONGODB_URL` is correct
   - `SECRET_KEY` is set

### 2. Analysis Taking Too Long / Stuck

**Symptoms:**
- Analysis shows "Loading analysis results..." forever
- Analysis never completes
- No results appear

**Solutions:**
1. **Check server logs** - Look for these messages:
   ```
   🔍 Starting analysis for <url>
   📊 Analysis <id>: Starting for <url>
   📊 Analysis <id>: Status updated to processing
   📊 Analysis <id>: Running analyzers...
   ✅ Analysis <id>: Completed successfully!
   ```

2. **Test with a simple URL first:**
   ```
   https://example.com
   ```

3. **Run the test script:**
   ```bash
   python test_analysis_flow.py
   ```

4. **Check for specific errors:**
   - **Rate limiter error**: Fixed in latest version (ObjectId bug)
   - **AI service error**: Check `GOOGLE_API_KEY` in `.env`
   - **Network error**: Check internet connection
   - **Timeout**: Try a faster website

5. **Restart the server:**
   ```bash
   # Stop the server (Ctrl+C)
   # Start again
   uvicorn app.main:app --reload
   ```

### 3. Login Not Working

**Symptoms:**
- Can't login after registration
- "Incorrect email or password" error

**Solutions:**
1. Verify you're using the correct email and password
2. Check if user was created:
   ```bash
   python check_mongodb.py
   ```
3. Try registering a new account
4. Check server logs for authentication errors

### 4. Pages Returning 404

**Symptoms:**
- `/login`, `/register`, `/analyze` return 404
- "Not Found" error

**Solutions:**
1. **This should be fixed** - Pages are now in `app/main.py`
2. Restart the server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Verify routes are loaded:
   - Check server startup logs
   - Should see route registrations

### 5. MongoDB Connection Issues

**Symptoms:**
- "Connection refused" errors
- "Authentication failed" errors

**Solutions:**
1. Check MongoDB Atlas connection string in `.env`
2. Verify IP whitelist in MongoDB Atlas (allow 0.0.0.0/0 for testing)
3. Test connection:
   ```bash
   python check_mongodb.py
   ```

### 6. Google Gemini API Errors

**Symptoms:**
- Analysis fails at AI summary generation
- "API key invalid" errors

**Solutions:**
1. Verify `GOOGLE_API_KEY` in `.env`
2. Check API key is valid at: https://makersuite.google.com/app/apikey
3. Ensure you have Gemini API access enabled
4. Check API quota/limits

## Testing Commands

### Test MongoDB Connection
```bash
python check_mongodb.py
```

### Test Registration Flow
```bash
python test_registration.py
```

### Test Analysis Flow
```bash
python test_analysis_flow.py
```

### Test Email (Optional)
```bash
python test_email.py
```

### Test Local Storage
```bash
python test_local_storage.py
```

## Server Logs to Watch

When running the server, watch for these key log messages:

### Successful Analysis Flow:
```
🔍 Starting analysis for https://example.com
📊 Analysis 507f1f77bcf86cd799439011: Starting for https://example.com
📊 Analysis 507f1f77bcf86cd799439011: Status updated to processing
📊 Analysis 507f1f77bcf86cd799439011: Initializing analyzers...
📊 Analysis 507f1f77bcf86cd799439011: Running analyzers...
📊 Analysis 507f1f77bcf86cd799439011: Analyzers completed
📊 Analysis 507f1f77bcf86cd799439011: Overall score calculated: 75.5
📊 Analysis 507f1f77bcf86cd799439011: Generating AI insights...
📊 Analysis 507f1f77bcf86cd799439011: AI insights generated
✅ Analysis 507f1f77bcf86cd799439011: Completed successfully!
```

### Error Indicators:
```
❌ Analysis error: <error message>
⚠️  UX analyzer error: <error>
⚠️  SEO analyzer error: <error>
Registration error: <error>
```

## Quick Fixes Applied

### ✅ Fixed: Rate Limiter ObjectId Bug
- **Issue**: Rate limiter was using string `user_id` instead of `ObjectId(user_id)`
- **Fix**: Added `from bson import ObjectId` and wrapped all user_id lookups
- **Files**: `app/utils/rate_limiter.py`

### ✅ Fixed: Analysis Running Synchronously
- **Issue**: Analysis was using background tasks requiring Celery
- **Fix**: Changed to run synchronously in the request
- **Files**: `app/api/v1/endpoints/analysis.py`

### ✅ Fixed: Page Routes 404
- **Issue**: Page routes were under `/api/v1/` prefix
- **Fix**: Moved page routes to `app/main.py`
- **Files**: `app/main.py`, `app/api/v1/router.py`

### ✅ Fixed: Better Error Logging
- **Issue**: Hard to debug analysis failures
- **Fix**: Added detailed logging with emojis for easy tracking
- **Files**: `app/services/analysis_service.py`, `app/api/v1/endpoints/analysis.py`

## Need More Help?

1. Check server terminal for error messages
2. Look for red ❌ or yellow ⚠️  emoji indicators in logs
3. Run the test scripts to isolate the issue
4. Check `.env` file for missing/incorrect configuration
5. Verify MongoDB Atlas connection and IP whitelist
