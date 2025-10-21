# OAuth 2.1 Authentication Setup Guide

This guide explains how to configure OAuth authentication for the Bioclin MCPX deployment.

## Quick Decision Matrix

| Provider | Best For | Complexity | Cost |
|----------|----------|------------|------|
| **Auth0** | Most use cases, enterprise SSO | Low | Free tier available |
| **Google OAuth** | Google Workspace integration | Low | Free |
| **Stytch** | Modern auth, passwordless | Medium | Free tier available |
| **WorkOS** | Enterprise SSO (SAML, OIDC) | Medium | Paid |
| **Custom** | Full control, existing auth | High | Variable |

## Recommended: Auth0 Setup

Auth0 is recommended for production deployment because:
- ✅ Free tier sufficient for most use cases
- ✅ Easy setup with good documentation
- ✅ Supports enterprise SSO
- ✅ Built-in user management
- ✅ Battle-tested security

### Step 1: Create Auth0 Account

1. Go to https://auth0.com
2. Sign up for free account
3. Create a new tenant (e.g., `bioclin-dev.us.auth0.com`)

### Step 2: Create API

1. In Auth0 Dashboard → Applications → APIs
2. Click "Create API"
3. Fill in:
   - **Name**: `MCPX Bioclin API`
   - **Identifier**: `mcpx-bioclin` (this becomes the `audience`)
   - **Signing Algorithm**: `RS256`
4. Click "Create"

### Step 3: Define Permissions (Scopes)

In your API settings → Permissions tab:

Add these scopes:
- `read:tools` - List and view available tools
- `execute:tools` - Execute MCP tools
- `read:profile` - Read user profile information

### Step 4: Create Application

1. In Auth0 Dashboard → Applications → Applications
2. Click "Create Application"
3. Fill in:
   - **Name**: `MCPX Client`
   - **Type**: `Machine to Machine Applications` (for service-to-service)
   - OR `Single Page Application` (for web chatbot)
4. Select your API (`MCPX Bioclin API`)
5. Grant all permissions

### Step 5: Get Credentials

From your application settings, copy:
- **Domain** (e.g., `bioclin-dev.us.auth0.com`)
- **Client ID**
- **Client Secret**

### Step 6: Configure MCPX

1. Create `.env` file:
   ```bash
   cp mcpx-config/.env.template mcpx-config/.env
   ```

2. Edit `.env`:
   ```bash
   AUTH0_DOMAIN=bioclin-dev.us.auth0.com
   AUTH0_CLIENT_ID=your_client_id_here
   AUTH0_CLIENT_SECRET=your_client_secret_here
   BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1
   ```

3. Update `app.yaml`:
   ```bash
   # Copy auth config from app-with-auth.yaml
   # Or just enable auth in existing app.yaml:
   sed -i '' 's/enabled: false/enabled: true/' mcpx-config/app.yaml
   ```

### Step 7: Test Locally

```bash
# Get access token
curl --request POST \
  --url "https://${AUTH0_DOMAIN}/oauth/token" \
  --header 'content-type: application/json' \
  --data '{
    "client_id":"${AUTH0_CLIENT_ID}",
    "client_secret":"${AUTH0_CLIENT_SECRET}",
    "audience":"mcpx-bioclin",
    "grant_type":"client_credentials"
  }'

# Use token to call MCPX
export TOKEN="your_access_token_here"

curl -X POST http://localhost:9000/mcp \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}'
```

## Alternative: Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create new project: `bioclin-mcpx`
3. Enable APIs: `Google+ API`, `Identity Toolkit API`

### Step 2: Create OAuth 2.0 Credentials

1. Go to APIs & Services → Credentials
2. Create OAuth 2.0 Client ID
3. Application type: `Web application`
4. Authorized redirect URIs:
   - `http://localhost:9000/auth/callback` (local)
   - `https://your-service.run.app/auth/callback` (production)

### Step 3: Configure MCPX

Update `.env`:
```bash
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:9000/auth/callback
```

Update `app.yaml` - use Google OAuth config from `app-with-auth.yaml`

