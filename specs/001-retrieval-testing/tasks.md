---
description: "Task list for retrieval testing implementation"
---

# Tasks: Retrieval & Pipeline Testing for RAG Ingestion

**Input**: Design documents from `/specs/001-retrieval-testing/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend project**: `backend/` directory with test files
- **Dependencies**: `backend/requirements-test.txt` and existing `backend/.env`
- **Test files**: `backend/test_retrieval.py`, `backend/validation_utils.py`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Install test dependencies in backend/requirements-test.txt
- [x] T002 [P] Verify existing Qdrant collection `rag_embedding` is accessible
- [x] T003 [P] Verify Cohere API key configuration in existing .env file

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Setup Qdrant client configuration for retrieval testing in backend/test_config.py
- [x] T005 Setup Cohere client configuration for query embedding generation
- [x] T006 [P] Create validation utilities in backend/validation_utils.py for content comparison
- [x] T007 [P] Create utility functions for JSON output formatting
- [x] T008 Configure logging for test execution in backend/test_retrieval.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Verify Vector Retrieval Accuracy (Priority: P1) 🎯 MVP

**Goal**: Query Qdrant and receive correct top-k matches based on semantic similarity, with retrieved chunks matching original text content

**Independent Test**: Query Qdrant with a known input, receive top-k matches, and verify that returned chunks match original text content. This delivers confidence in the retrieval mechanism.

### Implementation for User Story 1

- [x] T009 [P] [US1] Implement connect_to_qdrant function to access existing `rag_embedding` collection
- [x] T010 [P] [US1] Implement generate_query_embedding function using Cohere for sample queries
- [x] T011 [US1] Implement query_qdrant_with_topk function for top-k search
- [x] T012 [US1] Implement validate_retrieved_chunks function to compare against original text
- [x] T013 [US1] Create basic_retrieval_test function to test top-k match accuracy
- [x] T014 [US1] Add error handling for Qdrant connection issues
- [x] T015 [US1] Test basic retrieval with sample queries against existing data

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Validate Metadata Retrieval (Priority: P2)

**Goal**: Ensure that metadata (URL, chunk_id) is returned correctly during retrieval to enable proper attribution and source tracking

**Independent Test**: Make a retrieval query and verify that returned metadata (URL and chunk_id) matches what was stored during ingestion. This delivers proper source attribution capability.

### Implementation for User Story 2

- [x] T016 [P] [US2] Enhance query_qdrant_with_topk to retrieve metadata fields (url, chunk_id)
- [x] T017 [US2] Implement verify_metadata_correctness function to validate metadata integrity
- [x] T018 [US2] Create metadata_validation_test function to check url and chunk_id accuracy
- [x] T019 [US2] Test metadata retrieval with various query types

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - End-to-End Query Testing (Priority: P3)

**Goal**: Perform complete end-to-end testing from input query to clean JSON output to validate the complete retrieval pipeline

**Independent Test**: Provide an input query, process through entire retrieval pipeline, and receive clean JSON output. This delivers a complete test of system functionality.

### Implementation for User Story 3

- [x] T020 [P] [US3] Implement end_to_end_retrieval_test function to orchestrate complete pipeline
- [x] T021 [US3] Create generate_clean_json_output function for consistent result format
- [x] T022 [US3] Add performance timing to measure test execution speed
- [x] T023 [US3] Test complete pipeline with various query inputs
- [x] T024 [US3] Validate JSON output format matches contract specification

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T025 [P] Add comprehensive logging throughout the testing framework
- [x] T026 Add configuration options for top-k values and timeout settings
- [x] T027 [P] Create README section with testing instructions
- [x] T028 Add input validation for query parameters
- [x] T029 Performance optimization for large-scale testing
- [x] T030 Run quickstart.md validation to ensure all steps work as documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all parallel tasks for User Story 1 together:
Task: "Implement connect_to_qdrant function to access existing `rag_embedding` collection"
Task: "Implement generate_query_embedding function using Cohere for sample queries"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify functionality after each task or logical group
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence