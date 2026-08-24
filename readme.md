AI Travel Assistant

An AI-powered travel assistant that uses Retrieval-Augmented Generation (RAG) to answer travel-related questions using information extracted from uploaded PDF travel guides.

The application combines FastAPI, Streamlit, SentenceTransformers, Qdrant, LangChain, and Large Language Models to build an end-to-end document-based question-answering system.

Running the Application

The application consists of two components:

FastAPI backend
Streamlit frontend

Both need to be running.

Start the FastAPI Backend

From the project root:

uvicorn src.main:app --reload

The API will be available at:

http://localhost:8000

FastAPI automatically provides interactive API documentation at:

http://localhost:8000/docs
Start the Streamlit Frontend

Open another terminal and activate the virtual environment.

Then run:

streamlit run src/app.py

The Streamlit interface will open in your browser.

Overview

The AI Travel Assistant allows users to upload travel guide PDFs and ask natural-language questions about their content.

Instead of relying only on an LLM's pre-trained knowledge, the application retrieves relevant information from the uploaded documents and provides it to the language model as context before generating an answer.

Core workflow
PDF Travel Guide
       |
       v
Text Extraction
       |
       v
Document Chunking
       |
       v
Sentence Embeddings
       |
       v
Qdrant Vector Database
       |
       v
Semantic Retrieval
       |
       v
Relevant Context
       |
       v
LLM
       |
       v
Generated Answer
Key Features
PDF Document Ingestion

Users can upload PDF travel guides through the Streamlit interface.

The backend:

Validates the uploaded file.
Checks the file size.
Extracts text using PyMuPDF.
Preserves page-level metadata.
Splits the extracted text into smaller overlapping chunks.
Generates vector embeddings.
Stores the vectors and metadata in Qdrant.
Semantic Search

The application uses the all-MiniLM-L6-v2 SentenceTransformer model to convert text into dense vector representations.

User questions are embedded using the same model and compared against stored document vectors using cosine similarity.

This allows the system to retrieve information based on semantic meaning rather than only exact keyword matches.

Retrieval-Augmented Generation

The application follows a RAG architecture.

For every user question:

The question is converted into an embedding.
Qdrant searches for semantically similar document chunks.
The most relevant chunks are retrieved.
The retrieved content is added to the LLM prompt.
The LLM generates an answer using the retrieved context.

This allows the assistant to answer questions based on the uploaded travel guides.

Multiple LLM Providers

The project supports multiple model providers through environment configuration.

Supported providers include:

Hugging Face
OpenAI

The provider can be selected through the .env file.

MODEL_PROVIDER=huggingface

or:

MODEL_PROVIDER=openai
FastAPI Backend

The backend provides REST APIs for:

PDF uploading
Document processing
Question answering

The API includes:

Request validation
File validation
File-size validation
HTTP status codes
Exception handling
Backend logging
JSON responses
Streamlit Frontend

The Streamlit application provides a simple interface for:

Uploading travel guides
Processing documents
Entering natural-language questions
Viewing generated responses
System Architecture
                         +----------------------+
                         |      Streamlit       |
                         |       Frontend       |
                         +----------+-----------+
                                    |
                               HTTP / REST
                                    |
                         +----------v-----------+
                         |       FastAPI        |
                         |        Backend       |
                         +----+-------------+---+
                              |             |
                         Upload           Ask
                              |             |
                     +--------v----+   +----v----------+
                     | PDF Parsing |   | Query         |
                     |  PyMuPDF    |   | Embedding     |
                     +------+------+   +-------+-------+
                            |                  |
                            v                  |
                     +-------------+           |
                     |  Chunking   |           |
                     | LangChain   |           |
                     +------+------+           |
                            |                  |
                            v                  v
                     +-------------+    +-------------+
                     | Embeddings  |    |   Qdrant    |
                     | MiniLM      |    | Vector DB   |
                     +------+------+    +------+------+ 
                            |                  |
                            +--------+---------+
                                     |
                                     v
                            Retrieved Context
                                     |
                                     v
                            +----------------+
                            |      LLM       |
                            | HuggingFace /  |
                            | OpenAI         |
                            +-------+--------+
                                    |
                                    v
                              Final Answer
How the RAG Pipeline Works
1. Document Upload

The user uploads a PDF travel guide.

User
 |
 v
Streamlit
 |
 v
POST /upload
 |
 v
FastAPI

The API validates:

File presence
File extension
File size

The current maximum file size is:

10 MB
2. Text Extraction

PyMuPDF extracts text from every page of the uploaded PDF.

Page information is preserved so that the original source can be identified later.

Example metadata:

