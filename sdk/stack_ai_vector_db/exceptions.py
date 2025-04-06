class VectorDBError(Exception):
    """Base exception for all VectorDB errors"""
    pass

class APIError(VectorDBError):
    """Error when communicating with the API"""
    pass

class NotFoundError(VectorDBError):
    """Resource not found error"""
    pass

class ValidationError(VectorDBError):
    """Data validation error"""
    pass

class IndexingError(VectorDBError):
    """Error during indexing operations"""
    pass

class AuthenticationError(VectorDBError):
    """Authentication error"""
    pass 