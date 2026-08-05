#here we will have al logic thats need for reading the file 
from langchain_core.documents import Document
from fastapi import UploadFile
import fitz #pymuPDF #help read the pdf file 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import COLLECTION_NAME
from src.embeddings import get_embeddings

#work of ingest_file function to take whatever is coming to endpoint /upload and then read it and just chuck it 

async def ingest_pdf(file: UploadFile):
    print(f"processing PDF file : {file.filename}")
    content= await file.read()

    #load pdf directly from memory
    docs=[]
    pdf=fitz.open(stream=content,filetype="pdf")#trying to read content by using fitz
    page_count=len(pdf)
    print(f"PDF loaded successfully. Found {page_count} pages")
    try:
        for page_num in range(page_count):#going through each page 
            page = pdf[page_num]
            text=page.get_text()#getting info out of the content 
            docs.append(Document   
            (page_content=text, metadata={"page":page_num , "source": file.filename}))
            #putting data in into docs array.
    finally:
        pdf.close()
    
    #llm have limit on token , we are optimizing the info by using slpitting technique (RecursiveCharacterTextSplitter) and creating chunks and chunking of 500 characters
    print("splitting document into chunks...")
    #chunk_size is total number of characters we want to pass to the LLM at one go  and overlap is the number of words we want to keep in common between chunks to maintain the context 
    splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=100)
    chunks=splitter.split_documents(docs)
    print("Generating embeddings...")
    texts = [chunk.page_content for chunk in chunks]
    embeddings = get_embeddings(texts)

    return {
        "filename": file.filename,
        "total_pages": page_count,
        "total_chunks": len(chunks),
        "chunks": [{"page_content": chunk.page_content, "metadata": chunk.metadata} for chunk in chunks],
        "embeddings": embeddings,
        "status": "success"
    }

    # #get Qdrant client
    # client=get_qdrant_client()

    # #perpare payloads
    # payloads=[{"text":chunk.page_content, **chunk.metadata} for chunk in chunks]

    # #upload points
    # print(f"Uploading {len(chunks)} documents to collection '{COLLECTION_NAME}'...")
    # client.upload_collection(
    #     collection_name=COLLECTION_NAME,
    #     vectors=embeddings,
    #     payloads=payloads
    # )
    # print(f"Upload complete ! Added {len(chunks)} chunks from {page_count} pages")
