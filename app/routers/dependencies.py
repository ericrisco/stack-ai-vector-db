from fastapi import Header, HTTPException
from typing import Optional

async def verify_api_version(api_version: Optional[str] = Header(None, alias="X-API-Version")):
    """
    Dependency function to verify the API version.
    If the version is not 1.0 and is not None, raise an HTTPException.
    """
    if api_version != "1.0" and api_version is not None:
        raise HTTPException(status_code=400, detail=f"API version {api_version} not supported. Current version: 1.0")
    return api_version 