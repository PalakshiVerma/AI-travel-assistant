# ✈️ AI Travel Assistant

An AI-powered travel assistant that uses **Retrieval-Augmented Generation (RAG)** to answer travel-related questions using information extracted from uploaded PDF travel guides.

The application combines **FastAPI, Streamlit, SentenceTransformers, Qdrant, LangChain, and Large Language Models** to build an end-to-end document-based question-answering system.

---

## 🚀 Overview

The AI Travel Assistant allows users to:

* 📄 Upload travel guide PDFs
* 🔍 Extract and process text from documents
* ✂️ Split documents into smaller contextual chunks
* 🧠 Generate semantic embeddings using SentenceTransformers
* 🗄️ Store embeddings in the Qdrant vector database
* 🔎 Perform semantic similarity search
* 🤖 Generate answers using an LLM
* 🌐 Access the system through a FastAPI backend
* 💬 Interact with the application through a Streamlit frontend

Instead of relying only on the model's pre-trained knowledge, the system retrieves relevant information from the uploaded travel guide and uses it as context for answer generation.

---

## 🧠 How It Works

The application follows a Retrieval-Augmented Generation pipeline:

```text
                    ┌─────────────────────┐
                    │     Streamlit UI    │
                    │      Frontend       │
                    └──────────┬──────────┘
                               │
                         HTTP REST API
                               │
                    ┌──────────▼──────────┐
                    │      FastAPI        │
                    │       Backend       │
                    └──────┬───────┬──────┘
                           │       │
                     Upload│       │Question
                           │       │
                ┌──────────▼─┐   ┌─▼────────────┐
                │ PDF Parser │   │ Query        │
                │  PyMuPDF   │   │ Embedding    │
                └──────┬─────┘   └──────┬───────┘
                       │                │
                       ▼                ▼
                ┌────────────┐    ┌──────────────┐
                │  Chunking  │    │    Qdrant    │
                │  500 chars │    │ Vector Search│
                └──────┬─────┘    └──────┬───────┘
                       │                 │
                       ▼                 ▼
                ┌────────────┐    ┌──────────────┐
                │ Embeddings │    │   Relevant   │
                │ MiniLM     │    │   Context    │
                └──────┬─────┘    └──────┬───────┘
                       │                 │
                       ▼                 ▼
                ┌─────────────────────────────┐
                │        LLM Generation       │
                │  HuggingFace / OpenAI       │
                └──────────────┬──────────────┘
                               │
                               ▼
                       Generated Answer
```

### RAG Pipeline

```text
PDF
 ↓
Text Extraction
 ↓
Document Chunking
 ↓
Sentence Embeddings
 ↓
Qdrant Vector Database
 ↓
Semantic Retrieval
 ↓
Relevant Context
 ↓
LLM
 ↓
Travel Answer / Itinerary
```

---

## ✨ Key Features

### 📄 PDF Travel Guide Ingestion

Users can upload PDF travel guides through the Streamlit interface.

The backend:

1. Validates the uploaded file
2. Enforces a 10 MB file-size limit
3. Extracts text using PyMuPDF
4. Preserves page-level metadata
5. Splits the extracted text into overlapping chunks
6. Generates embeddings
7. Stores vectors and metadata in Qdrant

---

### 🧠 Semantic Search

The system uses the `all-MiniLM-L6-v2` SentenceTransformer model to convert text into dense vector representations.

User questions are embedded using the same model and compared against stored document vectors using **cosine similarity**.

This allows the system to retrieve information based on **meaning**, rather than only matching exact keywords.

---

### 🔎 Retrieval-Augmented Generation

Retrieved travel-guide content is passed to the configured language model as contextual information.

The model is instructed to use the retrieved context when answering questions and avoid inventing information that is not available in the provided context.

---

### 🤖 Multiple LLM Providers

The project supports two model providers:

* **Hugging Face**

  * `google/flan-t5-base`
* **OpenAI**

  * `gpt-3.5-turbo`

The provider can be selected through environment configuration.

```env
MODEL_PROVIDER=huggingface
```

or

```env
MODEL_PROVIDER=openai
```

---

### ⚡ FastAPI Backend

The backend exposes REST endpoints for:

| Method | Endpoint  | Purpose                       |
| ------ | --------- | ----------------------------- |
| `GET`  | `/`       | API health/message            |
| `POST` | `/upload` | Upload and process a PDF      |
| `POST` | `/ask`    | Ask a travel-related question |

The API includes:

* Request validation
* HTTP status codes
* File validation
* File-size validation
* Exception handling
* Logging
* Structured JSON responses

---

### 💻 Streamlit Frontend

The Streamlit application provides a simple interface for:

* Uploading travel guides
* Processing documents
* Entering natural-language questions
* Viewing generated travel recommendations

---

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

### AI / Machine Learning

* Hugging Face Transformers
* SentenceTransformers
* LangChain
* PyTorch

### RAG / Vector Search

* Qdrant
* Cosine similarity
* Dense vector embeddings

### Document Processing

* PyMuPDF
* LangChain RecursiveCharacterTextSplitter

### Frontend

* Streamlit

### Configuration

