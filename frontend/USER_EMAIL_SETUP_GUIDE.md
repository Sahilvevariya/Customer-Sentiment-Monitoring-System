# User Email Setup Guide

## How Email Configuration Works for New Users

### 🔐 **Authentication Flow**

1. **User Signs Up/Logs In** via Clerk authentication
2. **Real User ID** is automatically used instead of `default_user`
3. **Email Configuration** is saved per user
4. **Monitoring** works with user-specific email accounts

### 📧 **Email Setup Process**

#### Step 1: Navigate to Gmail Setup
- Go to `/gmail-setup` in your application
- Or click "Configure Gmail" from the Start Monitoring page

#### Step 2: Fill in Your Gmail Credentials
```
Gmail Address: your.email@gmail.com
Gmail App Password: [Generate from Google Account]
Telegram User ID: [Optional - for notifications]
```

#### Step 3: Generate Gmail App Password
1. Go to your Google Account settings
2. Navigate to **Security** → **2-Step Verification** → **App passwords**
3. Select "Mail" and your device
4. Copy the 16-character password

#### Step 4: Save Configuration
- Click "Save Configuration"
- System automatically resets data for fresh start
- Configuration is saved for your specific user ID

### 🔄 **How It Works**

#### For New Users:
1. **User ID**: `user_2abc123def456` (from Clerk)
2. **Email Config**: Saved with this specific user ID
3. **Monitoring**: Uses this user's email configuration
4. **Data**: All analytics stored per user

#### For Existing Users:
1. **User ID**: Same Clerk user ID
2. **Email Config**: Retrieved for this user
3. **Monitoring**: Continues with existing configuration
4. **Data**: User-specific analytics maintained

### 🛠 **Technical Implementation**

#### Frontend Changes:
- ✅ Uses `useUser()` from Clerk to get real user ID
- ✅ Passes user ID to all API calls
- ✅ Email configuration saved per user

#### Backend Changes:
- ✅ Email config stored with user ID
- ✅ Monitoring uses user-specific configuration
- ✅ Data analytics separated by user

### 🚀 **Testing the Flow**

1. **Sign up** with a new account
2. **Navigate** to Gmail Setup
3. **Configure** your email credentials
4. **Start monitoring** - it will use your specific email
5. **Check** that data is user-specific

### 🔍 **Verification**

To verify it's working:
1. Check browser console for user ID logs
2. Verify email config is saved with correct user ID
3. Confirm monitoring starts without errors
4. Check that data is isolated per user

### 📝 **Example User Flow**

```
User A (user_123) → Gmail: alice@gmail.com → Monitoring: Alice's emails
User B (user_456) → Gmail: bob@gmail.com   → Monitoring: Bob's emails
```

Each user has their own:
- ✅ Email configuration
- ✅ Monitoring session
- ✅ Analytics data
- ✅ Sentiment history

### 🎯 **Key Benefits**

1. **Multi-tenant**: Multiple users can use the system
2. **Data Isolation**: Each user's data is separate
3. **Personalized**: Each user monitors their own emails
4. **Secure**: User-specific authentication and data 