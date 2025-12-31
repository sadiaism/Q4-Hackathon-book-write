# Quickstart Guide: User Authentication and Onboarding

## Overview
This guide provides instructions for setting up and using the user authentication and onboarding system.

## Prerequisites
- Node.js 18+ installed
- PostgreSQL database
- Next.js 14 project with App Router
- Better-Auth configured

## Setup Steps

### 1. Environment Variables
Create/update your `.env` file with:
```
DATABASE_URL="postgresql://username:password@localhost:5432/your_database"
AUTH_SECRET="your-super-secret-jwt-token-with-at-least-32-characters-long"
```

### 2. Install Dependencies
```bash
npm install @better-auth/node @better-auth/node/adapter-prisma @prisma/client
npm install -D prisma
```

### 3. Update Prisma Schema
Add the UserProfile model to your `prisma/schema.prisma` file:
```
model UserProfile {
  id               String   @id @default(cuid())
  userId           String   @unique
  programmingLevel String?
  languages        String[]
  tools            String[]
  ram              String?
  processor        String?
  gpu              String?
  learningGoal     String?
  completed        Boolean  @default(false)
  createdAt        DateTime @default(now())
  updatedAt        DateTime @updatedAt
  user             User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("user_profile")
}
```

### 4. Run Prisma Migrations
```bash
npx prisma db push
```

### 5. Configure Better-Auth
Create `lib/auth/index.ts` with your Better-Auth configuration.

### 6. Create API Routes
Create the required API routes in `app/api/profile/route.ts`.

## Usage
1. Users visit `/signup` to create an account
2. After signup, they're redirected to `/onboarding`
3. Complete the onboarding form to save their profile
4. After onboarding, they can access the main application

## Development
- Run the development server: `npm run dev`
- The authentication system will protect routes as configured
- Profile data can be accessed via the `/api/profile/me` endpoint