# CORS-Based Backend Deployment Guide

## Overview
This guide explains how to deploy your backend with proper CORS configuration to work with your GitHub Pages frontend.

## CORS Configuration Confirmed
✅ CORS is properly configured in `main.py` to allow requests from:
- GitHub Pages: `https://sadiaism.github.io`
- Local development: `http://localhost:3000`
- Local backend testing: `http://localhost:8000`
- Additional origins can be specified via environment variables

## Backend Deployment Options

### Recommended: Render.com (Free Tier)
1. Create account at https://render.com
2. Create new Web Service
3. Connect your GitHub repository
4. Set Dockerfile path to `./Dockerfile` in `/backend` directory
5. Set environment variables:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `COHERE_API_KEY` - Your Cohere API key
   - `QDRANT_URL` - Your Qdrant database URL
   - `QDRANT_API_KEY` - Your Qdrant API key
   - `FRONTEND_URL` - `https://sadiaism.github.io`
6. Deploy

### Alternative: Railway (Free Tier)
1. Create account at https://railway.app
2. Create new project from GitHub
3. Select your repository and branch
4. Set environment variables (same as above)
5. Deploy

### Alternative: Google Cloud Run (Free Tier)
1. Create account at https://cloud.google.com/run
2. Use the Dockerfile in the backend directory
3. Set environment variables during deployment
4. Deploy the container

## Required Environment Variables
For any deployment platform, ensure these environment variables are set:
- `GEMINI_API_KEY` - Your Google Gemini API key
- `COHERE_API_KEY` - Your Cohere API key
- `QDRANT_URL` - Your Qdrant database URL
- `QDRANT_API_KEY` - Your Qdrant API key
- `FRONTEND_URL` - `https://sadiaism.github.io` (for CORS)

## Frontend Configuration
After deploying your backend, update your frontend:
1. In `my-book/.env`, set:
   ```
   REACT_APP_BACKEND_URL=https://your-deployed-backend-url.com
   ```
2. Rebuild and redeploy your GitHub Pages site

## Port Configuration
The backend is configured to use the PORT environment variable (for platforms like Railway/Render) or default to 8000 for local development.

## Testing
1. After deployment, test your backend health: `https://your-backend-url/health`
2. Test the ask endpoint: `https://your-backend-url/ask` (POST request)
3. Test from your GitHub Pages frontend - the chatbot should work without CORS errors

## Additional Notes
- The Dockerfile in the backend directory is configured for deployment
- Your backend will work both locally and after deployment
- The CORS configuration allows requests from your GitHub Pages domain
- No additional changes are needed beyond setting environment variables