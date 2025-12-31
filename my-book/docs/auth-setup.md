---
title: Authentication Setup
---

# Authentication System

This document describes the authentication system implemented for the Physical AI & Humanoid Robotics Textbook website.

## Overview

The authentication system allows users to sign up, sign in, and manage their profile information. The system consists of:

- Frontend: Docusaurus-based UI components for signup, signin, and profile management
- Backend: FastAPI endpoints for user authentication and profile management

## Architecture

### Backend (FastAPI)

Authentication endpoints are implemented in `backend/src/api/auth_endpoint.py`:

- `/auth/signup` - Create a new user account
- `/auth/signin` - Authenticate a user and return a session token
- `/auth/signout` - End a user's session
- `/profile` - Create/update user profile information
- `/profile/me` - Retrieve current user's profile

### Frontend (Docusaurus)

Authentication UI components are located in `my-book/src/`:

- Pages: `my-book/src/pages/auth/` - Signup, signin, onboarding pages
- Components: `my-book/src/components/auth/` - Reusable auth components
- Utilities: `my-book/src/utils/auth.js` - Authentication utility functions
- Context: `my-book/src/contexts/AuthContext.js` - Authentication state management

## Environment Configuration

The authentication system uses the following environment variables:

- `REACT_APP_API_URL` - Base URL for the backend API (defaults to `http://localhost:8000`)

## API Endpoints

### Authentication

- `POST /auth/signup` - Create a new user
  - Request body: `{ "email": string, "password": string, "name": string }`
  - Response: `{ "token": string, "userId": string, "email": string, "name": string }`

- `POST /auth/signin` - Authenticate a user
  - Request body: `{ "email": string, "password": string }`
  - Response: `{ "token": string, "userId": string, "email": string, "name": string }`

- `POST /auth/signout` - End user session

### Profile Management

- `POST /profile` - Create or update user profile
  - Request body: `{ "programmingLevel": string, "languages": string[], "tools": string[], "ram": string, "processor": string, "gpu": string, "learningGoal": string }`
  - Requires Authorization header with Bearer token

- `GET /profile/me` - Get current user's profile
  - Requires Authorization header with Bearer token

## Frontend Components

### Pages

- `/auth/signup` - New user registration
- `/auth/signin` - User authentication
- `/auth/signout` - User logout
- `/auth/onboarding` - Profile completion form
- `/dashboard` - User profile dashboard

### Navigation

The navbar automatically shows Sign In/Sign Up links when unauthenticated, and a user dropdown when authenticated.

## Implementation Details

### Security

- Passwords are hashed using SHA-256 before storage
- Session tokens are generated using secure random methods
- API requests require Bearer token authentication
- Session tokens are stored in localStorage (for production, consider using secure cookies)

### User Flow

1. New users visit `/auth/signup` to create an account
2. After signup, users are redirected to `/auth/onboarding` to complete their profile
3. Returning users visit `/auth/signin` to log in
4. If a returning user hasn't completed onboarding, they are redirected to `/auth/onboarding`
5. Once authenticated and profile is complete, users can access protected content
6. Users can update their profile at any time via the dashboard

## Development

To run the authentication system locally:

1. Start the backend: `cd backend && uvicorn main:app --reload`
2. Start the frontend: `cd my-book && npm run start`

The system will connect to the backend at `http://localhost:8000` by default.