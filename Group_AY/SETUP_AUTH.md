# Google Authentication Setup Guide

This guide will help you set up Google OAuth authentication for the EduVideo AI application.

## Prerequisites

- A Google Cloud Platform account
- Your application running locally or deployed

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" at the top
3. Click "NEW PROJECT"
4. Enter a project name (e.g., "EduVideo AI")
5. Click "CREATE"

## Step 2: Enable Google OAuth

1. In your project, go to **APIs & Services** > **OAuth consent screen**
2. Select "External" user type and click "CREATE"
3. Fill in the required information:
   - App name: `EduVideo AI`
   - User support email: Your email
   - Developer contact information: Your email
4. Click "SAVE AND CONTINUE"
5. Skip the "Scopes" section (click "SAVE AND CONTINUE")
6. Add test users if needed, then click "SAVE AND CONTINUE"

## Step 3: Create OAuth Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click "CREATE CREDENTIALS" > "OAuth client ID"
3. Select "Web application"
4. Configure:
   - **Name**: EduVideo AI Web Client
   - **Authorized JavaScript origins**:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
   - **Authorized redirect URIs**:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
5. Click "CREATE"
6. **IMPORTANT**: Copy both the **Client ID** - you'll need this!

## Step 4: Configure Environment Variables

### Backend (.env)

Create or update `Backend/.env`:

```bash
# Your existing API keys
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
DID_API_KEY=your-did-api-key

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com

# JWT Secret (generate a random string)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
```

### Frontend (.env)

Create or update `Client/.env`:

```bash
# Leave empty when using Docker (nginx will proxy)
VITE_URL=

# Google OAuth Client ID (same as backend)
VITE_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

## Step 5: Generate a JWT Secret

Generate a secure JWT secret:

```bash
# Linux/Mac
openssl rand -base64 32

# Windows (PowerShell)
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

Add this value to the `JWT_SECRET` in your `.env` file.

## Step 6: Run the Application

### With Docker:

```bash
cd Backend
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Local Development:

**Backend:**
```bash
cd Backend
pip install -r requirements.txt
python api_server.py
```

**Frontend:**
```bash
cd Client
npm install
npm run dev
```

## Troubleshooting

### "Google OAuth not configured" error
- Verify `GOOGLE_CLIENT_ID` is set in `Backend/.env`
- Restart the backend server

### "redirect_uri_mismatch" error
- Check that your authorized redirect URIs in Google Console match your application URL
- Common mistake: Missing `http://` or `https://`

### Authentication fails silently
- Check browser console for errors
- Verify `VITE_GOOGLE_CLIENT_ID` is set in `Client/.env` (for local dev)
- Check that the Client ID matches between frontend and backend

### Token verification fails
- Ensure the Client ID in backend matches the one used in frontend
- Check that your JWT_SECRET is properly set

## Security Notes

- **Never commit** your `.env` files to version control
- Use different OAuth credentials for development and production
- Rotate your JWT_SECRET regularly in production
- Use HTTPS in production environments
- Consider implementing refresh tokens for better security

## Production Deployment

When deploying to production:

1. Create a new OAuth client ID for your production domain
2. Update the authorized origins and redirect URIs
3. Set all environment variables in your hosting platform
4. Use a strong, unique JWT_SECRET
5. Enable HTTPS for your domain
6. Consider moving from in-memory user storage to a database

## Additional Resources

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
