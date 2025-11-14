# Fix Google Calendar OAuth Error 403

## Problem
You're seeing: "Access blocked: Lumina has not completed the Google verification process"

This is because your Google Cloud OAuth app is in "Testing" mode.

## Solution: Add Your Email as Test User

### Step 1: Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### Step 2: Select Your Project
Make sure you're in the correct project where you created the OAuth credentials.

### Step 3: Navigate to OAuth Consent Screen
- Click on the menu (☰) in the top left
- Go to: **APIs & Services** → **OAuth consent screen**

### Step 4: Add Test Users
1. Scroll down to the **"Test users"** section
2. Click **"+ ADD USERS"** button
3. Enter your email: `heshamharoon19@gmail.com`
4. Click **"Save"**

### Step 5: Try Again
Now run the calendar authentication again:
```bash
source venv/bin/activate
python calendar_service.py
```

The authentication should work now!

---

## What This Does

When your OAuth app is in "Testing" mode, only users you explicitly add can authorize the app. This is a security feature by Google to prevent unauthorized access during development.

You have two options:
1. **Keep it in Testing mode** (recommended for personal use) - Add yourself as test user
2. **Publish the app** (not recommended) - Requires Google verification process

For personal use like Lumina, keeping it in Testing mode and adding yourself as a test user is the best approach.

---

## Screenshots to Help

When you're in the OAuth consent screen:

1. You'll see your app name at the top
2. Scroll down past the "Publishing status" section
3. Find the "Test users" section
4. Click "+ ADD USERS"
5. Type your email
6. Save

That's it! Your email will be whitelisted and the authentication will work.
