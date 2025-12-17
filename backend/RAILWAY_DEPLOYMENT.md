# Railway Deployment Guide

## Prerequisites
- Railway account (https://railway.app)
- Your API keys ready:
  - GEMINI_API_KEY
  - COHERE_API_KEY
  - QDRANT_URL
  - QDRANT_API_KEY

## Deployment Steps

### 1. Create New Project on Railway
1. Go to https://railway.app and sign in
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Choose your repository

### 2. Configure the Service
- **Service Type**: Select "Web Service" (or "Backend" if prompted)
- **Repository**: Select your GitHub repository
- **Branch**: Select your main branch (usually `main` or `master`)
- **Build & Deploy**: Enable auto-deploy from GitHub

### 3. Set Environment Variables
In the Railway dashboard:
1. Go to your project
2. Click on "Variables" or "Environment Variables"
3. Add the following variables:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `COHERE_API_KEY` - Your Cohere API key
   - `QDRANT_URL` - Your Qdrant database URL
   - `QDRANT_API_KEY` - Your Qdrant API key
   - `FRONTEND_URL` - Set to `https://sadiaism.github.io`

### 4. Configure the Service
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path**: `/health`

### 5. Deploy
1. Click "Deploy" or wait for auto-deployment to complete
2. Once deployed, note the assigned Railway URL (e.g., `https://your-project-name-production.up.railway.app`)

### 6. Update Frontend Configuration
Update your frontend to point to your Railway URL:

In `my-book/.env`:
```
REACT_APP_BACKEND_URL=https://your-project-name-production.up.railway.app
```

Then rebuild and redeploy your GitHub Pages site.

## Alternative: Using Railway CLI

If you prefer using the Railway CLI:

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Link your project: `railway init`
4. Set variables: `railway vars set GEMINI_API_KEY=your_key`
5. Deploy: `railway up`

## Important Notes

- Railway automatically provides a `$PORT` environment variable
- The backend will use this port instead of the hardcoded 8000
- CORS is configured to allow your GitHub Pages URL
- First requests after inactivity may take longer as the service wakes up

## Testing Your Deployment

1. Once deployed, test the health endpoint: `https://your-project-name-production.up.railway.app/health`
2. Test the ask endpoint: `https://your-project-name-production.up.railway.app/ask` (with a POST request)
3. Verify the chatbot on your GitHub Pages site works correctly

## Troubleshooting

If deployment fails:
1. Check that all environment variables are set correctly
2. Verify your Dockerfile is in the backend directory
3. Confirm the start command matches the expected format
4. Check the deployment logs in Railway dashboard for errors

If the chatbot doesn't work after deployment:
1. Check browser console for CORS errors
2. Verify the REACT_APP_BACKEND_URL in your frontend is correct
3. Ensure the FRONTEND_URL environment variable in Railway matches your GitHub Pages URL