## Alternative: Custom OAuth Server

If you have an existing OAuth 2.1 server:

### Prerequisites

Your OAuth server must support:
- ✅ OAuth 2.1 / OIDC specification
- ✅ JWT tokens with RS256/ES256 signing
- ✅ JWKS endpoint for token verification
- ✅ Standard claims: `sub`, `exp`, `iat`, `aud`, `iss`

### Configuration

Update `.env`:
```bash
OAUTH_ISSUER_URL=https://your-auth-server.com
OAUTH_CLIENT_ID=your_client_id
OAUTH_CLIENT_SECRET=your_client_secret
```

Update `app.yaml` - use custom OAuth config from `app-with-auth.yaml`

## User Management Integration

### Option 1: Separate Auth from Bioclin

Users authenticate with OAuth provider (Auth0/Google) first, then:
- Use `bioclin_login` tool to authenticate with Bioclin API
- MCPX manages OAuth session
- Bioclin MCP server manages Bioclin API session

**Flow:**
```
User → OAuth Login → Get JWT → Call MCPX with JWT →
  → MCPX validates JWT → Call bioclin_login tool →
    → Bioclin API session created → Use other tools
```

### Option 2: Federated Auth (Advanced)

Configure Bioclin to accept OAuth tokens directly:
- Bioclin validates same JWT tokens
- Single sign-on experience
- Requires Bioclin API changes

## Security Best Practices

### For Production

1. **Always enable HTTPS**
   - Use Cloud Run's automatic HTTPS
   - Never disable certificate validation

2. **Rotate secrets regularly**
   - Rotate client secrets every 90 days
   - Use Google Secret Manager for storage

3. **Use short-lived tokens**
   - Access tokens: 15-60 minutes
   - Refresh tokens: 7-30 days
   - Configure in OAuth provider

4. **Implement rate limiting**
   - Enable in `app.yaml`
   - Configure per-consumer limits

5. **Audit logging**
   - Enable Cloud Logging
   - Log all authentication attempts
   - Monitor for suspicious activity

6. **Principle of least privilege**
   - Grant minimum required scopes
   - Use tool groups for fine-grained control
   - Review permissions regularly

### Token Validation

MCPX automatically validates:
- ✅ Token signature (using JWKS)
- ✅ Expiration (`exp` claim)
- ✅ Audience (`aud` claim)
- ✅ Issuer (`iss` claim)
- ✅ Not-before (`nbf` claim)

## Troubleshooting

### "Invalid token" errors

1. Check token expiration: `jwt.io` to decode token
2. Verify `audience` matches API identifier
3. Check clock skew between systems
4. Ensure JWKS cache is refreshed

### "Insufficient permissions" errors

1. Verify scopes in token
2. Check consumer mapping in `app.yaml`
3. Review tool group permissions
4. Check Auth0 API permissions granted to application

### CORS errors (for web chatbots)

1. Enable CORS in `app.yaml`
2. Add your domain to `allowedOrigins`
3. Include `Authorization` in `allowedHeaders`

## Testing

Test script with authentication:

```bash
#!/bin/bash
# test-auth.sh

# Get token
TOKEN=$(curl -s --request POST \
  --url "https://${AUTH0_DOMAIN}/oauth/token" \
  --header 'content-type: application/json' \
  --data "{
    \"client_id\":\"${AUTH0_CLIENT_ID}\",
    \"client_secret\":\"${AUTH0_CLIENT_SECRET}\",
    \"audience\":\"mcpx-bioclin\",
    \"grant_type\":\"client_credentials\"
  }" | jq -r '.access_token')

echo "Got token: ${TOKEN:0:20}..."

# Test authenticated request
curl -X POST http://localhost:9000/mcp \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq .
```

## Next Steps

After auth is configured:
1. ✅ Test locally with authentication enabled
2. ⏭️ Deploy to Cloud Run with secrets
3. ⏭️ Configure chatbot client with OAuth flow
4. ⏭️ Monitor auth logs and metrics
