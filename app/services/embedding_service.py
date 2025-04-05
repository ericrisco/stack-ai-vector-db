import os
import httpx
from typing import List, Optional, Dict, Union, Literal
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmbeddingService:
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    COHERE_EMBED_URL = "https://api.cohere.ai/v1/embed"
    DEFAULT_MODEL = "embed-english-v3.0"
    
    @classmethod
    async def generate_embeddings(
        cls, 
        texts: Union[str, List[str]], 
        model: Optional[str] = None,
        truncate: Optional[str] = "END",
        input_type: Optional[str] = "search_document"
    ) -> List[List[float]]:
        """
        Generate embeddings for a single text or a list of texts using Cohere's API.
        
        Args:
            texts: A string or list of strings to generate embeddings for
            model: The embedding model to use (defaults to embed-english-v3.0)
            truncate: How to handle texts longer than the maximum token length ('NONE', 'START', 'END')
            input_type: Type of input text (search_document, search_query, classification, clustering)
            
        Returns:
            A list of embeddings (one embedding per input text)
            
        Raises:
            ValueError: If the API key is missing or the API returns an error
            httpx.HTTPError: If there's a network or HTTP-related error
        """
        if not cls.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY is not set in environment variables")
        
        # Ensure texts is always a list
        texts_list = [texts] if isinstance(texts, str) else texts
        
        # Prepare request data
        payload = {
            "texts": texts_list,
            "model": model or cls.DEFAULT_MODEL,
            "truncate": truncate,
            "input_type": input_type,
        }
        
        headers = {
            "Authorization": f"Bearer {cls.COHERE_API_KEY}",
            "Content-Type": "application/json",
        }
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                cls.COHERE_EMBED_URL,
                json=payload,
                headers=headers,
                timeout=60.0
            )
            
            # Handle response
            if response.status_code != 200:
                error_msg = f"Cohere API error: {response.status_code} - {response.text}"
                raise ValueError(error_msg)
            
            response_data = response.json()
            
            if "embeddings" not in response_data:
                raise ValueError(f"Unexpected API response: {response_data}")
                
            return response_data["embeddings"]
    
    @classmethod
    async def generate_embedding(
        cls, 
        text: str, 
        model: Optional[str] = None,
        truncate: Optional[str] = "END",
        input_type: Optional[str] = "search_document"
    ) -> List[float]:
        """
        Generate an embedding for a single text using Cohere's API.
        
        Args:
            text: The text to generate an embedding for
            model: The embedding model to use (defaults to embed-english-v3.0)
            truncate: How to handle texts longer than the maximum token length ('NONE', 'START', 'END')
            input_type: Type of input text (search_document, search_query, classification, clustering)
            
        Returns:
            A single embedding vector
            
        Raises:
            ValueError: If the API key is missing or the API returns an error
            httpx.HTTPError: If there's a network or HTTP-related error
        """
        embeddings = await cls.generate_embeddings([text], model, truncate, input_type)
        return embeddings[0] 