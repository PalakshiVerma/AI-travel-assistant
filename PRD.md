# Product Requirements Document (PRD) — AI Travel Assistant

## 1. Problem Statement, Goals, and Non-Goals
*(unchanged)*

### 1.1 Problem Statement
Travelers frequently struggle to extract actionable, personalized travel itineraries and specific destination facts from lengthy PDF travel guides and brochures.

### 1.2 Goals
- Provide an intuitive web application where users can upload PDF travel guides.
- Ingest and chunk PDF documents, converting text content into dense vector embeddings for semantic indexing.
- Allow users to ask natural language questions about travel destinations.
- Retrieve the most relevant contextual passages from Qdrant vector database and generate concise, accurate answers using LLM technology.

### 1.3 Non-Goals
- Real-time booking or flight/hotel reservation integration.
- Multi-user authentication, JWT session management, or access control.
- Support for non-PDF document formats.
- Async background job queues or persistent offline worker nodes.

---

## 2. Target Users & User Stories
*(unchanged)*

| ID | As a | I want to | So that |
|---|---|---|---|
| `US-1` | Traveler | Upload a PDF travel guide through the web UI | The assistant can index and search the guide's specific content. |
| `US-2` | Traveler | Ask natural language travel questions | I receive instant, accurate answers extracted from my uploaded guide. |
| `US-3` | Traveler | Receive responses generated from LLMs backed by retrieved context | Answers are factual, relevant, and free from hallucinations. |
| `US-4` | System Admin | Configure LLM providers via environment variables | The app can run locally offline or leverage cloud APIs flexibly. |

---

## 3. Functional Requirements

### 3.1 Document Ingestion & Vector Indexing (`FR-ING`)
- **`FR-ING-1`**: The system shall accept PDF file uploads via multipart HTTP requests at `POST /upload`.
- **`FR-ING-2`**: The system shall parse PDF content directly in memory using PyMuPDF (`fitz`).
- **`FR-ING-3`**: The system shall split document text into chunks using `RecursiveCharacterTextSplitter` (chunk_size=500, chunk_overlap=100).
- **`FR-ING-4`**: The system shall generate 384-dimensional embeddings using `sentence-transformers/all-MiniLM-L6-v2`.
- **`FR-ING-5`**: The system shall upload embeddings and metadata into the Qdrant vector database collection.
- **`FR-ING-6`** *(new)*: The system shall reject uploaded files exceeding **10 MB** with an `HTTP 413 Payload Too Large` response, and reject missing files or non-`.pdf` extensions with an `HTTP 400 Bad Request` response — both without attempting ingestion.

### 3.2 Information Retrieval & Generation (`FR-QA`)
- **`FR-QA-1`**: The system shall accept natural language query strings via JSON payload at `POST /ask`.
- **`FR-QA-2`**: The system shall encode the query into a 384-d vector and perform Cosine similarity search against Qdrant (`top_k=2`).
- **`FR-QA-3`**: The system shall truncate context text to a maximum of 800 characters before prompt injection.
- **`FR-QA-4`**: The system shall execute LLM inference via Flan-T5 or OpenAI based on `MODEL_PROVIDER`.
- **`FR-QA-5`** *(new)*: The system shall reject empty or whitespace-only queries with an `HTTP 400 Bad Request` response before attempting retrieval or generation.

### 3.3 Operations & Infrastructure (`FR-OPS`)
- **`FR-OPS-1`**: The backend shall initialize the Qdrant collection automatically on server startup via FastAPI lifespan hooks.
- **`FR-OPS-2`**: The system shall load environment configuration from a `.env` file via `python-dotenv`.
- **`FR-OPS-3`** *(new)*: Failures in the ingestion or generation pipeline shall be logged server-side with full detail (via Python `logging`) while returning a generic, non-sensitive error message to the client, so internal exception details are never exposed over the API.

---

## 4. Non-Functional Requirements

| Category | Requirement Description | Target Metric |
|---|---|---|
| **Performance** | End-to-end Q&A retrieval and generation latency | < 3 seconds (OpenAI) / < 5 seconds (Flan-T5 CPU) |
| **Performance** | PDF processing and embedding throughput | < 2 seconds for a 10-page PDF document |
| **Portability** | System execution across local platforms | Windows / Linux / macOS with Python 3.10+ |
| **Reliability** | File upload input validation | Reject missing files, non-PDF extensions, and files over 10 MB with distinct, correctly-classified HTTP status codes (`400` vs `413`) rather than a uniform `200` response *(updated)* |
| **Reliability** | API error transparency | Every failure mode (client-caused or server-caused) returns a distinguishable HTTP status code; server-side root causes are logged, not leaked to the client *(new)* |
| **Maintainability** | Modular Python architecture | Decoupled files for API, UI, Ingest, Retrieval, Vectorstore, and LLM |

---

## 5. Success Metrics
*(unchanged)*

- **Zero Ingestion Failures**: 100% successful parsing rate for standard vector-capable PDF travel documents.
- **Vector Dimension Alignment**: 100% match between SentenceTransformer output and Qdrant collection parameters.
- **Context Fallback Reliability**: Graceful fallback to general itinerary generation when vector database context is empty.
- **Service Uptime**: Clean system boot and lifespan startup without manual database collection initialization.

---

## 6. Phased Milestones
*(unchanged from original roadmap)*