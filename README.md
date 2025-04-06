# Stack AI Vector DB

A FastAPI service for vector database operations.

## Project Structure

```
├── app/                  # Application code
│   ├── main.py           # FastAPI application entrypoint
│   ├── routers/          # API endpoint routers
│   │   ├── v1/           # API version 1 routers
│   │   │   ├── library.py   # Library endpoints
│   │   │   ├── document.py  # Document endpoints
│   │   │   └── chunk.py     # Chunk endpoints
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   │   ├── library_service.py    # Library operations
│   │   ├── document_service.py   # Document operations
│   │   ├── chunk_service.py      # Chunk operations
│   │   └── embedding_service.py  # Vector embedding generation
│   ├── database/         # Database connections and queries
│   └── indexer/          # Vector indexing functionality
│   └── demo/             # Demo applications and examples
├── tests/                # Unit tests
│   ├── database/         # Database layer tests
│   ├── services/         # Service layer tests
│   ├── routers/          # API router tests
│   └── indexer/          # Vector indexer tests
├── Dockerfile            # Container definition
├── helmchart/            # Kubernetes Helm chart
└── requirements.txt      # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Create a virtual environment:

```bash
python3 -m venv venv
```

2. Activate the virtual environment:

```bash
# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your Cohere API key to the `.env` file for embedding functionality

### Running the Application

Start the FastAPI application:

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Documentation

Once the application is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative API docs: http://localhost:8000/redoc

### Health Check

Test if the API is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

## Wikipedia Demo

The application includes a demo that showcases how to use the vector database and indexing functionality with real-world content from Wikipedia.

### What the Demo Does

The Wikipedia demo:

1. Downloads articles about Andorra from Wikipedia using the Wikipedia API
2. Creates a library and documents in the vector database
3. Splits the article content into small text chunks
4. Generates vector embeddings for each chunk using Cohere's API
5. Indexes all chunks using the BruteForce indexer
6. Performs sample searches to find relevant information

### Running the Demo

To run the Wikipedia demo:

```bash
python3 -m app.demo.wikipedia_demo --indexer brute_force --chunk-size 150
```

Parameters:
- `--indexer`: The vector indexer to use (currently only "brute_force" is supported)
- `--chunk-size`: The size of text chunks to create (default: 150 characters)

### Prerequisites for the Demo

To run the demo, you need:

1. A Cohere API key in your `.env` file (for generating embeddings)
2. Internet connection (to download Wikipedia articles)

### Sample Searches

The demo performs the following sample searches:
- "What is the capital of Andorra?"
- "What languages are spoken in Andorra?"
- "What is the economy of Andorra based on?"
- "What is the history of Andorra?"
- "What are popular tourist activities in Andorra?"

## API Endpoints

The API is versioned using the `X-API-Version` header. Current version is `1.0`.

### Library Endpoints
- `POST /api/libraries` - Create a new library
- `GET /api/libraries` - Get all libraries
- `GET /api/libraries/{library_id}` - Get a specific library
- `PATCH /api/libraries/{library_id}` - Update a library
- `DELETE /api/libraries/{library_id}` - Delete a library

### Document Endpoints
- `POST /api/documents` - Create a new document
- `GET /api/documents` - Get all documents
- `GET /api/documents/library/{library_id}` - Get documents by library
- `GET /api/documents/{document_id}` - Get a specific document
- `PATCH /api/documents/{document_id}` - Update a document
- `DELETE /api/documents/{document_id}` - Delete a document

### Chunk Endpoints
- `POST /api/chunks` - Create a new chunk
- `POST /api/chunks/batch` - Create multiple chunks
- `GET /api/chunks` - Get all chunks
- `GET /api/chunks/document/{document_id}` - Get chunks by document
- `GET /api/chunks/{chunk_id}` - Get a specific chunk
- `PATCH /api/chunks/{chunk_id}` - Update a chunk
- `DELETE /api/chunks/{chunk_id}` - Delete a chunk

## Services

### Embedding Service

The application includes a service to generate text embeddings using Cohere's API. To use this service:

1. Ensure you have a Cohere API key in your `.env` file
2. Use the `EmbeddingService` class in your code:

```python
from app.services.embedding_service import EmbeddingService

# Generate embedding for a single text
embedding = await EmbeddingService.generate_embedding(
    "Your text here",
    input_type="search_document"
)

# Generate embeddings for multiple texts
embeddings = await EmbeddingService.generate_embeddings(
    ["First text", "Second text"],
    input_type="search_document"
)
```

The service supports different embedding models and input types as provided by Cohere's API.

## Vector Indexers

The application includes vector indexers for efficient similarity search:

### BruteForce Indexer

The BruteForce indexer is a simple implementation that compares query vectors with all indexed vectors. It's suitable for small libraries or as a baseline for comparison.

Usage example:

```python
from app.indexer import BruteForceIndexer

# Initialize the indexer
indexer = BruteForceIndexer()

# Index a library
stats = await indexer.index_library(library_id)

# Search for similar content
results = await indexer.search(
    text="Your search query",
    library_id=library_id,
    top_k=5
)
```

## Docker

Build the Docker image:

```bash
docker build -t stack-ai-vector-db .
```

Run the container:

```bash
docker run -p 8000:8000 stack-ai-vector-db
```

## Testing

### Running Database Tests

The project includes comprehensive tests for the database layer. To run these tests:

1. Make sure you have activated your virtual environment:

```bash
source venv/bin/activate
```

2. Run all tests:

```bash
python -m pytest
```

3. Run specific test files:

```bash
# Test chunk database operations
python -m pytest tests/database/test_chunk_db.py

# Test document database operations
python -m pytest tests/database/test_document_db.py

# Test library database operations
python -m pytest tests/database/test_library_db.py
```

### Running Service Tests

The project includes tests for the service layer, which verify that services correctly use the database layer:

```bash
# Test chunk service operations
python -m pytest tests/services/test_chunk_service.py

# Test document service operations
python -m pytest tests/services/test_document_service.py

# Test library service operations
python -m pytest tests/services/test_library_service.py

# Test embedding service
python -m pytest tests/services/test_embedding_service.py
```

### Running Router Tests

The project includes tests for the API routers:

```bash
# Test all routers
python -m pytest tests/routers

# Test specific routers
python -m pytest tests/routers/v1/test_library.py
python -m pytest tests/routers/v1/test_document.py
python -m pytest tests/routers/v1/test_chunk.py
```

### Running Indexer Tests

The project includes tests for the vector indexers:

```bash
# Test all indexers
python -m pytest tests/indexer

# Test specific indexers
python -m pytest tests/indexer/test_brute_force_indexer.py
```

The BruteForce indexer tests verify:
- Correct indexer name and metadata
- Library indexing functionality
- Search functionality with results
- Handling of empty or non-existent libraries

### Embedding Live Tests

To test the Embedding service with actual Cohere API calls:

```bash
# Skip these tests by default
python -m pytest tests/services/test_embedding_service_live.py -v
```

These tests will be skipped if:
- `SKIP_LIVE_TESTS=true` is set in your environment
- No Cohere API key is found in the environment

### Verbose Test Output

Run tests with detailed output:

```bash
python -m pytest -xvs
```

Where:
- `-x`: Stop after first failure
- `-v`: Verbose output
- `-s`: Show print statements during test execution