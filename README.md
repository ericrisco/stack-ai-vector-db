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

## Library Indexing and Search

The application supports indexing libraries and performing semantic searches directly through the API. This feature maintains the indexing state of each library and ensures searches only work on properly indexed libraries.

### Indexing a Library

To index a library:

```bash
curl -X POST "http://localhost:8000/api/libraries/{library_id}/index" \
  -H "X-API-Version: 1.0" \
  -H "Content-Type: application/json" \
  -d '{"indexer_type": "BALL_TREE", "leaf_size": 40}'
```

Parameters:
- `indexer_type`: Either "BRUTE_FORCE" or "BALL_TREE"
- `leaf_size`: Size of leaf nodes for Ball Tree indexer (optional, default: 40)

### Checking Indexing Status

To check the indexing status of a library:

```bash
curl -X GET "http://localhost:8000/api/libraries/{library_id}/index/status" \
  -H "X-API-Version: 1.0"
```

### Searching in a Library

To search for content in an indexed library:

```bash
curl -X POST "http://localhost:8000/api/libraries/{library_id}/search" \
  -H "X-API-Version: 1.0" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "Your search query", "top_k": 5}'
```

Parameters:
- `query_text`: The text to search for
- `top_k`: Number of results to return (optional, default: 5)

### Library Indexing Lifecycle

1. A new library starts with `indexed: false` and `indexing_in_progress: false`
2. When you start indexing, the library transitions to `indexed: false` and `indexing_in_progress: true`
3. After successful indexing, the library becomes `indexed: true` and `indexing_in_progress: false`
4. Any modifications to the library's documents or chunks automatically mark it as `indexed: false`
5. You can only perform searches on libraries that are fully indexed (`indexed: true`)

## Wikipedia Demo

The application includes a demo that showcases how to use the vector database and indexing functionality with real-world content from Wikipedia.

### What the Demo Does

The Wikipedia demo:

1. Downloads articles about Andorra from Wikipedia using the Wikipedia API
2. Creates a library and documents in the vector database
3. Splits the article content into small text chunks
4. Indexes all chunks using the selected indexer, generating embeddings during indexing
5. Performs sample searches to find relevant information

### Running the Demo

To run the Wikipedia demo:

```bash
# Using Brute Force indexer
python3 -m app.demo.wikipedia_demo --indexer brute_force --chunk-size 150

# Using Ball Tree indexer with custom leaf size
python3 -m app.demo.wikipedia_demo --indexer ball_tree --chunk-size 150 --leaf-size 30
```

Parameters:
- `--indexer`: The vector indexer to use ("brute_force" or "ball_tree")
- `--chunk-size`: The size of text chunks to create (default: 150 characters)
- `--leaf-size`: The maximum size of leaf nodes in the Ball Tree (default: 40)

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

## Services

### Library Service

The LibraryService provides methods for managing libraries, including indexing and searching:

```python
from app.services.library_service import LibraryService
from uuid import UUID

# Create a library
library = LibraryService.create_library(library)

# Start indexing a library
result = await LibraryService.start_indexing_library(
    library_id=UUID("your-library-id"),
    indexer_type="BALL_TREE",
    leaf_size=40
)

# Check indexing status
status = LibraryService.get_indexing_status(UUID("your-library-id"))

# Search in an indexed library
results = await LibraryService.search_library(
    library_id=UUID("your-library-id"),
    query_text="Your search query",
    top_k=5
)
```

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

### Ball Tree Indexer

The Ball Tree indexer organizes vectors in a hierarchical tree structure of nested hyperspheres, allowing for more efficient nearest neighbor searches with O(log n) complexity in the average case. It's especially efficient for higher-dimensional spaces and larger datasets.

### Using Indexers via the Library Service

The recommended way to use indexers is through the LibraryService, which manages the indexing state:

```python
# Start indexing with BruteForce indexer
await LibraryService.start_indexing_library(
    library_id=UUID("your-library-id"),
    indexer_type="BRUTE_FORCE"
)

# Start indexing with BallTree indexer
await LibraryService.start_indexing_library(
    library_id=UUID("your-library-id"),
    indexer_type="BALL_TREE",
    leaf_size=40
)

# Search an indexed library
results = await LibraryService.search_library(
    library_id=UUID("your-library-id"),
    query_text="Your search query",
    top_k=5
)
```

#### Ball Tree Structure

The Ball Tree organizes points in a binary tree where:
- Each node represents a "ball" (hypersphere) containing a subset of the points
- The root node contains all points
- Each non-leaf node has two children that partition its points
- Leaf nodes contain at most `leaf_size` points
- The tree supports efficient nearest neighbor searches by pruning large portions of the search space

#### Performance Comparison

When comparing the Ball Tree indexer with the Brute Force indexer:

- **Indexing Time**: Similar for small datasets, Ball Tree may take slightly longer to build the tree structure
- **Search Time**: Ball Tree performs faster and more consistent searches, especially as the dataset grows
- **Memory Usage**: Ball Tree requires additional memory to store the tree structure
- **Scalability**: Ball Tree scales better with O(log n) average search complexity vs O(n) for Brute Force

For small datasets (hundreds of vectors), both indexers perform well, but as the data grows to thousands or millions of vectors, the Ball Tree indexer offers significant performance advantages.

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
python -m pytest tests/indexer/test_ball_tree_indexer.py
```

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

## Postman Collection

Para probar la API de Stack AI Vector DB, puedes importar la colección de Postman incluida en este repositorio:

1. Abre Postman
2. Haz clic en "Import" en la esquina superior izquierda
3. Selecciona el archivo `postman_collection.json` de este repositorio
4. La colección "Stack AI Vector DB API" estará disponible en tu espacio de trabajo

### Variables de entorno

La colección usa las siguientes variables que deberás configurar:

- `base_url`: URL base de la API (por defecto: http://localhost:8000)
- `library_id`: ID de una biblioteca creada
- `document_id`: ID de un documento creado
- `chunk_id`: ID de un chunk recuperado

### Flujo de prueba recomendado

1. Ejecuta "Create Library" para crear una biblioteca nueva
2. Guarda el ID devuelto en la variable `library_id`
3. Crea un documento usando "Create Document" 
4. Guarda el ID del documento en la variable `document_id`
5. Inicia la indexación con "Start Indexing (BruteForce)" o "Start Indexing (BallTree)"
6. Verifica el estado de la indexación con "Get Indexing Status"
7. Una vez indexado, prueba las búsquedas con "Search Library"