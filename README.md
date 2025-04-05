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