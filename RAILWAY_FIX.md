# 🚂 Railway Deployment Fix - Railpack Error Resolution

## Problem Solved ✅

**Error:** "Error creating build plan with Railpack"

**Root Cause:** 
- Empty `yarn.lock` file at project root confused Railway's Railpack auto-detection
- No clear project structure indicators for multi-service Docker Compose setup

## What Was Changed

### 1. Removed Misleading File
- ❌ Deleted: `/yarn.lock` (root level, empty file)

### 2. Added Railway Configuration Files

#### Root Configuration (`/railway.json`)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "echo 'This is a multi-service project. Deploy frontend and backend separately.'",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Backend Configuration (`/backend/railway.json`)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn server:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Frontend Configuration (`/frontend/railway.json`)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "nginx -g 'daemon off;'",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 3. Added Nixpacks Configuration Files

#### Backend Nixpacks (`/backend/nixpacks.toml`)
```toml
[phases.setup]
nixPkgs = ["python311"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["mkdir -p uploads"]

[start]
cmd = "uvicorn server:app --host 0.0.0.0 --port $PORT"
```

#### Frontend Nixpacks (`/frontend/nixpacks.toml`)
```toml
[phases.setup]
nixPkgs = ["nodejs_20", "yarn"]

[phases.install]
cmds = ["yarn install --frozen-lockfile"]

[phases.build]
cmds = ["yarn build"]

[start]
cmd = "npx serve -s build -l $PORT"
```

### 4. Updated Frontend Dependencies
- Added `serve` package for serving the production build in Railway

## How to Deploy on Railway Now

### Option 1: Deploy Each Service Separately (Recommended)

#### Step 1: Deploy Backend
1. Go to Railway Dashboard
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Click **"Add Service"**
6. Select **"Deploy from a monorepo"**
7. Set **Root Directory:** `backend`
8. Railway will automatically use `backend/railway.json` and `backend/Dockerfile`

**Environment Variables for Backend:**
```
MONGO_URL=mongodb://mongodb:27017
DB_NAME=educando_db
JWT_SECRET=your-secure-secret-key-here
PORT=8001
```

#### Step 2: Deploy Frontend
1. In the same project, click **"New Service"**
2. Select your repository again
3. Click **"Deploy from a monorepo"**
4. Set **Root Directory:** `frontend`
5. Railway will automatically use `frontend/railway.json` and `frontend/Dockerfile`

**Environment Variables for Frontend:**
```
REACT_APP_BACKEND_URL=https://your-backend-url.railway.app
PORT=80
```

#### Step 3: Add MongoDB
1. Click **"New Service"**
2. Select **"Database"**
3. Choose **"MongoDB"**
4. Railway will provision MongoDB automatically
5. Copy the connection URL and update your Backend's `MONGO_URL` variable

### Option 2: Use Docker Compose (Alternative)

Railway also supports Docker Compose, but you'll need to deploy as a single service:

1. Create a new project
2. Deploy from GitHub
3. Railway will detect `docker-compose.yml`
4. Set environment variables for all services

**Note:** This method may have limitations with Railway's free tier.

## Verification Steps

After deployment:

1. **Check Backend:**
   ```bash
   curl https://your-backend-url.railway.app/
   ```
   Should return: `{"message": "API is running"}`

2. **Check Frontend:**
   Open `https://your-frontend-url.railway.app` in browser
   You should see the login page

3. **Check Database Connection:**
   Backend logs should show: "Connected to MongoDB"

## Common Issues and Solutions

### Issue 1: Build Still Fails
**Solution:** Make sure you selected the correct root directory (`backend` or `frontend`) when deploying

### Issue 2: Frontend Can't Connect to Backend
**Solution:** Update the `REACT_APP_BACKEND_URL` environment variable with your backend's Railway URL

### Issue 3: MongoDB Connection Failed
**Solution:** 
- If using Railway's MongoDB, use the provided connection string
- Format: `mongodb://mongo:password@host:port/database`
- Update the `MONGO_URL` environment variable in backend

### Issue 4: Port Binding Error
**Solution:** Railway automatically provides `$PORT` environment variable. Make sure your app uses it:
- Backend: Already configured to use `$PORT`
- Frontend: Nginx listens on port 80 by default (configured in Dockerfile)

## What NOT to Do

❌ Don't deploy from the root directory - Railway won't know which service to build  
❌ Don't delete the Dockerfiles - they're required for the build process  
❌ Don't forget to set environment variables - your app won't work without them  
❌ Don't use `localhost` URLs - use the actual Railway URLs for cross-service communication

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Nixpacks Documentation](https://nixpacks.com/)
- [Docker Compose on Railway](https://docs.railway.app/deploy/dockerfiles)

## Need Help?

If you still encounter issues:
1. Check Railway logs (click on your service → "Logs" tab)
2. Verify all environment variables are set correctly
3. Make sure your GitHub repository has the latest changes
4. Try redeploying by clicking "Redeploy" in Railway

---

**Status:** ✅ Issue Fixed - Ready to Deploy
**Last Updated:** February 17, 2026
