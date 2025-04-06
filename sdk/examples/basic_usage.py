"""
Basic example demonstrating the use of the Stack AI Vector DB Python SDK.
This example shows how to create a library, add a document with chunks,
index the library, and perform a search.
"""

from stack_ai_vector_db import VectorDBClient
import time

# Initialize the client
client = VectorDBClient(base_url="http://localhost:8000")

# Create a new library
library = client.create_library(
    name="Research Papers",
    metadata={"field": "AI", "category": "NLP"}
)
print(f"Created library: {library.id} - {library.name}")

# Create a document with chunks
document = client.create_document(
    library_id=library.id,
    name="Introduction to Vector Databases",
    metadata={"author": "John Doe", "date": "2023-04-01"},
    chunks=[
        {
            "text": "Vector databases are specialized database systems designed for managing vector embeddings.",
            "metadata": {"position": "1"}
        },
        {
            "text": "They excel at similarity search operations, which are essential for modern AI applications.",
            "metadata": {"position": "2"}
        },
        {
            "text": "Unlike traditional databases, vector databases optimize for nearest neighbor search in high-dimensional spaces.",
            "metadata": {"position": "3"}
        }
    ]
)
print(f"Created document: {document.id} - {document.name}")

# Index the library
print("Starting library indexing...")
indexing = client.index_library(
    library_id=library.id,
    indexer_type="BALL_TREE",
    leaf_size=40
)
print(f"Indexing started with status: {indexing}")

# Wait for indexing to complete
print("\nWaiting for indexing to complete...")
indexed = False
max_retries = 30  # Maximum number of retries
retry_count = 0
retry_interval = 2  # Time in seconds between retries

while not indexed and retry_count < max_retries:
    status = client.get_indexing_status(library.id)
    is_indexed = status.get('indexed', False)
    in_progress = status.get('indexing_in_progress', True)
    
    print(f"Retry {retry_count+1}/{max_retries}: Indexed: {is_indexed}, In Progress: {in_progress}")
    
    if is_indexed and not in_progress:
        indexed = True
        print("✅ Indexing completed successfully!")
    else:
        retry_count += 1
        print(f"⏳ Indexing still in progress, waiting {retry_interval} seconds...")
        time.sleep(retry_interval)

if not indexed:
    print("❌ Indexing did not complete in the expected time. Try running the search manually later.")
    exit(1)

# Now that indexing is complete, search the library
print("\nPerforming search...")
results = client.search(
    library_id=library.id,
    query_text="How do vector databases work?",
    top_k=3
)

print("\nSearch results:")
if not results:
    print("No results found.")
else:
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result.score:.4f}")
        print(f"   Text: {result.text}")
        print(f"   Document: {result.document.name}")
        print()

print(f"""
Example completed successfully!
Library ID: {library.id}
Document ID: {document.id}

You can use these IDs to experiment with other API operations.
""") 