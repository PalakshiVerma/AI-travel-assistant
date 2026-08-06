# High-Level Design (HLD) — AI Travel Assistant

## 1. System Architecture Context Diagram

The AI Travel Assistant is constructed as a decoupled two-tier micro-service system (Streamlit Frontend + FastAPI Backend) backed by a vector database engine (Qdrant) and LLM inference providers (HuggingFace Transformers / OpenAI API).

```mermaid
flowchart TD
    subgraph Client Layer
        UI["Streamlit Web Client\n(src/app.py)"]
    end

    subgraph Application Server Layer
        API["FastAPI App & Endpoints\n(src/main.py)"]
        
        subgraph Services
            INGEST["PDF Ingestion Service\n(src/ingest.py)"]
            EMBED["Embedding Engine\n(src/embeddings.py)"]
            RETRIEVE["Retrieval Engine\n(src/retriever.py)"]
            GEN["Answer Generator\n(src/generator.py)"]
            CFG["Config & Environment\n(src/config.py)"]
        end
    end

    subgraph Data & AI Infrastructure Layer
        VDB[("Qdrant Vector DB\n(src/vectorstores.py)")]
        HF["HuggingFace Flan-T5\n(google/flan-t5-base)"]
        OAI["OpenAI API\n(gpt-3.5-turbo)"]
    end

    UI -- "HTTP POST /upload (Multipart)" --> API
    UI -- "HTTP POST /ask (JSON)" --> API

    API --> INGEST
    API --> GEN

    INGEST -- "Extract text & chunk" --> INGEST
    INGEST -- "Encode chunks" --> EMBED
    INGEST -- "Upload vectors & payloads" --> VDB

    GEN -- "Query vector search" --> RETRIEVE
    RETRIEVE -- "Encode query" --> EMBED
    RETRIEVE -- "Cosine search (top_k=2)" --> VDB
    VDB -- "Matching context text" --> RETRIEVE
    RETRIEVE -- "Retrieved docs" --> GEN

    GEN -- "MODEL_PROVIDER == 'huggingface'" --> HF
    GEN -- "MODEL_PROVIDER == 'openai'" --> OAI

    CFG -. "Inject credentials & settings" .-> API
```

---

## 2. Component Responsibilities

| Component | Source File | Core Responsibilities |
|---|---|---|
| **Web Frontend** | [`src/app.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/app.py) | Provides interactive Streamlit UI, renders PDF file upload form in sidebar, handles user question input, and formats response messages. |
| **API Web Server** | [`src/main.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/main.py) | Implements FastAPI web application framework, defines `POST /upload`, `POST /ask`, and `GET /` endpoints, manages async lifespan database initialization hooks. |
| **Document Ingestor** | [`src/ingest.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/ingest.py) | Stream-reads PDF files using PyMuPDF (`fitz`), splits text into 500-char chunks via `RecursiveCharacterTextSplitter`, calls embedding engine, and stores vectors into Qdrant. |
| **Vector Searcher** | [`src/retriever.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/retriever.py) | Generates dense query vector embeddings, queries Qdrant DB via `query_points`, and extracts payload text strings. |
| **LLM Generator** | [`src/generator.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/generator.py) | Builds PromptTemplate, orchestrates retrieval, truncates context to 800 chars, executes inference via Flan-T5 local pipeline or OpenAI `ChatOpenAI`. |
| **Embedding Engine** | [`src/embeddings.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/embeddings.py) | Wraps `SentenceTransformer('all-MiniLM-L6-V2')` model to produce 384-dimensional floating-point embeddings. |
| **Vector Store Manager** | [`src/vectorstores.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/vectorstores.py) | Manages `QdrantClient` connection instance and initializes vector collection (`VectorParams(size=384, distance=Distance.COSINE)`). |
| **Configuration** | [`src/config.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/config.py) | Loads `.env` environment variables (`QDRANT_HOST`, `QDRANT_API_KEY`, `COLLECTION_NAME`, `OPENAI_API_KEY`, `MODEL_PROVIDER`, `FASTAPI_URL`). |

---

## 3. Data Flow Journeys

### 3.1 Document Upload Journey

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Streamlit as Streamlit UI (src/app.py)
    participant FastAPI as FastAPI Server (src/main.py)
    participant Ingest as Ingestion Service (src/ingest.py)
    participant PyMuPDF as PyMuPDF / fitz
    participant Embed as SentenceTransformer (src/embeddings.py)
    participant Qdrant as Qdrant DB (src/vectorstores.py)

    User->>Streamlit: Upload PDF & click "Process Guide"
    Streamlit->>FastAPI: POST /upload (files={"file": uploaded_file})
    FastAPI->>FastAPI: Validate file extension (.pdf)
    FastAPI->>Ingest: await ingest_pdf(file)
    Ingest->>PyMuPDF: fitz.open(stream=content, filetype="pdf")
    PyMuPDF-->>Ingest: Extract text per page
    Ingest->>Ingest: RecursiveCharacterTextSplitter(chunk_size=500, overlap=100)
    Ingest->>Embed: get_embeddings(texts)
    Embed-->>Ingest: Return List[List[float]] (384-d)
    Ingest->>Qdrant: client.upload_collection(collection, vectors, payload)
    Qdrant-->>Ingest: Upload success
    Ingest-->>FastAPI: Return summary dict (status, total_chunks)
    FastAPI-->>Streamlit: HTTP 200 {"message": "File processed successfully"}
    Streamlit-->>User: Display Success Toast
