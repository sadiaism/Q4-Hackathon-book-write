# Research: Embedding Pipeline Setup

## Decision: Backend Technology Stack
**Rationale**: Python was chosen as the primary language due to its strong ecosystem for web scraping, NLP, and vector databases. The stack includes:
- **Cohere API**: For high-quality text embeddings
- **Qdrant**: Vector database for efficient similarity search
- **BeautifulSoup**: For HTML parsing and text extraction
- **Requests**: For HTTP requests to fetch Docusaurus content

**Alternatives considered**:
- Using OpenAI embeddings instead of Cohere: Chosen Cohere for potentially better performance and cost
- Using Pinecone instead of Qdrant: Chosen Qdrant for open-source nature and self-hosting capability
- Using Selenium for scraping instead of requests+BeautifulSoup: Chosen requests+BS for efficiency and simplicity

## Decision: URL Crawling Strategy
**Rationale**: For the deployed Docusaurus site at https://sadiaism.github.io/Q4-Hackathon-book-write/, we'll implement a breadth-first crawling approach that:
- Starts with the provided URL
- Extracts all internal links from the site
- Processes each page to extract clean text content
- Handles navigation and structure appropriately

**Alternatives considered**:
- Sitemap-based crawling: May not capture all pages if sitemap is incomplete
- Headless browser approach: More resource-intensive than necessary

## Decision: Text Chunking Strategy
**Rationale**: Text will be chunked using a sliding window approach with overlap to preserve context across chunks. This ensures that semantic relationships aren't broken at chunk boundaries.

**Alternatives considered**:
- Fixed-size chunking without overlap: Could break semantic context
- Semantic-aware chunking: More complex but potentially better quality

## Decision: Embedding Generation Approach
**Rationale**: Using Cohere's embed-multilingual-v3.0 model for generating embeddings, which handles various languages and provides high-quality vector representations for semantic search.

**Alternatives considered**:
- OpenAI embeddings: Chosen Cohere for potentially better cost/performance
- Sentence Transformers: Local models require more infrastructure management

## Decision: Qdrant Collection Design
**Rationale**: Creating a collection named `rag_embedding` with appropriate vector dimensions matching Cohere's output (1024 dimensions for embed-multilingual-v3.0). Metadata will include source URL, chunk text, and any relevant page information.

**Alternatives considered**:
- Different vector dimensions: Must match embedding model output
- Different collection names: Following the requirement to use `rag_embedding`