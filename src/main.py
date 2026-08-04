#backend

from fastapi import FastAPI, UploadFile
from contextlib import asynccontextmanager
from pydantic import BaseModel
from src.ingest import ingest_pdf

@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialized resources here
    yield


app = FastAPI(lifespan=lifespan)

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
    return {"response": "your answer"}


@app.post("/upload")
async def upload_file(file: UploadFile = None):
    if not file:
        return {"message": "No file uploaded"}
        
    if not file.filename.endswith('.pdf'):
        return {"message": "Please upload a PDF file"}
    
    try:
        data=await ingest_pdf(file)#calling our ingest_pdf function from ingest.py
        # return {"message": data}
        return data

    except Exception as e:
        return {"message": f"Error processing file: {str(e)}"}
