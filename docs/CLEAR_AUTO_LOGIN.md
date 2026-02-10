# How to Clear Auto-Login / Demo Session

## Problem
The application automatically logs you in with "user@example.com" when you open it. This is because there's a demo/test token stored in your browser's localStorage.

## Solution - 3 Easy Methods

### Method 1: Visit Clear Session Page (Easiest)
1. Open your browser
2. Go to: `http://127.0.0.1:8000/clear-session`
3. Wait 1 second - you'll be automatically redirected to homepage
4. You're now logged out!

### Method 2: Use Browser Console
1. Open your browser
2. Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac)
3. Go to the "Console" tab
4. Type this command and press Enter:
   ```javascript
   localStorage.clear(); location.reload();
   ```
5. Done! The page will refresh and you'll be logged out

### Method 3: Clear Browser Data
1. Open your browser settings
2. Go to Privacy/Security settings
3. Clear browsing data
4. Select "Cookies and other site data"
5. Clear data for `127.0.0.1:8000`
6. Refresh the page

## Prevent Auto-Login in Future

The demo token was likely set during testing. To prevent this:

1. **Never commit tokens to code** - Always use environment variables
2. **Clear localStorage after testing** - Use Method 1 or 2 above
3. **Use incognito/private mode for testing** - No persistent storage

## For Developers

If you want to add a "Logout" button that clears everything:

```javascript
function logout() {
    localStorage.clear();
    window.location.href = '/';
}
```

Or use the existing logout function in `app/static/js/main.js`:
```javascript
async function logout() {
    removeToken();
    window.location.href = '/';
}
```

## Verification

After clearing, you should see:
- ✅ "Login" and "Get Started" buttons in navbar
- ✅ No user menu dropdown
- ✅ No "My Account" section
- ✅ Landing page shows as guest user

If you still see the user menu, try:
1. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
2. Clear browser cache completely
3. Try a different browser or incognito mode
