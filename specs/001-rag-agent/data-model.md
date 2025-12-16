# Data Model: RAG Agent with FastAPI and Retrieval Integration

## Entities

### QueryRequest
- **Fields**:
  - query (string): The natural language question from the user
  - metadata (object, optional): Additional context or parameters for the query
- **Validation**:
  - query must not be empty
  - query length should be reasonable (e.g., < 1000 characters)
- **Relationships**: None

### QueryVector
- **Fields**:
  - vector (array of floats): Numerical representation of the query
  - query_text (string): Original query text for reference
- **Validation**:
  - vector must be properly formatted
  - vector dimensions must match knowledge base
- **Relationships**:
  - One-to-many with RetrievedChunks (used for similarity search)

### RetrievedChunks
- **Fields**:
  - content (string): Text content retrieved from knowledge base
  - source (string): Source identifier for the content
  - score (float): Similarity score to the query
  - metadata (object, optional): Additional information about the chunk
- **Validation**:
  - content must not be empty
  - score must be between 0 and 1
- **Relationships**:
  - Many-to-one with QueryVector (retrieved based on query vector)

### ResponseObject
- **Fields**:
  - answer (string): The generated answer to the user's query
  - sources (array of strings): List of sources used to generate the answer
  - matched_chunks (array of objects): The text chunks used to generate the answer
  - query_id (string, optional): Identifier for tracking the query
- **Validation**:
  - answer must not be empty when successful
  - sources and matched_chunks should be present when answer is provided
- **Relationships**: None

### ErrorObject
- **Fields**:
  - error_code (string): Code identifying the type of error
  - message (string): Human-readable error message
  - details (object, optional): Additional error details
- **Validation**:
  - error_code and message must be present for error responses
- **Relationships**: None

## State Transitions

### Query Processing Flow
1. QueryRequest received → validated
2. If valid → QueryVector generated
3. QueryVector → similarity search in knowledge base
4. RetrievedChunks → answer generation
5. Answer + sources + chunks → ResponseObject
6. ResponseObject → returned to client

### Error States
- Invalid QueryRequest → ErrorObject returned immediately
- Knowledge base unavailable → ErrorObject with appropriate code
- No relevant results found → ResponseObject with empty answer or appropriate message