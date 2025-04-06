import asyncio
import httpx
import re
import time
import uuid
import argparse
from typing import List, Dict, Any, Type

from app.models.library import Library, IndexerType
from app.models.document import Document
from app.models.chunk import Chunk
from app.services.library_service import LibraryService
from app.services.document_service import DocumentService
from app.services.embedding_service import EmbeddingService

class WikipediaDemo:
    """
    A demonstration class that:
    1. Downloads articles about Andorra from Wikipedia
    2. Creates a library with documents and chunks
    3. Indexes the content with the specified indexer
    4. Performs sample searches
    """
    
    def __init__(self, indexer_type: IndexerType, leaf_size: int = 40, chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.library = None
        self.indexer_type = indexer_type
        self.leaf_size = leaf_size
        self.wikipedia_topics = [
            "Andorra",
            "Andorra la Vella"
        ]
    
    async def download_wikipedia_article(self, topic: str) -> Dict[str, Any]:
        """Download a Wikipedia article using the Wikipedia API"""
        url = "https://en.wikipedia.org/w/api.php"
        
        params = {
            "action": "query",
            "format": "json",
            "titles": topic,
            "prop": "extracts",
            "explaintext": True,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            
            # Extract article content
            pages = data.get("query", {}).get("pages", {})
            if not pages:
                return {"title": topic, "content": ""}
            
            # Get the first page (there should only be one)
            page_id = next(iter(pages))
            page = pages[page_id]
            
            return {
                "title": page.get("title", topic),
                "content": page.get("extract", ""),
                "page_id": page_id
            }
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of approximately chunk_size characters"""
        # Clean text: remove multiple spaces, newlines, etc.
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Simple chunking by character count
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            # Try to end chunks at sentence or paragraph boundaries if possible
            end = min(i + self.chunk_size, len(text))
            
            # Extend to end of sentence if possible
            sentence_end = text.find('. ', end - 30, end + 30)
            if sentence_end != -1:
                end = sentence_end + 1
            
            chunks.append(text[i:end].strip())
        
        return chunks
    
    async def create_library(self) -> Library:
        """Create a library for Andorra with documents and chunks from Wikipedia"""
        print("Creating Andorra library...")
        
        # Create library
        library = Library(
            name="Andorra",
            metadata={"source": "Wikipedia"}
        )
        self.library = LibraryService.create_library(library)
        print(f"Created library: {self.library.name} with ID: {self.library.id}")
        
        # Download articles and create documents
        for topic in self.wikipedia_topics:
            print(f"Processing article: {topic}")
            article = await self.download_wikipedia_article(topic)
            
            if not article["content"]:
                print(f"No content found for {topic}, skipping...")
                continue
                
            # Create document
            document = Document(
                library_id=self.library.id,
                name=article["title"],
                metadata={"source": "Wikipedia", "page_id": article.get("page_id", "unknown")}
            )
            
            # Create chunks
            text_chunks = self.chunk_text(article["content"])
            print(f"  Created {len(text_chunks)} chunks from article")
            
            # Add chunks to document (without embeddings)
            document.chunks = []
            for i, chunk_text in enumerate(text_chunks):
                print(f"  Adding chunk {i+1}/{len(text_chunks)}")
                
                # Create chunk with text only - embedding will be generated during indexing
                chunk = Chunk(
                    document_id=document.id,
                    text=chunk_text,
                    embedding=None,  # Explicitly set to None to make it clear no embedding is being created
                    metadata={"position": str(i), "article": article["title"]}
                )
                document.chunks.append(chunk)
            
            # Save document with chunks
            DocumentService.create_document(document)
            print(f"  Saved document with {len(document.chunks)} chunks")
        
        return self.library
    
    async def index_content(self) -> Dict[str, Any]:
        """Index the content using the LibraryService indexing API"""
        if not self.library:
            raise ValueError("Library not created yet. Call create_library() first.")
        
        print(f"Indexing library with ID: {self.library.id} using {self.indexer_type} indexer")
        print("This will generate embeddings for all chunks...")
        
        # Start the indexing process
        start_time = time.time()
        result = await LibraryService.start_indexing_library(
            library_id=self.library.id,
            indexer_type=self.indexer_type,
            leaf_size=self.leaf_size
        )
        
        print(f"Indexing started: {result}")
        
        # Wait for indexing to complete, polling status
        while True:
            status = LibraryService.get_indexing_status(self.library.id)
            if status["indexing_in_progress"]:
                print(f"Indexing in progress... Waiting 3 seconds")
                await asyncio.sleep(3)
                continue
                
            if status["indexed"]:
                print(f"Indexing completed successfully")
                break
                
            print(f"Indexing failed")
            break
            
        elapsed = time.time() - start_time
        print(f"Indexing completed in {elapsed:.2f} seconds")
        
        # Get final status
        status = LibraryService.get_indexing_status(self.library.id)
        
        return status
    
    async def perform_searches(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Perform a series of searches on the indexed content using LibraryService"""
        if not self.library:
            raise ValueError("Library not created yet. Call create_library() first.")
            
        results = []
        
        for query in queries:
            print(f"\nSearching for: '{query}'")
            start_time = time.time()
            
            try:
                # Use the library service to search
                search_results = await LibraryService.search_library(
                    library_id=self.library.id,
                    query_text=query,
                    top_k=3
                )
                
                elapsed = time.time() - start_time
                print(f"Search completed in {elapsed:.2f} seconds")
                print(f"Found {len(search_results)} results")
                
                for i, result in enumerate(search_results):
                    print(f"\nResult #{i+1} - Score: {result['score']:.4f}")
                    print(f"Document: {result['document']['name']}")
                    print(f"Text: {result['text'][:150]}...")
                
                results.append({
                    "query": query,
                    "results": search_results,
                    "search_time": elapsed
                })
                
            except ValueError as e:
                print(f"Search error: {str(e)}")
                results.append({
                    "query": query,
                    "error": str(e),
                    "results": []
                })
        
        return results

async def run_demo(indexer_name: str = "brute_force", chunk_size: int = 150, leaf_size: int = 40):
    """
    Run the Wikipedia demo with the specified indexer
    
    Args:
        indexer_name: Name of the indexer to use ('brute_force' or 'ball_tree')
        chunk_size: Size of text chunks to create
        leaf_size: Size of leaf nodes for Ball Tree indexer
    """
    # Convert indexer name to the format expected by the API
    if indexer_name.lower() == "brute_force":
        indexer_type = IndexerType.BRUTE_FORCE
        print(f"Using BRUTE_FORCE indexer")
    elif indexer_name.lower() == "ball_tree":
        indexer_type = IndexerType.BALL_TREE
        print(f"Using BALL_TREE indexer with leaf_size={leaf_size}")
    else:
        print(f"Unknown indexer: {indexer_name}. Using BRUTE_FORCE indexer.")
        indexer_type = IndexerType.BRUTE_FORCE
    
    demo = WikipediaDemo(indexer_type=indexer_type, leaf_size=leaf_size, chunk_size=chunk_size)
    
    try:
        # Create and index content
        await demo.create_library()
        await demo.index_content()
        
        # Perform sample searches
        sample_queries = [
            "What is the capital of Andorra?",
            "What languages are spoken in Andorra?",
            "What is the economy of Andorra based on?",
            "What is the history of Andorra?",
            "What are popular tourist activities in Andorra?"
        ]
        
        search_results = await demo.perform_searches(sample_queries)
        print("\nDemo completed successfully!")
        
    except Exception as e:
        print(f"Error during demo: {str(e)}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Wikipedia indexer demo")
    parser.add_argument("--indexer", type=str, default="brute_force", 
                        help="Indexer to use ('brute_force' or 'ball_tree')")
    parser.add_argument("--chunk-size", type=int, default=150,
                        help="Size of text chunks to create")
    parser.add_argument("--leaf-size", type=int, default=40,
                        help="Size of leaf nodes for Ball Tree indexer")
    
    args = parser.parse_args()
    
    # Run the demo with the specified indexer
    asyncio.run(run_demo(
        indexer_name=args.indexer, 
        chunk_size=args.chunk_size,
        leaf_size=args.leaf_size
    )) 