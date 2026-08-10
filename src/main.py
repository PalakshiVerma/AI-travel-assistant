"""
FastAPI backend web server for the AI Travel Assistant application.
Initializes the Qdrant database on startup and exposes API endpoints for document ingestion and Q&A.
Handles requests for PDF travel guide upload (/upload) and natural language questions (/ask).
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.ingest import ingest_pdf
from src.generator import generate_answer
from src.vectorstores import init_qdrant

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
logger = logging.getLogger("uvicorn.error")

# why are we calling VDB here :this runs just before the server is actually avabile or ready to take the request  
@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize qdrant database
    logger.info("Initializing Qdrant database...")
    init_qdrant()
    logger.info("Database initialization complete.")
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "Internal server error. Please try again later."}
    )


@app.get("/")
async def root():
    return {"message": "AI Travel Assistant API is running"}


# we want query of string type
class QueryRequest(BaseModel):
    query: str


# endpoint ask, when ask button is clicked execute this function 
# takes up a parameter and then return the logic 
@app.post("/ask")
async def ask_question(req: QueryRequest):
    stripped_query = req.query.strip()
    if not stripped_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    try:
        res = generate_answer(stripped_query)
        return {"response": res}
    except Exception:
        logger.exception("Error generating answer")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to generate an answer right now"
        )


@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = None):
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file uploaded"
        )
        
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload a PDF file"
        )
    
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 10MB limit"
        )
    
    await file.seek(0)
    
    try:
        result = await ingest_pdf(file)  # calling our async ingest_pdf function from ingest.py
        return {**result, "message": "File processed successfully"}
    except Exception:
        logger.exception("Error processing file")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing file"
        )


