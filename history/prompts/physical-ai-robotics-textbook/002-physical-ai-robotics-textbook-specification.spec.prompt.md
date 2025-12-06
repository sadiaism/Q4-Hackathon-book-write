---
id: 002
title: Physical AI Robotics Textbook Specification
stage: spec
date: 2025-12-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: physical-ai-robotics-textbook
branch: 002-physical-ai-robotics-textbook
user: claude
command: /sp.specify Project: Hackathon I — Textbook for Teaching Physical AI & Humanoid Robotics

Purpose:
Create the full technical specification for a multi-module textbook designed to teach students Physical AI, humanoid robotics, and embodied intelligence using ROS 2, Gazebo, Unity, NVIDIA Isaac, and Vision-Language-Action models.

Primary Objective:
Transform the high-level book layout (4 modules, 17 chapters + appendices) into a precise, actionable specification that the book-writing agent will follow.

Core Principles:
- Technical accuracy (robotics, tudent deliverable for that chapter.

3. **Pedagogical Structure**
   - Difficulty should increase gradually.
   - Include weekly breakdown alignment (Weeks 1–13).
   - Include checkpoints, quizzes, and milestone projects.
   - Provide sample student outcomes after each module.

4. **Technical Standards**
   - ROS 2 version: Humble or Iron on Ubuntu 22.04.
   - Gazebo version: Fortress or Garden.
   - Isaac Sim: Latest Omniverse build supporting USD workflows.
   - Unity: LTS release with ROS-TCP-Connector.
   - AI Models: Whisper, GPT, VSLAM, object detection models, Nav2.

AI, simulation, perception)
- Curriculum coherence across all modules
- Student-focused learning outcomes
- Hands-on, project-driven structure
- Alignment with Physical AI ecosystem: ROS 2, Gazebo, Unity, Isaac Sim, Jetson, VLA models
- Progressive complexity from fundamentals → applied robotics → AI-driven humanoid autonomy

Specification Requirements:

1. **Module-Level Specifications**
   - Define clear purpose of each module.
   - Summaries of skills students will acquire.
   - Required software/hardware for each module.
   - Expected outputs (projects, assignments, assessments).

2. **Chapter-Level Specifications**
   For each chapter (1–17):
   - Problem or concept the chapter teaches.
   - Learning objectives.
   - Key concepts and required robotics/AI knowledge.
   - Hands-on activities, exercises, and practical tasks.
   - Diagrams, simulations, or code examples required.
   - Any dependencies on earlier chapters.
   - Whether ROS 2, Gazebo, Isaac, Unity, or VLA models are used.
   - Expected s5. **Hardware Requirements Specification**
   - RTX workstation requirements.
   - Jetson Orin Nano/NX edge kit requirements.
   - Sensor stack: RealSense, IMU, LiDAR.
   - Optional robot hardware tiers: Unitree Go2, Hiwonder humanoids, Unitree G1.
   - Cloud alternative infrastructure (AWS g5/g6e instances).

6. **Capstone Specification (Module 4)**
   - Full system pipeline: Voice → LLM Plan → ROS 2 Actions → Navigation → Perception → Manipulation.
   - Simulation-first deployment on Isaac/Gazebo.
   - Optional real-world deployment via Jetson + robot.
   - Full architecture diagram requirement (text-based).

7. **Constraints**
   - No chapter may exceed the scope of a typical 1-week teaching block.
   - Use diagrams, examples, and code wherever clarity improves learning.
   - Maintain consistent terminology: robot brain, digital twin, embodied intelligence, autonomous humanoid.
   - Follow safety and ethical guidelines in robotics (collision risks, latency issues, secure deployment).

8. **Success Criteria**
   - The specification is complete, detailed, and unambiguous.
   - Every module and chapter includes precise learning outcomes.
   - The textbook becomes executable for an AI agent to generate content.
   - All software/hardware requirements are explicit and correct.
   - Capstone project is fully defined from input → output.

Output Format:
Produce the specification as a structured multi-section Markdown document, following this order:
1. Overview
2. Module Specs
3. Chapter Specs
4. Pedagogy & Weekly Breakdown
5. Technical Standards
6. Hardware Requirements
7. Capstone Specification
8. Success Criteria
9. Appendix Notes (if needed)
labels: ["specification", "robotics", "ai", "textbook"]
links:
  spec: specs/002-physical-ai-robotics-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/002-physical-ai-robotics-textbook/spec.md
 - specs/002-physical-ai-robotics-textbook/checklists/requirements.md
tests:
 - Specification quality checklist passed
---

## Prompt

Project: Hackathon I — Textbook for Teaching Physical AI & Humanoid Robotics

Purpose:
Create the full technical specification for a multi-module textbook designed to teach students Physical AI, humanoid robotics, and embodied intelligence using ROS 2, Gazebo, Unity, NVIDIA Isaac, and Vision-Language-Action models.

