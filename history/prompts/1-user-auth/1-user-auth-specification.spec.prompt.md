---
id: 1
title: user-auth-specification
stage: spec
date_iso: 2025-12-22
surface: agent
model: Claude Sonnet 4.5
feature: 1-user-auth
branch: 1-user-auth
user: user
command: /sp.specify
labels: ["authentication", "onboarding", "user-profile"]
spec: null
ticket: null
adr: null
pr: null
files_yaml:
  - "specs/1-user-auth/spec.md"
  - "specs/1-user-auth/checklists/requirements.md"
tests_yaml: []
---

# Prompt History Record: user-auth-specification

## Outcome
Successfully created user authentication and onboarding specification following the Spec-Driven Development approach. The specification includes user scenarios, functional requirements, success criteria, and key entities in a technology-agnostic format.

## Evaluation
The specification meets all requirements with clear user stories, testable acceptance scenarios, and measurable success criteria. Implementation details were removed to maintain focus on user value and business needs.

## Prompt Text
## Goal
Implement Signup/Signin using **Better-Auth** and collect user **software + hardware background** after signup.

## Success Criteria
- Working Signup + Signin with Better-Auth
- After signup → redirect to **/onboarding**
- Onboarding form collects:
  - Programming level
  - Known languages
  - Tools used
  - Laptop specs (RAM, CPU, GPU)
  - Learning goal
- Save background data in `user_profile` linked with `userId`
- Middleware:
  - Not logged in → `/signin`
  - No profile → `/onboarding`
- **Ensure my existing project and folder structure remain unchanged; only add this new functionality without breaking anything.**

## Requirements
- Next.js 14 (App Router)
- TypeScript
- Prisma + PostgreSQL
- Provide:
  - Better-Auth config
  - Prisma schema
  - Signup/Signin pages
  - Onboarding page
  - API routes
  - Folder structure additions only (no modifications that break existing code)

## Response Text
Created comprehensive feature specification for user authentication and onboarding. The specification includes:
- User scenarios with prioritized user stories
- Functional requirements (FR-001 to FR-010)
- Key entities (User and UserProfile)
- Success criteria with measurable outcomes (SC-001 to SC-005)
- Edge cases consideration
- Technology-agnostic approach focusing on user value