# Stack AI Vector DB

A FastAPI service for vector database operations.

## Project Structure

```
├── app/                  # Application code
│   ├── main.py           # FastAPI application entrypoint
│   ├── routers/          # API endpoint routers
│   ├── models/           # Data models
│   ├── services/         # Business logic
│   ├── database/         # Database connections and queries
│   └── indexer/          # Vector indexing functionality
├── tests/                # Unit tests
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

The project also includes tests for the service layer, which verify that services correctly use the database layer:

```bash
# Test chunk service operations
python -m pytest tests/services/test_chunk_service.py

# Test document service operations
python -m pytest tests/services/test_document_service.py

# Test library service operations
python -m pytest tests/services/test_library_service.py
```

### Verbose Test Output

Run tests with detailed output:

```bash
python -m pytest -xvs
```

Where:
- `-x`: Stop after first failure
- `-v`: Verbose output
- `-s`: Show print statements during test execution

### Test Coverage

The tests cover:
- CRUD operations for Chunks, Documents, and Libraries
- Relationship integrity between entities
- Cascading delete operations
- Error handling for invalid operations
- Edge cases and validation
- Service-layer business logic and validations