# Data Model: Retrieval & Pipeline Testing for RAG Ingestion

## Entities

### RetrievalQuery
**Description**: Represents an input query for testing retrieval functionality
- **query_text**: String (the text used to search for similar content)
- **top_k**: Integer (number of top matches to retrieve)
- **expected_results**: Array<Object> (optional, known correct results for validation)

### RetrievedChunk
**Description**: Text content returned from Qdrant that matches the query semantically
- **id**: String (Qdrant point ID)
- **text**: String (the actual text content retrieved)
- **score**: Float (similarity score from Qdrant)
- **url**: String (source URL from metadata)
- **chunk_id**: Integer (chunk index from metadata)
- **original_text**: String (original text for comparison during validation)

### ValidationResult
**Description**: Result of validation comparing retrieved content with original
- **query_id**: String (identifier for the test query)
- **is_accurate**: Boolean (whether retrieval was accurate)
- **content_matches**: Boolean (whether retrieved text matches original)
- **metadata_correct**: Boolean (whether metadata is correct)
- **accuracy_score**: Float (quantitative measure of retrieval accuracy)
- **error_message**: String (optional, if validation failed)

### TestExecution
**Description**: Represents a single test execution run
- **id**: String (unique test run identifier)
- **timestamp**: DateTime (when test was executed)
- **query**: RetrievalQuery (the query used)
- **results**: Array<RetrievedChunk> (chunks returned from Qdrant)
- **validation**: ValidationResult (validation result)
- **execution_time**: Float (time taken to execute the test in seconds)

## Relationships

- **TestExecution** 1-to-many **RetrievedChunk**: One test execution can return multiple chunks
- **TestExecution** has-one **ValidationResult**: Each test has one validation result
- **RetrievedChunk** belongs-to **TestExecution**: Each chunk is part of a test execution

## Validation Rules

- RetrievalQuery.query_text must not be empty
- RetrievalQuery.top_k must be between 1 and 100
- RetrievedChunk.score must be between 0 and 1 (similarity score)
- RetrievedChunk.url must be a valid URL format
- ValidationResult.accuracy_score must be between 0 and 1
- ValidationResult.is_accurate is true only if both content_matches and metadata_correct are true

## State Transitions

- TestExecution: [INITIATED] → [EXECUTED] → [VALIDATED] → [COMPLETED]
- ValidationResult: [PENDING] → [IN_PROGRESS] → [COMPLETED] → [ACCURATE/INACCURATE]