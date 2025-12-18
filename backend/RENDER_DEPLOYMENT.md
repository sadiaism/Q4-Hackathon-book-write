# Render Deployment Guide

This guide provides instructions for deploying your FastAPI backend to Render.com.

## Prerequisites

- A Render account (sign up at https://render.com)
- Your API keys and configuration ready:
  - Google Gemini API key
  - Cohere API key
  - Qdrant database URL and API key

## Deployment Steps

### 1. Create a New Web Service on Render

1. Log in to your Render dashboard
2. Click "New +" and select "Web Service"
3. Connect your GitHub/GitLab repository containing this backend code

### 2. Configure the Web Service

#### Basic Configuration:
- **Environment**: `Docker`
- **Dockerfile path**: `./Dockerfile`
- **Root directory**: `/backend` (if your backend is in a subdirectory)

#### Environment Variables:
Add the following environment variables in the Render dashboard:

| Variable Name | Description | Required |
|---------------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |
| `COHERE_API_KEY` | Your Cohere API key | Yes |
| `QDRANT_URL` | Your Qdrant database URL | Yes |
| `QDRANT_API_KEY` | Your Qdrant API key | Yes |
| `FRONTEND_URL` | Your frontend URL (e.g., `https://yourusername.github.io`) | Yes |
| `ADDITIONAL_CORS_ORIGINS` | Comma-separated list of additional origins (optional) | No |

#### Health Check:
- **Health Check URL**: `/health`
- **Health Check Interval**: 30 seconds (default)
- **Grace Period**: 30 seconds (default)
- **Max Consecutive Failures**: 5 (default)

### 3. Start Command

The start command is automatically handled by the Dockerfile:
```
sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
```

Render will automatically set the `PORT` environment variable, so no custom start command is needed.

### 4. Advanced Configuration

#### Render YAML Spec (Alternative Method)
Instead of configuring through the dashboard, you can create a `render.yaml` file in your repository root:

```yaml
services:
  - type: web
    name: rag-agent-api
    env: docker
    region: oregon  # or frankfurt for EU
    plan: free      # or starter/professional
    healthCheckPath: /health
    envVars:
      - key: GEMINI_API_KEY
        sync: false  # Render will prompt for the value
      - key: COHERE_API_KEY
        sync: false
      - key: QDRANT_URL
        sync: false
      - key: QDRANT_API_KEY
        sync: false
      - key: FRONTEND_URL
        value: https://yourusername.github.io
```

## Important Notes

1. **Port Configuration**: The application automatically uses Render's `PORT` environment variable or falls back to 8000.

2. **CORS Configuration**: The application is already configured to handle CORS for your frontend domain.

3. **Environment Variables**: Never commit API keys to your repository. Always use Render's environment variable configuration.

4. **Health Check**: The `/health` endpoint returns `{"status": "healthy"}` when the service is running properly.

5. **Scaling**: For the free tier, note Render's limitations on sleep times for inactive services.

## Troubleshooting

### Common Issues:

1. **CORS Errors**: Verify that `FRONTEND_URL` is set correctly in environment variables.

2. **API Connection Failures**: Check that all required API keys and URLs are correctly configured.

3. **Application Fails to Start**: Check the Render logs for error messages related to missing environment variables.

4. **Health Check Failing**: Verify the application starts properly and the `/health` endpoint is accessible.

### Checking Logs:
View logs in the Render dashboard under your service > "Logs" tab.

## Post-Deployment

1. Once deployed, note your Render service URL (typically `https://your-service.onrender.com`)
2. Update your frontend's environment variables to point to the new backend URL
3. Test the health endpoint: `https://your-service.onrender.com/health`
4. Test your application functionality

## Updating the Service

After pushing changes to your connected repository, Render will automatically rebuild and deploy your service. You can also manually trigger a deploy from the Render dashboard.