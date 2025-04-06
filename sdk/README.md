# Stack AI Vector DB Python SDK

A Python SDK for interacting with the Stack AI Vector Database API.

## Installation

### From the Current Directory

```bash
pip install -e .
```

### From PyPI (when available)

```bash
pip install stack-ai-vector-db
```

## Basic Usage

```python
from stack_ai_vector_db import VectorDBClient

# Initialize the client
client = VectorDBClient(base_url="http://localhost:8000")

# Create a library
library = client.create_library(
    name="My Library",
    metadata={"field": "AI", "category": "NLP"}
)

# Create a document with text chunks
document = client.create_document(
    library_id=library.id,
    name="Introduction to Vector Databases",
    metadata={"author": "John Doe"},
    chunks=[
        {
            "text": "Vector databases are specialized systems designed to manage vector embeddings.",
            "metadata": {"position": "1"}
        },
        {
            "text": "They excel at similarity search operations, essential for modern AI applications.",
            "metadata": {"position": "2"}
        }
    ]
)

# Index the library
client.index_library(
    library_id=library.id,
    indexer_type="BALL_TREE",
    leaf_size=40
)

# Search for similar content
results = client.search(
    library_id=library.id,
    query_text="How do vector databases work?",
    top_k=5
)

# Process the results
for result in results:
    print(f"Score: {result.score} - {result.text}")
    print(f"Document: {result.document.name}")
```

## Running the Example

To run the provided example:

1. Make sure the Vector DB API server is running (typically on http://localhost:8000)

2. Install the SDK locally from the `sdk` directory:
   ```bash
   cd sdk
   pip install -e .
   ```

3. Run the example script:
   ```bash
   python examples/basic_usage.py
   ```

The `basic_usage.py` example shows how to create a library, add documents with chunks, index the library and perform basic searches. The example includes automatic waiting for indexing to complete before performing searches.

## Important Note on Indexing

Indexing a library is an asynchronous process that must complete before you can search the library:

1. When you call `client.index_library()`, the indexing process starts but runs asynchronously
2. You need to check for completion using `client.get_indexing_status()`
3. A library is ready for searching only when both conditions are true:
   - `indexed: true`
   - `indexing_in_progress: false`
4. The `basic_usage.py` example demonstrates how to properly wait for indexing to complete

## Features

- Complete Pythonic interface for the Stack AI Vector DB API
- Support for managing libraries, documents, and chunks
- Similarity search functionality
- Robust error handling with custom exceptions
- Data validation with Pydantic
- Comprehensive documentation with examples

## SDK Structure

- `client.py`: Main client with all methods to interact with the API
- `models/`: Pydantic models reflecting the API data structure
- `exceptions.py`: Custom exceptions for more intuitive error handling

## API Reference

### Main Client

```python
VectorDBClient(base_url: str = "http://localhost:8000", api_key: Optional[str] = None)
```

### Library Methods

- `create_library(name: str, metadata: Optional[Dict] = None) -> Library`
- `get_libraries() -> List[Library]`
- `get_library(library_id: Union[str, UUID]) -> Library`
- `update_library(library_id: Union[str, UUID], data: Dict) -> Library`
- `delete_library(library_id: Union[str, UUID]) -> bool`
- `index_library(library_id: Union[str, UUID], indexer_type: Union[str, IndexerType] = "BRUTE_FORCE", leaf_size: int = 40) -> Dict`
- `get_indexing_status(library_id: Union[str, UUID]) -> Dict`
- `search(library_id: Union[str, UUID], query_text: str, top_k: int = 5) -> List[SearchResult]`

### Document Methods

- `create_document(library_id: Union[str, UUID], name: str, chunks: List[Dict] = None, metadata: Dict = None) -> Document`
- `get_documents() -> List[Document]`
- `get_document(document_id: Union[str, UUID]) -> Document`
- `get_documents_by_library(library_id: Union[str, UUID]) -> List[Document]`
- `update_document(document_id: Union[str, UUID], data: Dict) -> Document`
- `delete_document(document_id: Union[str, UUID]) -> bool`

### Chunk Methods

- `create_chunk(document_id: Union[str, UUID], text: str, metadata: Dict = None) -> Chunk`
- `create_chunks(chunks: List[Dict]) -> List[Chunk]`
- `get_chunks() -> List[Chunk]`
- `get_chunk(chunk_id: Union[str, UUID]) -> Chunk`
- `get_chunks_by_document(document_id: Union[str, UUID]) -> List[Chunk]`
- `update_chunk(chunk_id: Union[str, UUID], data: Dict) -> Chunk`
- `delete_chunk(chunk_id: Union[str, UUID]) -> bool`

## Error Handling

The SDK provides the following custom exceptions:

- `VectorDBError`: Base exception for all errors
- `APIError`: API communication error
- `NotFoundError`: Resource not found (404)
- `ValidationError`: Data validation error (400)
- `IndexingError`: Error during indexing operations

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information. 