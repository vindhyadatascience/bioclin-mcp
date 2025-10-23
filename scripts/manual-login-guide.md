# Manual Docker-Only Login Guide

If you want to avoid installing Python/Playwright on your host machine, you can manually capture your session cookies.

## Quick Login Steps

1. **Open Bioclin in your browser**: https://bioclin.vindhyadatascience.com/login

2. **Log in normally**

3. **Open DevTools** (press F12 or Cmd+Option+I on Mac)

4. **Go to Application/Storage tab** → Cookies → https://bioclin.vindhyadatascience.com

5. **Copy these three cookies**:
   - `access_token`
   - `refresh_token`
   - `csrf_token`

6. **Run this Docker command** with your cookies:

```bash
docker run -it --rm bioclin-mcp:latest python -c "
import json
from pathlib import Path
from datetime import datetime, timedelta

# Replace with your actual cookie values
cookies = {
    'access_token': 'YOUR_ACCESS_TOKEN_HERE',
    'refresh_token': 'YOUR_REFRESH_TOKEN_HERE',
    'csrf_token': 'YOUR_CSRF_TOKEN_HERE'
}

session = {
    'cookies': cookies,
    'user': {
        'email': 'your@email.com',
        'username': 'username',
        'id': 'user-id'
    },
    'created_at': datetime.now().isoformat(),
    'expires_at': (datetime.now() + timedelta(days=7)).isoformat()
}

session_file = Path.home() / '.bioclin_session.json'
session_file.write_text(json.dumps(session, indent=2))
print(f'✅ Session saved to {session_file}')
"
```

7. **Mount the session** when running the MCP server

## Alternative: CLI Login (No Browser)

If Bioclin supports username/password login via API:

```bash
docker run -it --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login
# Choose option 2 (CLI login)
# Enter username and password
```
