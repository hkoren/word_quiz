# Google OAuth Setup Guide for Spelling Quiz

## Setting up Google OAuth Authentication

To enable Google OAuth authentication, you need to create credentials in the Google Cloud Console:

### 1. Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API or Google Identity API

### 2. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. Configure the OAuth consent screen first if prompted
4. Choose **Web application** as the application type
5. Add authorized redirect URIs:
   - For development: `http://127.0.0.1:5557/auth/google/callback`
   - For production: `https://yourdomain.com/auth/google/callback`

### 3. Configure Environment Variables

Set the following environment variables with your Google OAuth credentials:

```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

### 4. Development Mode

If no environment variables are set, the application will run in development mode with dummy credentials. Google OAuth buttons will be visible but won't work until real credentials are configured.

### 5. Production Deployment

For production deployment:
1. Set the environment variables on your server
2. Update the redirect URI to match your domain
3. Ensure HTTPS is enabled
4. Remove the `OAUTHLIB_INSECURE_TRANSPORT` setting

## Testing

1. Start the application: `python3 web_quiz.py`
2. Visit the login page
3. You should see both "Sign In" and "Sign in with Google" buttons
4. Google OAuth will only work with valid credentials configured

## Features

- **Automatic Account Creation**: New Google users are automatically created
- **Email Conflict Handling**: Prevents Google users from overriding existing email accounts
- **Mixed Authentication**: Users can have both local and Google accounts
- **Profile Integration**: User profiles show the authentication method used