Primary Objective:
Transform the high-level book layout (4 modules, 17 chapters + appendices) into a precise, actionable specification that the book-writing agent will follow.

Core Principles:
- Technical accuracy (robotics, tudent deliverable for that chapter.

3. **Pedagogical Structure**
   - Difficulty should increase gradually.
   - Include weekly breakdown alignment (Weeks 1–13).
   - Include checkpoints, quizzes, and milestone projects.
   - Provide sample student outcomes after each module.

4. **Technical Standards**
   - ROS 2 version: Humble or Iron on Ubuntu 22.04.
   - Gazebo version: Fortress or Garden.
   - Isaac Sim: Latest Omniverse build supporting USD workflows.
   - Unity: LTS release with ROS-TCP-Connector.
   - AI Models: Whisper, GPT, VSLAM, object detection models, Nav2.

AI, simulation, perception)
- Curriculum coherence across all modules
- Student-focused learning outcomes
- Hands-on, project-driven structure
- Alignment with Physical AI ecosystem: ROS 2, Gazebo, Unity, Isaac Sim, Jetson, VLA models
- Progressive complexity from fundamentals → applied robotics → AI-driven humanoid autonomy

Specification Requirements:

1. **Module-Level Specifications**
   - Define clear purpose of each module.
   - Summaries of skills students will acquire.
   - Required software/hardware for each module.
   - Expected outputs (projects, assignments, assessments).

2. **Chapter-Level Specifications**
   For each chapter (1–17):
   - Problem or concept the chapter teaches.
   - Learning objectives.
   - Key concepts and required robotics/AI knowledge.
   - Hands-on activities, exercises, and practical tasks.
   - Diagrams, simulations, or code examples required.
   - Any dependencies on earlier chapters.
   - Whether ROS 2, Gazebo, Isaac, Unity, or VLA models are used.
   - Expected s5. **Hardware Requirements Specification**
   - RTX workstation requirements.
   - Jetson Orin Nano/NX edge kit requirements.
   - Sensor stack: RealSense, IMU, LiDAR.
   - Optional robot hardware tiers: Unitree Go2, Hiwonder humanoids, Unitree G1.
   - Cloud alternative infrastructure (AWS g5/g6e instances).

6. **Capstone Specification (Module 4)**
   - Full system pipeline: Voice → LLM Plan → ROS 2 Actions → Navigation → Perception → Manipulation.
   - Simulation-first deployment on Isaac/Gazebo.
   - Optional real-world deployment via Jetson + robot.
   - Full architecture diagram requirement (text-based).

7. **Constraints**
   - No chapter may exceed the scope of a typical 1-week teaching block.
   - Use diagrams, examples, and code wherever clarity improves learning.
   - Maintain consistent terminology: robot brain, digital twin, embodied intelligence, autonomous humanoid.
   - Follow safety and ethical guidelines in robotics (collision risks, latency issues, secure deployment).

8. **Success Criteria**
   - The specification is complete, detailed, and unambiguous.
   - Every module and chapter includes precise learning outcomes.
   - The textbook becomes executable for an AI agent to generate content.
   - All software/hardware requirements are explicit and correct.
   - Capstone project is fully defined from input → output.

Output Format:
Produce the specification as a structured multi-section Markdown document, following this order:
1. Overview
2. Module Specs
3. Chapter Specs
4. Pedagogy & Weekly Breakdown
5. Technical Standards
6. Hardware Requirements
7. Capstone Specification
8. Success Criteria
9. Appendix Notes (if needed)

## Response snapshot

Created new branch `002-physical-ai-robotics-textbook`.
Created feature directory `specs/002-physical-ai-robotics-textbook`.
Wrote the technical specification to `specs/002-physical-ai-robotics-textbook/spec.md`.
Created and passed the specification quality checklist at `specs/002-physical-ai-robotics-textbook/checklists/requirements.md`.

## Outcome

- ✅ Impact: Successfully generated a comprehensive technical specification for the Physical AI & Humanoid Robotics textbook.
- 🧪 Tests: Specification quality checklist passed all criteria.
- 📁 Files: specs/002-physical-ai-robotics-textbook/spec.md, specs/002-physical-ai-robotics-textbook/checklists/requirements.md
- 🔁 Next prompts: The next step is to run `/sp.clarify` to address any remaining ambiguities or `/sp.plan` to begin architectural planning.
- 🧠 Reflection: Successfully handled the `/sp.specify` command, including branch creation, spec generation, and validation. The Bash script failure was mitigated by using agent-native tools.

## Evaluation notes (flywheel)

- Failure modes observed: The `create-phr.sh` script was not found. The `create-new-feature.ps1` also failed due to complex multi-line string passing in Bash.
- Graders run and results (PASS/FAIL): Manual validation of spec against checklist: PASS.
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Investigate the `create-phr.sh` and `create-new-feature.ps1` script execution within the Bash tool for better robustness with complex string inputs.