{
  "text": "Travel guide content...",
  "page": 4,
  "source": "paris-guide.pdf"
}
3. Document Chunking

Large documents are divided into smaller chunks using LangChain's RecursiveCharacterTextSplitter.

Current configuration:

Chunk Size:     500 characters
Chunk Overlap:  100 characters

Chunk overlap helps preserve context between neighboring chunks.

4. Embedding Generation

Each chunk is converted into a numerical vector using:

sentence-transformers/all-MiniLM-L6-v2

The model generates:

384-dimensional embeddings

These embeddings allow the application to perform semantic similarity searches.

5. Vector Storage

The generated embeddings are stored in Qdrant.

The current vector configuration uses:

Vector Size: 384
Distance:    Cosine Similarity

Each vector is stored together with document metadata such as:

Extracted text
Page number
Source filename
6. Query Processing

When a user asks a question, for example:

What are the best places to visit in Paris?

the question is converted into an embedding using the same embedding model.

The resulting vector is sent to Qdrant for similarity search.

7. Context Retrieval

Qdrant returns the most relevant document chunks.

The retrieved chunks are combined to create the context provided to the language model.

User Question
      +
Retrieved Context
      |
      v
     LLM
      |
      v
Generated Answer
8. Answer Generation

The LLM generates the final response using the retrieved information.

The system is designed to prioritize information available in the retrieved travel guide context.

Tech Stack
Backend
Python
FastAPI
Uvicorn
Pydantic
AI and Machine Learning
Hugging Face Transformers
SentenceTransformers
PyTorch
LangChain
Retrieval and Vector Database
Qdrant
Dense Vector Embeddings
Cosine Similarity
Document Processing
PyMuPDF
LangChain RecursiveCharacterTextSplitter
Frontend
Streamlit
Configuration
Python-dotenv
Environment Variables
Project Structure
AI-travel-assistant/
|
├── src/
│   ├── app.py
│   ├── main.py
│   ├── config.py
│   ├── ingest.py
│   ├── embeddings.py
│   ├── retriever.py
│   ├── vectorstores.py
│   └── generator.py
|
├── .env.example
├── requirements.txt
├── HLD.md
├── LLD.md
├── PRD.md
├── LICENSE
└── README.md
Module Responsibilities
File	Responsibility
app.py	Streamlit frontend
main.py	FastAPI application and API routes
config.py	Environment and application configuration
ingest.py	PDF processing and document chunking
embeddings.py	SentenceTransformer embedding generation
retriever.py	Qdrant semantic retrieval
vectorstores.py	Qdrant client and collection management
generator.py	LLM-based answer generation
API Documentation
GET /

Checks whether the API is running.

Response
{
  "message": "AI Travel Assistant API is running"
}
POST /upload

Uploads and processes a PDF travel guide.

Request
multipart/form-data
file=<travel-guide.pdf>
Supported File Type
PDF
Maximum File Size
10 MB
Example Response
{
  "filename": "paris-guide.pdf",
  "total_pages": 20,
  "total_chunks": 85,
  "status": "success",
  "message": "File processed successfully"
}
POST /ask

Generates an answer based on retrieved travel-guide information.

Request
{
  "query": "What are the best places to visit in Paris?"
}
Response
{
  "response": "..."
}
Validation

An empty query is rejected with:

400 Bad Request
API Status Codes
Status Code	Meaning
200 OK	Request completed successfully
201 Created	PDF successfully processed
400 Bad Request	Invalid request or empty query
413 Content Too Large	Uploaded file exceeds size limit
502 Bad Gateway	LLM/answer-generation failure
500 Internal Server Error	Unexpected server-side error
Installation
Prerequisites

Make sure the following are installed:

Python 3.10+
pip
Qdrant instance
Git
1. Clone the Repository
git clone <your-repository-url>
cd AI-travel-assistant
2. Create a Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate
macOS / Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
Environment Configuration

Create a .env file in the project root.

Use .env.example as a starting point.

Example:

QDRANT_HOST=<your-qdrant-url>
QDRANT_API_KEY=<your-qdrant-api-key>

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

MODEL_PROVIDER=huggingface

OPENAI_API_KEY=

FASTAPI_URL=http://localhost:8000
Qdrant Configuration

The application requires a Qdrant instance for vector storage.

Configure:

QDRANT_HOST=<your-qdrant-url>
QDRANT_API_KEY=<your-qdrant-api-key>
Hugging Face Configuration

For the default Hugging Face setup:

MODEL_PROVIDER=huggingface

The application uses:

google/flan-t5-base
OpenAI Configuration

To use OpenAI:

MODEL_PROVIDER=openai
OPENAI_API_KEY=<your-api-key>
