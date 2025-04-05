from fastapi import FastAPI
from app.routers import health
from app.routers.v1 import library, document, chunk

app = FastAPI(
    title="Stack AI Vector DB",
    description="A FastAPI service for managing vector databases",
    version="0.1.0"
)

app.include_router(health.router)
app.include_router(library.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(chunk.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 