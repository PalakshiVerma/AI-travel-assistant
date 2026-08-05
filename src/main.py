#backend

from src.vectorstores import init_qdrant
from fastapi import FastAPI, UploadFile
from contextlib import asynccontextmanager
from pydantic import BaseModel
from src.ingest import ingest_pdf


#why are we calling VDB here :this runs just before the server is actually avabile or ready to take the request  
@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize qdrant database
    print("Initializing Qdrant database...")
    init_qdrant()
    print("Database initialization complete.")
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
        await ingest_pdf(file) # calling our async ingest_pdf function from ingest.py
        return {"message":"File processed successfully"}
        # return data

    except Exception as e:
        return {"message": f"Error processing file: {str(e)}"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("src.main:app", host="127.0.0.1", port=8001, reload=True)