```

### 3.2 Question-Answering & Retrieval Journey

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Streamlit as Streamlit UI (src/app.py)
    participant FastAPI as FastAPI Server (src/main.py)
    participant Generator as Answer Generator (src/generator.py)
    participant Retriever as Retrieval Engine (src/retriever.py)
    participant Embed as SentenceTransformer (src/embeddings.py)
    participant Qdrant as Qdrant DB (src/vectorstores.py)
    participant LLM as LLM Engine (Flan-T5 / OpenAI)

    User->>Streamlit: Enter query & click "Ask"
    Streamlit->>FastAPI: POST /ask {"query": "Best places in Paris"}
    FastAPI->>Generator: generate_answer(query)
    Generator->>Retriever: retrieve_docs(query, top_k=2)
    Retriever->>Embed: get_embeddings([query])
    Embed-->>Retriever: Return query_vector (384-d)
    Retriever->>Qdrant: client.query_points(collection, query_vector, limit=2)
    Qdrant-->>Retriever: Return ScoredPoints with payload["text"]
    Retriever-->>Generator: Return List[str] docs
    Generator->>Generator: Truncate context to 800 chars & format PromptTemplate
    Generator->>LLM: Execute LLM inference (model.generate / qa_chain.invoke)
    LLM-->>Generator: Decoded answer string
    Generator-->>FastAPI: Return answer string
    FastAPI-->>Streamlit: HTTP 200 {"response": answer}
    Streamlit-->>User: Render Travel Itinerary Answer
```

---

## 4. Technology Stack Matrix

| Layer | Component | Technology | Rationale & Selection Criteria |
|---|---|---|---|
| **Frontend** | Interactive Web UI | Streamlit | Rapid prototyping of Python-native data and AI web applications without custom JavaScript/CSS. |
| **Backend API** | REST Microservice | FastAPI + Uvicorn | High-performance asynchronous Python web framework with Pydantic validation and native OpenAPI docs. |
| **PDF Parser** | In-Memory Extractor | PyMuPDF (`fitz`) | Blazing fast C-backed PDF text extraction without needing external OCR dependencies or temporary disk files. |
| **Chunking** | Text Splitter | LangChain Text Splitters | Standardized character-level splitting with overlapping window support (`RecursiveCharacterTextSplitter`). |
| **Embeddings** | Dense Vector Model | `sentence-transformers/all-MiniLM-L6-v2` | Lightweight 384-dimensional model offering ideal trade-off between latency, memory footprint, and semantic quality. |
| **Vector DB** | Vector Storage Engine | Qdrant Cloud / Local | Fast, production-ready vector engine supporting payload metadata indexing and Cosine distance similarity. |
| **LLM Inference** | Language Model Engine | HuggingFace `google/flan-t5-base` / OpenAI `gpt-3.5-turbo` | Flexible dual-mode architecture: offline local inference via PyTorch/Transformers or high-accuracy cloud generation. |

---

## 5. Deployment Architecture & Configuration

### 5.1 Local Service Execution
The application runs as two separate Python processes interacting over HTTP localhost (`http://localhost:8000`):

```powershell
# Backend Server Process (Uvicorn)
.\venv\Scripts\python.exe -m uvicorn src.main:app --reload

# Frontend UI Process (Streamlit)
.\venv\Scripts\python.exe -m streamlit run src/app.py
```

### 5.2 Required Environment Variables (`.env`)
```ini
QDRANT_HOST=https://your-qdrant-cluster-url.qdrant.tech:6333
QDRANT_API_KEY=your_qdrant_api_key_here
COLLECTION_NAME=travel_guides
OPENAI_API_KEY=sk-proj-your_openai_key_here
MODEL_PROVIDER=huggingface
```

---

## 6. Security & Architectural Trade-offs

### 6.1 Security Architecture
- **In-Memory Streaming**: Uploaded PDF files are read directly into memory buffers (`file.read()`) and processed without writing raw sensitive documents to temporary disk storage.
- **Environment Isolation**: API tokens (`QDRANT_API_KEY`, `OPENAI_API_KEY`) are managed entirely through server-side `.env` files and never exposed to the Streamlit client browser.

### 6.2 Key Architectural Decisions
- **PyMuPDF In-Memory Parsing vs Disk Storage**: Keeps ingestion state stateless and clean.
- **Fixed-Window Chunking (500/100) vs Page-Level Indexing**: 500-character chunks ensure granular semantic search while preserving context boundary continuity via 100-character overlap.
- **Dual Model Provider Support**: Allows seamless switching between low-latency local execution (Flan-T5) and high-capability cloud LLMs (GPT-3.5-Turbo) by changing a single configuration key.
