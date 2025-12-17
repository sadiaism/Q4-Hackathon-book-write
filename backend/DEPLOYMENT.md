# Deployment Instructions for Render.com

## Prerequisites
- A Render.com account (https://render.com)
- Your API keys ready:
  - GEMINI_API_KEY
  - COHERE_API_KEY
  - QDRANT_URL
  - QDRANT_API_KEY

## Deployment Steps

### 1. Prepare Your Repository
Make sure all the following files are in your repository:
- `backend/` directory with your FastAPI application
- `Dockerfile` (included in the backend directory)
- `render.yaml` (in the root directory)

### 2. Connect Your Repository to Render
1. Go to https://dashboard.render.com
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select the branch you want to deploy from (usually `main` or `master`)

### 3. Configure the Web Service
- **Environment**: `Docker`
- **Docker file path**: `./Dockerfile` (or `backend/Dockerfile` if Dockerfile is in backend directory)
- **Root directory**: `/backend` (since our Dockerfile is in the backend directory)

### 4. Set Environment Variables
In the Render dashboard, under your service settings, add these environment variables:

- `GEMINI_API_KEY` - Your Google Gemini API key
- `COHERE_API_KEY` - Your Cohere API key
- `QDRANT_URL` - Your Qdrant database URL
- `QDRANT_API_KEY` - Your Qdrant API key
- `FRONTEND_URL` - Set to `https://sadiaism.github.io` (your GitHub Pages URL)

### 5. Update Frontend Configuration
After deployment, update your frontend to point to your Render URL:

In `my-book/.env`:
```
REACT_APP_BACKEND_URL=https://your-service-name.onrender.com
```

Then rebuild and redeploy your GitHub Pages site.

## Important Notes

- The free tier on Render allows your service to sleep after 15 minutes of inactivity
- First requests after sleep may take longer as the service wakes up
- Update your GitHub Pages site after backend deployment to ensure the chatbot connects properly

## Testing Your Deployment

1. Once deployed, test the health endpoint: `https://your-service-name.onrender.com/health`
2. Test the ask endpoint: `https://your-service-name.onrender.com/ask` (with a POST request)
3. Verify the chatbot on your GitHub Pages site works correctly

## Troubleshooting

If the chatbot doesn't work:
1. Check that CORS is properly configured in your backend
2. Verify environment variables are correctly set in Render
3. Confirm the frontend is pointing to the correct backend URL
4. Check browser console for CORS errors