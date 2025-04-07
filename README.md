# Stack AI Vector DB

A FastAPI service for efficient vector database operations with multiple indexing algorithms and persistent storage.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
  - [Docker Compose](#docker-compose)
  - [Kubernetes Deployment](#kubernetes-deployment)
- [Database Model](#database-model)
- [Indexing Algorithms](#indexing-algorithms)
- [Concurrency and Thread Safety](#concurrency-and-thread-safety)
- [CRUD Operations & Data Flow](#crud-operations--data-flow)
- [API Workflow](#api-workflow)
- [Persistence Implementation](#persistence-implementation)
- [Testing](#testing)
- [Wikipedia Data Importer](#wikipedia-data-importer)
- [API Reference](#api-reference)
- [Python SDK](#python-sdk)

## Overview

Stack AI Vector DB is a specialized service for managing vector databases that efficiently store, index, and search text embeddings. It provides a scalable solution for semantic similarity search, featuring multiple indexing algorithms and persistent disk storage.

## Features

- In-memory vector storage with JSON persistence
- Multiple vector indexing algorithms (BruteForce, BallTree)
- RESTful API with FastAPI
- Thread-safe operations for concurrent access
- Hierarchical document organization (libraries → documents → chunks)
- Automatic vector embedding generation (via Cohere API)
- Comprehensive test suite
- Docker and Docker Compose support
- Wikipedia data importer for demo purposes

## Installation

### Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stack-ai-vector-db.git
   cd stack-ai-vector-db
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   echo "COHERE_API_KEY=your_api_key_here" > .env
   ```

5. Run the application:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

6. Access the API documentation:
   - Interactive API docs: http://localhost:8000/docs
   - Alternative API docs: http://localhost:8000/redoc

7. Verify the service is running:
   ```bash
   curl http://localhost:8000/health
   # Expected response: {"status": "ok"}
   ```

### Docker Installation

1. Build the Docker image:
   ```bash
   docker build -t stack-ai-vector-db .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 -e COHERE_API_KEY=your_api_key_here stack-ai-vector-db
   ```

### Docker Compose

1. Create a `.env` file with your Cohere API key:
   ```bash
   echo "COHERE_API_KEY=your_api_key_here" > .env
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up
   ```

3. To use the test dataset:
   ```bash
   TESTING_DATA=true docker-compose up
   ```

### Kubernetes Deployment

For deploying to a Kubernetes cluster like Minikube, this project includes a Helm chart in the `helmchart/` directory.

1. **Build and push the Docker image**:
   ```bash
   docker build -t your-username/vector-db:latest .
   docker push your-username/vector-db:latest
   ```

2. **Update the image repository in values.yaml**:
   ```yaml
   image:
     repository: your-username/vector-db
     tag: latest
   ```

3. **Install the Helm chart**:
   ```bash
   # Create base64 encoded API key
   COHERE_API_KEY_B64=$(echo -n "your-actual-api-key" | base64)

   # Install the chart
   helm install vector-db ./helmchart/vector-db --set cohereApiKey=$COHERE_API_KEY_B64
   ```

4. **Access the service in Minikube**:
   ```bash
   minikube service vector-db --url
   ```

#### Health and Readiness Probes

The Kubernetes deployment includes health monitoring via probes that connect to the application's `/health` endpoint:

- **Liveness Probe**: Verifies the application is running and responsive. If this probe fails, Kubernetes automatically restarts the container.
  - Initial delay: 30 seconds after container starts
  - Check frequency: Every 10 seconds
  - Timeout: 5 seconds per check
  - Failure threshold: 3 consecutive failures trigger a restart

- **Readiness Probe**: Determines if the application is ready to receive traffic. Until this probe succeeds, the pod won't receive requests.
  - Initial delay: 5 seconds after container starts
  - Check frequency: Every 10 seconds
  - Timeout: 2 seconds per check
  - Success threshold: 1 successful check to mark as ready
  - Failure threshold: 3 failures to mark as not ready

These probes ensure high availability by:
- Automatically restarting unhealthy containers
- Routing traffic only to healthy instances
- Enabling smoother rolling updates during deployments

All probe settings can be customized in the Helm chart's `values.yaml` file.

## Database Model

The database is structured using a hierarchical model:

1. **Library**: The top-level container that holds documents and configuration
   - Properties: id, name, metadata, index_status
   - Relationships: one-to-many with Documents

2. **Document**: Contains metadata and a collection of text chunks
   - Properties: id, library_id, name, metadata
   - Relationships: belongs-to Library, one-to-many with Chunks

3. **Chunk**: The smallest unit of text with vector embeddings
   - Properties: id, document_id, text, embedding, metadata
   - Relationships: belongs-to Document

This hierarchical approach enables:
- Logical organization of related content
- Efficient retrieval by context
- Independent indexing for different content collections
- Flexible metadata at multiple levels

## Indexing Algorithms

The system implements two vector indexing algorithms:

### BruteForce Indexer
- Simple implementation that compares query vectors with all indexed vectors
- Time complexity: O(n) where n is the number of vectors
- Space complexity: O(n×d) where d is the embedding dimension
- Pros: Exact results, simple implementation
- Cons: Slow for large datasets
- Best for: Small libraries (<1000 vectors) or when precision is critical

### BallTree Indexer
- Tree-based structure that organizes vectors in nested hyperspheres
- Time complexity: O(log n) average case for queries
- Space complexity: O(n×d) plus tree overhead
- Pros: Faster queries on large datasets, scales better
- Cons: Slightly more complex, approximate results
- Best for: Larger libraries, speed-critical applications
- Configuration: Tunable via `leaf_size` parameter (default: 40)

#### Choosing the Right Indexer

- **Brute Force**: Best for small datasets (< 1000 vectors) or when exact results are critical
- **Ball Tree**: Better for larger datasets, higher-dimensional embeddings, or when search speed is important

The `leaf_size` parameter in Ball Tree allows tuning the trade-off between search speed and memory usage:
- Smaller leaf sizes (10-20) create deeper trees that can search faster but use more memory
- Larger leaf sizes (40-100) create shallower trees that use less memory but may search slightly slower

## Concurrency and Thread Safety

The application handles concurrent operations through:

1. **Fine-grained Locks**: Separate locks for libraries, documents, and chunks
   ```python
   self.library_lock = threading.RLock()
   self.document_lock = threading.RLock()
   self.chunk_lock = threading.RLock()
   ```

2. **Reentrant Locks**: Using `RLock` to allow the same thread to acquire a lock multiple times

3. **Atomic Operations**: Critical operations are wrapped in a single lock context:
   ```python
   with db.document_lock:
       # Atomic operations here
   ```

4. **Relationship Consistency**: Locks ensure map relationships remain consistent:
   ```python
   with db.document_lock:
       db.documents[document_id] = document_data
       db.document_library_map[document_id] = library_id
   ```

5. **Hierarchical Locking**: Careful lock ordering prevents deadlocks

## CRUD Operations & Data Flow

The service implements a layered architecture:

1. **Database Layer** (`app/database/`):
   - Direct data access with thread-safe operations
   - Maintains relationships between entities
   - Handles persistence to disk

2. **Service Layer** (`app/services/`):
   - Business logic implementation
   - Coordinates database operations
   - Manages side effects and dependencies

3. **API Layer** (`app/routers/`):
   - HTTP endpoint routing
   - Input validation
   - Response formatting

Data flow follows a clean, cascading pattern:
- Creating a document automatically creates its chunks
- Deleting a library automatically deletes its documents and their chunks
- Updating a document or chunk marks the library as not indexed
- Library operations like search automatically use the appropriate indexer

## API Workflow

The typical workflow for using the API:

1. **Create a Library**:
   ```bash
   curl -X POST "http://localhost:8000/api/libraries" \
     -H "Content-Type: application/json" \
     -d '{"name": "Research Papers", "metadata": {"field": "Computer Science"}}'
   ```

2. **Create Documents with Chunks**:
   ```bash
   curl -X POST "http://localhost:8000/api/documents" \
     -H "Content-Type: application/json" \
     -d '{
       "library_id": "your-library-id",
       "name": "Transformer Architecture",
       "metadata": {"author": "Smith et al."},
       "chunks": [
         {"text": "Transformers use self-attention...", "metadata": {"position": "0"}},
         {"text": "The encoder-decoder architecture...", "metadata": {"position": "1"}}
       ]
     }'
   ```

3. **Index the Library**:
   ```bash
   curl -X POST "http://localhost:8000/api/libraries/your-library-id/index" \
     -H "Content-Type: application/json" \
     -d '{"indexer_type": "BALL_TREE", "leaf_size": 40}'
   ```

4. **Search the Library**:
   ```bash
   curl -X POST "http://localhost:8000/api/libraries/your-library-id/search" \
     -H "Content-Type: application/json" \
     -d '{"query_text": "attention mechanism in transformers", "top_k": 5}'
   ```

This workflow separates content creation from indexing, allowing for batch operations and optimized embedding generation.

### Library Indexing Lifecycle

1. A new library starts with `indexed: false` and `indexing_in_progress: false`
2. When you start indexing, the library transitions to `indexed: false` and `indexing_in_progress: true`
3. After successful indexing, the library becomes `indexed: true` and `indexing_in_progress: false`
4. Any modifications to the library's documents or chunks automatically mark it as `indexed: false`
5. You can only perform searches on libraries that are fully indexed (`indexed: true`)
6. Attempting to search a library that is currently being indexed will return an error

## Persistence Implementation

The application uses JSON file-based persistence:

1. **Storage Structure**:
   - One JSON file per library (`library_{uuid}.json`)
   - Contains the library, its documents, and chunks in a single file
   - Embeddings are excluded from storage to save space

2. **Data Directory**:
   - Configured via `DATA_DIR` environment variable (default: "data")
   - Created automatically if it doesn't exist

3. **Load/Save Operations**:
   - `save_library()`: Saves a library to disk after modifications
   - `load_library()`: Loads a specific library from disk
   - `load_all_libraries()`: Loads all libraries during startup

4. **Test Data**:
   - Sample Andorra dataset provided for testing (`testing_data.json`)
   - Loaded automatically when `TESTING_DATA=true` environment variable is set
   - Contains a complete library with documents and chunks about Andorra

5. **Implementation**:
   ```python
   # Load all libraries on startup
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       # Load all libraries from disk
       libraries_loaded = load_all_libraries()
       
       # Load test data if testing mode is enabled
       if TESTING_DATA:
           test_file_path = os.environ.get("TESTING_DATA_FILE")
           if os.path.exists(test_file_path):
               load_library_from_file(test_file_path)
       
       yield
   ```

### Advantages and Disadvantages of JSON Persistence

#### Advantages
- **Simplicity**: Easy to implement and understand with no external dependencies
- **Human Readable**: JSON files can be inspected and edited manually if needed
- **Portability**: Files can be easily backed up, transferred, or shared
- **No Database Setup**: No need to install and configure a separate database system
- **Direct Mapping**: Straightforward serialization of the in-memory data structures
- **Library Isolation**: Each library's data is isolated in its own file, preventing cross-contamination

#### Disadvantages
- **Performance**: Not optimized for high-frequency writes or large datasets
- **Atomicity**: No built-in transaction support, could lead to data corruption during crashes
- **Scalability**: Limited ability to scale as dataset size increases (entire file must be read/written)
- **Query Capabilities**: No query language or filtering capabilities like SQL databases
- **Concurrency**: Limited support for concurrent access compared to dedicated databases
- **Memory Usage**: Requires loading entire libraries into memory

### Intended Use Case

This JSON persistence approach is best suited for:
- Development and testing environments
- Small to medium-sized datasets
- Applications with low to moderate write frequency
- Scenarios where simplicity is valued over high performance
- Use cases where data can fit comfortably in memory

For production use with very large datasets or high concurrency requirements, consider replacing the JSON persistence with a dedicated database system while maintaining the same API.

## Testing

The project includes a comprehensive test suite:

1. **Running All Tests**:
   ```bash
   python -m pytest
   ```

2. **Database Layer Tests**:
   ```bash
   python -m pytest tests/database/
   ```

3. **Service Layer Tests**:
   ```bash
   python -m pytest tests/services/
   ```

4. **API Layer Tests**:
   ```bash
   python -m pytest tests/routers/
   ```

5. **Indexer Tests**:
   ```bash
   python -m pytest tests/indexer/
   ```

6. **Embedding Service Tests**:
   ```bash
   # Mock tests (run by default)
   python -m pytest tests/services/test_embedding_service.py
   
   # Live tests (skipped by default)
   python -m pytest tests/services/test_embedding_service_live.py -v
   ```

7. **Verbose Testing**:
   ```bash
   python -m pytest -xvs
   ```

The test suite uses pytest fixtures for setup/teardown and mocks for external dependencies.

## Wikipedia Data Importer

The project includes a Wikipedia demo for importing real-world data:

1. **Functionality**:
   - Downloads Wikipedia articles via the Wikipedia API
   - Creates a library with documents and chunks
   - Indexes the content with specified algorithm
   - Performs sample searches

2. **Running the Demo**:
   ```bash
   # Basic usage with BruteForce indexer
   python -m app.demo.wikipedia_demo --indexer brute_force
   
   # Advanced usage with BallTree indexer
   python -m app.demo.wikipedia_demo --indexer ball_tree --chunk-size 150 --leaf-size 30
   ```

3. **Parameters**:
   - `--indexer`: Algorithm to use (`brute_force` or `ball_tree`)
   - `--chunk-size`: Size of text chunks (default: 150 characters)
   - `--leaf-size`: Size of leaf nodes for BallTree (default: 40)

4. **Requirements**:
   - Cohere API key in `.env` file
   - Internet connection for Wikipedia API access

The demo is an excellent way to test the system with realistic data and understand the indexing and search capabilities.

## API Reference

### Library Endpoints
- `POST /api/libraries` - Create a new library
- `GET /api/libraries` - Get all libraries
- `GET /api/libraries/{library_id}` - Get a specific library
- `PATCH /api/libraries/{library_id}` - Update a library
- `DELETE /api/libraries/{library_id}` - Delete a library
- `POST /api/libraries/{library_id}/index` - Start indexing a library
- `GET /api/libraries/{library_id}/index/status` - Get library indexing status
- `POST /api/libraries/{library_id}/search` - Search for content in an indexed library

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

### Using Test Data

The application includes a test dataset about Andorra that can be automatically loaded on startup. This is useful for testing and exploring the API without having to manually create data.

To enable the test data, set the `TESTING_DATA` environment variable to `true`:

```bash
# When running locally
TESTING_DATA=true python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# When using Docker Compose
TESTING_DATA=true docker-compose up
```

The test data includes:
- A library named "Andorra"
- 5 documents covering different aspects of Andorra (Overview, History, Tourism, Geography, and Culture)
- 23 text chunks with factual information about Andorra
- All relevant metadata and relationships

After loading, you can immediately use the API to search and explore this data, or use it as a starting point for testing indexing features.

## Using the Postman Collection

For quick testing and exploration of the API, you can use the included Postman collection:

1. Open Postman
2. Click on "Import" in the top left corner
3. Select the `postman_collection.json` file from this repository
4. The "Stack AI Vector DB API" collection will be imported into your workspace

### Collection Environment Variables

The collection uses the following variables that you should configure:

- `base_url`: Base URL of the API (default: http://localhost:8000)
- `library_id`: ID of a created library
- `document_id`: ID of a created document
- `chunk_id`: ID of a retrieved chunk

### Recommended Testing Workflow

For the most effective testing experience with the Postman collection:

1. Run "Create Library" request to create a new library
2. Save the returned library ID in the `library_id` variable
3. Create a document using "Create Document" request
4. Save the returned document ID in the `document_id` variable
5. Start indexing with "Start Indexing (BruteForce)" or "Start Indexing (BallTree)" request
6. Check the indexing status with "Get Indexing Status" request
7. Once indexed, test searches with the "Search Library" request

This workflow allows you to quickly test all core functionality of the API without writing any code.

## Python SDK

The project includes a Python SDK that makes it easy to interact with the Vector DB API programmatically. The SDK is located in the `/sdk` directory.

### SDK Features

- Complete Pythonic interface for all API endpoints
- Support for managing libraries, documents, and chunks
- Similarity search functionality
- Robust error handling with custom exceptions
- Data validation with Pydantic
- Comprehensive documentation with examples

### Installing the SDK

```bash
cd sdk
pip install -e .
```

### Basic SDK Usage

```python
from stack_ai_vector_db import VectorDBClient

# Initialize the client
client = VectorDBClient(base_url="http://localhost:8000")

# Create a library
library = client.create_library(
    name="Research Papers",
    metadata={"field": "AI"}
)

# Create a document with chunks
document = client.create_document(
    library_id=library.id,
    name="Introduction to Vector Databases",
    chunks=[
        {"text": "Vector databases are specialized systems designed to manage vector embeddings."}
    ]
)

# Index the library
client.index_library(library_id=library.id)

# Search for similar content
results = client.search(
    library_id=library.id,
    query_text="How do vector databases work?",
    top_k=5
)
```

### Running the Example

The SDK includes an example script that demonstrates how to use it:

1. First, ensure the Vector DB API server is running (typically on http://localhost:8000)

2. Then run the example script:
   ```bash
   cd sdk
   python examples/basic_usage.py
   ```

The example shows how to create a library, add documents with chunks, handle indexing properly, and perform searches. The script includes a mechanism to wait for indexing to complete before attempting to search.

For more detailed documentation, see the [SDK README](sdk/README.md).