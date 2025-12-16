# Data Model: Embedding Pipeline Setup

## Entities

### Document
**Description**: Represents a web page or document extracted from a Docusaurus URL
- **url**: String (unique identifier, the source URL)
- **title**: String (page title extracted from HTML)
- **content**: String (clean text content extracted from the page)
- **created_at**: DateTime (timestamp when document was indexed)
- **updated_at**: DateTime (timestamp when document was last updated)

### Embedding
**Description**: Vector representation of a text chunk with associated metadata
- **id**: String (unique identifier for the embedding)
- **vector**: Array<Float> (the actual embedding vector from Cohere)
- **text_chunk**: String (the text that was embedded)
- **document_url**: String (foreign key reference to Document.url)
- **chunk_index**: Integer (position of chunk within the original document)
- **metadata**: Object (additional metadata like source URL, title, etc.)

### Index
**Description**: Vector collection in Qdrant containing all embeddings
- **collection_name**: String (name of the Qdrant collection, e.g., "rag_embedding")
- **vector_size**: Integer (dimension of the embeddings, 1024 for Cohere multilingual model)
- **distance_function**: String (distance function used for similarity search, typically "Cosine")
- **documents_count**: Integer (number of documents indexed)

## Relationships

- **Document** 1-to-many **Embedding**: One document can generate multiple embeddings (chunks)
- **Embedding** belongs-to **Document**: Each embedding is associated with one source document

## Validation Rules

- Document.url must be a valid URL format
- Document.content must not exceed Cohere's token limit when chunked
- Embedding.vector must have exactly 1024 dimensions (for Cohere multilingual model)
- Embedding.text_chunk must not exceed 4000 characters to stay within Cohere's input limits
- Embedding.id must be unique within the collection

## State Transitions

- Document: [EXTRACTED] → [CHUNKED] → [EMBEDDED] → [INDEXED]
- Each state represents a stage in the processing pipeline