# High-Level Design (HLD) — AI Travel Assistant

## 1. System Architecture Context Diagram
*(unchanged — no components added or removed)*

The AI Travel Assistant is a decoupled two-tier system (Streamlit Frontend + FastAPI Backend) backed by Qdrant and LLM inference providers (HuggingFace / OpenAI).

---

## 2. Component Responsibilities

| Component | Source File | Core Responsibilities |
|---|---|---|
| **Web Frontend** | [`src/app.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/app.py) | Provides Streamlit UI, renders PDF upload form, handles question input, and parses backend responses — reads success messages from the `"message"` key and error details from the `"detail"` key (matching FastAPI's `HTTPException` format), checking the actual `response.status_code` (`201` for successful upload, `200` for successful ask) rather than assuming success. |
| **API Web Server** | [`src/main.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/main.py) | Implements `POST /upload`, `POST /ask`, `GET /`; manages async lifespan DB init; validates all input at the route level (file presence, extension, size; non-empty query) and raises `HTTPException` with a status code matched to the failure's cause; wraps pipeline calls in `try/except` with `logger.exception()` for server-side diagnostics; registers a global `@app.exception_handler(Exception)` as a catch-all safety net. |
| **Document Ingestor** | [`src/ingest.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/ingest.py) | Stream-reads PDFs, chunks text, calls embedding engine, stores vectors into Qdrant. *(unchanged)* |
| **Vector Searcher** | [`src/retriever.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/retriever.py) | Generates query embeddings, queries Qdrant, extracts payload text. *(unchanged)* |
| **LLM Generator** | [`src/generator.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/generator.py) | Builds prompts, truncates context, executes inference. *(unchanged)* |
| **Embedding Engine** | [`src/embeddings.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/embeddings.py) | Produces 384-d embeddings. *(unchanged)* |
| **Vector Store Manager** | [`src/vectorstores.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/vectorstores.py) | Manages Qdrant client and collection init. *(unchanged)* |
| **Configuration** | [`src/config.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/config.py) | Loads `.env` variables. *(unchanged)* |

---

## 3. Data Flow Journeys

### 3.1 Document Upload Journey *(updated)*

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Streamlit as Streamlit UI (src/app.py)
    participant FastAPI as FastAPI Server (src/main.py)
    participant Ingest as Ingestion Service (src/ingest.py)
    participant Qdrant as Qdrant DB (src/vectorstores.py)

    User->>Streamlit: Upload PDF & click "Process Guide"
    Streamlit->>FastAPI: POST /upload (files={"file": uploaded_file})
    FastAPI->>FastAPI: Validate file presence -> 400 if missing
    FastAPI->>FastAPI: Validate .pdf extension -> 400 if wrong type
    FastAPI->>FastAPI: Read content, validate size <= 10MB -> 413 if too large
    FastAPI->>Ingest: await ingest_pdf(file)
    Ingest->>Ingest: Parse, chunk, embed
    Ingest->>Qdrant: client.upload_collection(collection, vectors, payload)
    alt Ingestion succeeds
        Qdrant-->>Ingest: Upload success
        Ingest-->>FastAPI: Return summary dict
        FastAPI-->>Streamlit: HTTP 201 {"message": "File processed successfully", ...summary}
        Streamlit-->>User: Display Success Toast
    else Ingestion fails (parse/embed/DB error)
        Ingest--xFastAPI: Exception raised
        FastAPI->>FastAPI: logger.exception(); raise HTTPException(500)
        FastAPI-->>Streamlit: HTTP 500 {"detail": "Error processing file"}
        Streamlit-->>User: Display Error message from response.json()["detail"]
    end
```

### 3.2 Question-Answering & Retrieval Journey *(updated)*

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Streamlit as Streamlit UI (src/app.py)
    participant FastAPI as FastAPI Server (src/main.py)
    participant Generator as Answer Generator (src/generator.py)
    participant Retriever as Retrieval Engine (src/retriever.py)
    participant Qdrant as Qdrant DB (src/vectorstores.py)
    participant LLM as LLM Engine (Flan-T5 / OpenAI)

    User->>Streamlit: Enter query & click "Ask"
    Streamlit->>FastAPI: POST /ask {"query": "Best places in Paris"}
    FastAPI->>FastAPI: Validate query.strip() non-empty -> 400 if empty
    FastAPI->>Generator: generate_answer(query)
    Generator->>Retriever: retrieve_docs(query, top_k=2)
    Retriever->>Qdrant: client.query_points(collection, query_vector, limit=2)
    Qdrant-->>Retriever: Return ScoredPoints
    Retriever-->>Generator: Return List[str] docs
    Generator->>LLM: Execute LLM inference
    alt Generation succeeds
        LLM-->>Generator: Decoded answer string
        Generator-->>FastAPI: Return answer string
        FastAPI-->>Streamlit: HTTP 200 {"response": answer}
        Streamlit-->>User: Render Travel Itinerary Answer
    else Generation fails (model or Qdrant dependency error)
        Generator--xFastAPI: Exception raised
        FastAPI->>FastAPI: logger.exception(); raise HTTPException(502)
        FastAPI-->>Streamlit: HTTP 502 {"detail": "Failed to generate an answer right now"}
        Streamlit-->>User: Display Error message from response.json()["detail"]
    end
```

---

## 4. Technology Stack Matrix
*(unchanged)*

---

## 5. Deployment Architecture & Configuration

### 5.1 Local Service Execution
*(unchanged)*

### 5.2 Required Environment Variables (`.env`)
```ini
QDRANT_HOST=https://your-qdrant-cluster-url.qdrant.tech:6333
QDRANT_API_KEY=your_qdrant_api_key_here
COLLECTION_NAME=travel_guides
OPENAI_API_KEY=sk-proj-your_openai_key_here
MODEL_PROVIDER=huggingface
```

A `.env.example` file with the same variable names and placeholder values has been added to the repo root *(new)*. It's safe to commit since it holds no real secrets, and it documents exactly which variables a new environment needs — `.env` itself stays gitignored and untracked.

---

## 6. Security & Architectural Trade-offs

### 6.1 Security Architecture
- **In-Memory Streaming**: Uploaded PDFs are read into memory and processed without writing to temporary disk storage. *(unchanged)*
- **Environment Isolation**: API tokens are managed entirely through server-side `.env` and never exposed to the browser. *(unchanged)*
- **Bounded Upload Size** *(new)*: `/upload` now rejects files over 10 MB before ingestion begins, preventing a single request from consuming excessive memory or embedding-model compute.
- **Error Detail Isolation** *(new)*: Internal exception messages (stack traces, library error strings) are logged server-side via `logger.exception()` but never returned in the API response body — clients only see a generic, safe `detail` message. This prevents leaking implementation details (file paths, library versions, internal state) to callers.

### 6.2 Key Architectural Decisions
- **PyMuPDF In-Memory Parsing vs Disk Storage**: Keeps ingestion stateless. *(unchanged)*
- **Fixed-Window Chunking (500/100) vs Page-Level Indexing**: *(unchanged)*
- **Dual Model Provider Support**: *(unchanged)*
- **Status-Code-per-Failure-Cause** *(new)*: Rather than returning `200 OK` for every outcome, each failure mode maps to the HTTP status that best identifies who caused it and whether a retry could help — `400`/`413` for client-fixable request errors, `500`/`502` for server-side or upstream-dependency failures. This makes the API's error surface machine-distinguishable, not just human-readable.