* Python-dotenv
* Environment variables

---

## 📁 Project Structure

```text
AI-travel-assistant/
│
├── src/
│   ├── app.py              # Streamlit frontend
│   ├── main.py             # FastAPI application and API routes
│   ├── config.py           # Environment and application configuration
│   ├── ingest.py           # PDF ingestion and document chunking
│   ├── embeddings.py       # SentenceTransformer embeddings
│   ├── retriever.py        # Qdrant semantic retrieval
│   ├── vectorstores.py     # Qdrant client and collection management
│   └── generator.py        # LLM-based answer generation
│
├── .env.example            # Environment variable template
├── requirements.txt        # Python dependencies
├── HLD.md                  # High-Level Design
├── LLD.md                  # Low-Level Design
├── PRD.md                  # Product Requirements Document
├── LICENSE
└── README.md
```

---


## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd AI-travel-assistant
```

### 2. Create a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Configuration

Create a `.env` file in the project root.

You can use `.env.example` as a template.

```env
QDRANT_HOST=
QDRANT_API_KEY=

EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

MODEL_PROVIDER=huggingface

OPENAI_API_KEY=

FASTAPI_URL=http://localhost:8000
```

### Qdrant

The application requires a Qdrant instance for vector storage.

Configure:

```env
QDRANT_HOST=<your-qdrant-url>
QDRANT_API_KEY=<your-qdrant-api-key>
```

### Hugging Face

For the default Hugging Face configuration:

```env
MODEL_PROVIDER=huggingface
```

The application uses:

```text
google/flan-t5-base
```

### OpenAI

To use OpenAI:

```env
MODEL_PROVIDER=openai
OPENAI_API_KEY=<your-api-key>
```

---

## ▶️ Running the Application

The project consists of two components:

### Start FastAPI

From the project root:

```bash
uvicorn src.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

---

### Start Streamlit

In a second terminal:

```bash
streamlit run src/app.py
```

The Streamlit application will open in your browser.



## 🛡️ Error Handling

The backend implements validation and error handling for common failure cases.

| Scenario                   |                 HTTP Status |
| -------------------------- | --------------------------: |
| Successful request         |                    `200 OK` |
| PDF successfully processed |               `201 Created` |
| Empty query                |           `400 Bad Request` |
| Missing file               |           `400 Bad Request` |
| Invalid file type          |           `400 Bad Request` |
| File larger than 10 MB     |     `413 Content Too Large` |
| Answer-generation failure  |           `502 Bad Gateway` |
| Unexpected server error    | `500 Internal Server Error` |

Detailed exceptions are logged on the backend while user-facing responses remain generic.

---

## 🧩 Design Principles

The project follows a modular architecture where each major responsibility is separated into its own module.

```text
Configuration
      ↓
Document Ingestion
      ↓
Embedding Generation
      ↓
Vector Storage
      ↓
Retrieval
      ↓
LLM Generation
      ↓
API
      ↓
Frontend
```

This makes individual components easier to modify, test, and extend.

---

## 📊 Current RAG Configuration

| Component            | Configuration                    |
| -------------------- | -------------------------------- |
| Embedding Model      | `all-MiniLM-L6-v2`               |
| Embedding Dimensions | `384`                            |
| Vector Database      | Qdrant                           |
| Similarity Metric    | Cosine                           |
| Chunk Size           | `500` characters                 |
| Chunk Overlap        | `100` characters                 |
| Default Retrieval    | Top `2` chunks during generation |
| PDF Limit            | `10 MB`                          |
| Default LLM          | `google/flan-t5-base`            |
| Alternative LLM      | `gpt-3.5-turbo`                  |

---

## 🔮 Future Improvements

The current implementation provides the core RAG pipeline. Planned improvements include:

* [ ] Document-level filtering and isolation
* [ ] Similarity-score thresholds for retrieval
* [ ] Source and page-level citations in answers
* [ ] Document listing and deletion
* [ ] Duplicate-document detection
* [ ] Conversational chat history
* [ ] Improved Streamlit chat interface
* [ ] Automated unit and integration tests
* [ ] RAG evaluation dataset and retrieval metrics
* [ ] Background document-processing jobs
* [ ] `/health` endpoint for service monitoring
* [ ] Improved PDF validation
* [ ] Configurable chunk size and retrieval parameters
* [ ] Docker-based deployment
* [ ] Production deployment and monitoring

---

## 📌 Project Highlights

This project demonstrates practical implementation of:

* **Retrieval-Augmented Generation (RAG)**
* **Semantic search**
* **Vector databases**
* **Dense embeddings**
* **LLM integration**
* **Document ingestion pipelines**
* **REST API development**
* **Backend/frontend separation**
* **Input validation and HTTP status codes**
* **Environment-based configuration**
* **Modular software architecture**




## 👨‍💻 Project Purpose

The project was developed to explore the practical implementation of an end-to-end AI application combining:

**LLMs + RAG + Vector Databases + REST APIs + Document Processing + Web UI**

It demonstrates how an AI-powered application can be structured as a modular system rather than as a standalone LLM prompt.

---


## 📜 License

This project is licensed under the terms specified in the `LICENSE` file.
