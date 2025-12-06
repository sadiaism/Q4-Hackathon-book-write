---
id: 1
title: Technical Plan for Physical AI & Humanoid Robotics Textbook
stage: plan
date: 2025-12-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-physical-ai-robotics-textbook
branch: 002-physical-ai-robotics-textbook
user: unknown
command: /sp.plan
labels: ["planning", "robotics", "physical-ai", "textbook"]
links:
  spec: D:\\hackathone1\\specs\\002-physical-ai-robotics-textbook\\spec.md
  ticket: null
  adr: null
  pr: null
files:
  - D:\\hackathone1\\specs\\002-physical-ai-robotics-textbook\\plan.md
tests:
N/A
---

## Prompt

Project: Hackathon I — Physical AI & Humanoid Robotics Textbook
Goal: Create the technical plan that transforms the high-level specification into a structured, executable roadmap for the book’s creation.

Purpose of the Plan:
Define the architecture, structure, research-concurrent approach, and quality safeguards needed to write a rigorous, accurate, and pedagogically aligned textbook on Physical AI & Humanoid Robotics.

Plan Requirements:

1. **Architecture Sketch**
   - High-level book architecture: 4 modules → 17 chapters → capstone.
   - Flow from foundational concepts → simulation → perception → VLA humanoid autonomy.
   - Integration pathway between ROS 2, Gazebo, Unity, NVIDIA Isaac, and LLM/VLA systems.
   - System architecture for capstone: Voice Input → Whisper → LLM Planner → ROS 2 Actions → Navigation (Nav2) → Perception (VSLAM/Object Detection) → Manipulation.

2. **Section Structure**
   - Define structure for every chapter:
     - Concept introduction
     - Theory section (Physical AI + robotics fundamentals)
     - Applied section (ROS/Gazebo/Isaac/Unity)
     - Hands-on lab
     - Code examples
     - Diagrams & simulation figures
     - Assessment or micro-project
   - Module introduction pages and module summary pages.
   - Placement of appendices: hardware guide, environment setup, glossary, troubleshooting.

3. **Research Approach**
   - Use **research-concurrent writing**:
     - Research during writing, not before.
     - Verify robotics/AI facts with up-to-date ROS/Gazebo/Isaac/Unity documentation.
     - Use APA citations per Constitution.
     - For technical descriptions (e.g., Nav2, URDF, VSLAM), consult primary sources.
     - Fact-check hardware descriptions: Jetson, RealSense, Unitree hardware.
   - Maintain chain-of-custody for facts (source tracking).

4. **Quality Validation**
   - Validation criteria derived from Constitution + Specification:
     - Technical accuracy of robotics concepts.
     - Simulations must be reproducible.
     - ROS 2 packages/code must compile and run.
     - Hands-on labs should produce measurable outcomes.
     - Diagrams must reflect actual system behavior.
   - Generate internal QA checklist for each chapter:
     - Accuracy check
     - Code execution check
     - Pedagogical clarity check
     - Reference check (APA style)
     - Dependency check (chapter-to-chapter flow)

5. **Decisions Needing Documentation**
   - **Simulation Platform Choice**:
     - Gazebo Fortress vs Garden
       - Tradeoff: Garden has new features, Fortress is stable.
   - **Isaac Sim Version**:
     - Latest Omniverse build vs LTS
       - Tradeoff: stability vs new features.
   - **Unity Use Cases**:
     - When to use Unity vs Gazebo for visualization.
   - **Hardware Tier Selection**:
     - Unitree Go2 vs Hiwonder vs Unitree G1
       - Tradeoff: realism vs cost.
   - **AI Model Selection**:
     - Whisper → voice input
     - GPT-based planner → action translation
     - Nav2 → navigation stack
     - Isaac ROS → VSLAM & perception
   - **Deployment Strategy**:
     - Simulation-only vs Jetson + physical robot.
   - **Cloud vs Local Simulation**:
     - AWS g5/g6e instances vs RTX workstation.

6. **Testing Strategy / Validation Checks**
   - **Acceptance Criteria** (derived from Specification):
     - Each chapter must produce a working simulation, code result, or conceptual output.
     - Module labs must be reproducible with the given hardware/software.
     - Capstone must run end-to-end in simulation (voice → action → navigation → detection → manipulation).
   - **Technical Testing**:
     - ROS 2 nodes build with colcon and execute correctly.
     - URDF loads without warnings.
     - Gazebo and Isaac scenes render without physics errors.
     - Unity scenes load and respond with ROS-TCP-Connector.
     - Jetson deployment tests: latency, CPU/GPU utilization.
   - **Educational Testing**:
     - Ensure learning outcomes are measurable.
     - Ensure each chapter builds logically to the next.
     - Validate complexity curve from beginner → advanced.
   - **Book-Level Testing**:
     - All modules structurally align.
     - No contradictory definitions across chapters.
     - All citations complete and APA-correct.

7. **Phase Organization**
   Follow the recommended Spec-Kit Plus structure:

   **Phase 1 — Research**
   - Collect ROS 2, Gazebo, Isaac, Unity official docs.
   - Identify hardware references and robotics fundamentals.

   **Phase 2 — Foundation**
   - Finalize book structure.
   - Document technical architecture (simulation stack, AI stack, hardware stack).

   **Phase 3 — Analysis**
   - Break down chapter flows.
   - Map dependencies and prerequisites.
   - Define assessment structure.

   **Phase 4 — Synthesis**
   - Assemble the full book plan.
   - Ensure chapter-to-chapter integration.
   - Prepare the roadmap for content generation.

Output Format:
Produce the full plan as a structured Markdown document with the following sections:
1. Architecture Sketch
2. Section Structure
3. Research Approach
4. Quality Validation
5. Decisions Needing Documentation
6. Testing Strategy
7. Phase Breakdown
8. Final Plan Summary

## Response snapshot

The technical plan for "Physical AI & Humanoid Robotics Textbook" has been created and saved to `D:\hackathone1\specs\002-physical-ai-robotics-textbook\plan.md`.

**Branch**: `002-physical-ai-robotics-textbook`
**Implementation Plan Path**: `D:\hackathone1\specs\002-physical-ai-robotics-textbook\plan.md`

## Outcome

- ✅ Impact: The technical plan for the textbook has been successfully generated and saved.
- 🧪 Tests: N/A
- 📁 Files: `plan.md` created/updated.
- 🔁 Next prompts: Suggesting ADR for architectural decisions.
- 🧠 Reflection: The `create-phr.sh` script was not found, requiring manual PHR generation. The plan content aligns with the user's requirements and the project constitution.

## Evaluation notes (flywheel)

- Failure modes observed: `create-phr.sh` not found.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Investigate why `create-phr.sh` was not found.
