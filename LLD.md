# Low-Level Design (LLD) — AI Travel Assistant

## 1. API Contract Specifications

### 1.1 Endpoint Overview Matrix

| Method | Path | Request Body / Params | Response Body Schema | Status Codes | Auth Required |
|---|---|---|---|---|---|
| `GET` | `/` | None | `{"message": str}` | `200 OK` | No |
| `POST` | `/upload` | Multipart form data: `file: UploadFile` | Success: `{"message": str, ...ingest summary}` / Error: `{"detail": str}` | `201 Created`, `400 Bad Request`, `413 Payload Too Large`, `500 Internal Server Error` | No |
| `POST` | `/ask` | JSON: `{"query": str}` | Success: `{"response": str}` / Error: `{"detail": str}` | `200 OK`, `400 Bad Request`, `422 Unprocessable Entity`, `502 Bad Gateway` | No |

---

### 1.2 Endpoint Specifications

#### 1. `GET /`
- **Description**: API health check endpoint verifying FastAPI server status.
- **Handler**: `root()` in [`src/main.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/main.py)

#### 2. `POST /upload`
- **Description**: Uploads and ingests a PDF travel guide into Qdrant vector database.
- **Handler**: `upload_file(file: UploadFile)` in [`src/main.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/main.py)
- **Request Content-Type**: `multipart/form-data`
- **Validation** (in order):
  1. File presence check (`if not file`) → `400 Bad Request`
  2. `.pdf` file extension check → `400 Bad Request`
  3. File size check against `MAX_FILE_SIZE_BYTES` (10 MB) → `413 Payload Too Large`. File pointer is reset (`await file.seek(0)`) after this read so `ingest_pdf()` can read the content again from the start.
- **Success Response (`201 Created`)** — 201 rather than 200 because a new resource (vector embeddings + chunks in Qdrant) was created:
  ```json
  {
    "message": "File processed successfully",
    "filename": "Paris_Travel_Guide.pdf",
    "total_pages": 12,
    "total_chunks": 34,
    "status": "success"
  }
  ```
- **Error Responses** — all raised via FastAPI `HTTPException`, so the message is under `"detail"`, not `"message"`:
  ```json
  // 400 — no file attached
  { "detail": "No file uploaded" }
  ```
  ```json
  // 400 — wrong extension
  { "detail": "Please upload a PDF file" }
  ```
  ```json
  // 413 — file too large
  { "detail": "File exceeds 10MB limit" }
  ```
  ```json
  // 500 — ingestion pipeline failed (parsing/chunking/embedding/DB write)
  // raw exception is logged server-side via logger.exception(), never returned to client
  { "detail": "Error processing file" }
  ```

#### 3. `POST /ask`
- **Description**: Queries vector database and returns generated travel itinerary/answers.
- **Handler**: `ask_question(req: QueryRequest)` in [`src/main.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/main.py)
- **Request Schema (`QueryRequest`)**:
  ```json
  { "query": "What are the top attractions in Tokyo?" }
  ```
- **Validation**: `req.query.strip()` must be non-empty → `400 Bad Request` if empty/whitespace-only.
- **Success Response (`200 OK`)**:
  ```json
  { "response": "Based on the travel guide, top attractions include Senso-ji Temple, Tokyo Tower, and Shibuya Crossing." }
  ```
- **Error Responses**:
  ```json
  // 400 — empty query
  { "detail": "Query cannot be empty" }
  ```
  ```json
  // 422 — malformed request body, handled automatically by Pydantic before the handler runs
  ```
  ```json
  // 502 — generate_answer() failed (model or Qdrant dependency failure)
  // raw exception is logged server-side via logger.exception(), never returned to client
  { "detail": "Failed to generate an answer right now" }
  ```

---

## 2. Qdrant Vector Collection & Payload Schema
*(unchanged — no code changes made to embeddings, retrieval, or vector storage)*

- **Collection Name**: `COLLECTION_NAME` env var (default: `travel_guides`)
- **Vector Dimensions**: `384`, matching `SentenceTransformer('all-MiniLM-L6-V2')`
- **Distance Metric**: `Distance.COSINE`
- **Initialization Code**: [`src/vectorstores.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/vectorstores.py)

Payload per point:
```json
{
  "text": "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France...",
  "page": 0,
  "source": "Paris_Travel_Guide.pdf"
}
```

---

## 3. Detailed Ingestion Pipeline Execution
*(unchanged — RAG pipeline logic was not modified)*

Implemented in [`src/ingest.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/ingest.py). See original pipeline: memory read → `fitz` parse → `RecursiveCharacterTextSplitter(500, 100)` → `get_embeddings()` → `upload_collection()`.

---

## 4. Retrieval & Context Window Logic
*(unchanged — no code changes made to retrieval logic)*

Implemented in [`src/retriever.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/retriever.py). Query embedded → `client.query_points(top_k=2)` → context truncated to 800 chars in `generator.py`.

---

## 5. Generation Logic & Provider Branching
*(unchanged — no code changes made to prompt/generation logic)*

Implemented in [`src/generator.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/generator.py).

---

## 6. Error Handling & Failure Mode Matrix

| Scenario / Failure Mode | Exception Source | HTTP Status | Handler Behavior |
|---|---|---|---|
| No file attached in upload request | `src/main.py` — `upload_file()` | `400 Bad Request` | `raise HTTPException(400, detail="No file uploaded")` |
| Non-PDF file uploaded | `src/main.py` — `upload_file()` | `400 Bad Request` | `raise HTTPException(400, detail="Please upload a PDF file")` |
| Uploaded file exceeds 10 MB | `src/main.py` — `upload_file()` | `413 Payload Too Large` | `raise HTTPException(413, detail="File exceeds 10MB limit")` |
| Corrupted / unparseable PDF, or any failure inside `ingest_pdf()` (parsing, chunking, embedding, Qdrant write) | `src/ingest.py` / PyMuPDF / Qdrant | `500 Internal Server Error` | Caught in `try/except`, logged via `logger.exception()`, raises `HTTPException(500, detail="Error processing file")` — raw exception string is **not** exposed to the client |
| Empty / whitespace-only query | `src/main.py` — `ask_question()` | `400 Bad Request` | `raise HTTPException(400, detail="Query cannot be empty")` |
| Malformed `/ask` request body (fails `QueryRequest` schema) | FastAPI / Pydantic (automatic) | `422 Unprocessable Entity` | Handled by FastAPI before the route function executes; no custom code needed |
| `generate_answer()` fails (model inference or Qdrant query failure) | `src/main.py` — `ask_question()` | `502 Bad Gateway` | Caught in `try/except`, logged via `logger.exception()`, raises `HTTPException(502, detail="Failed to generate an answer right now")` — 502 chosen specifically because the failure originates in an upstream dependency, not the endpoint's own logic |
| Any other unhandled exception anywhere in the app | Global handler — `src/main.py` | `500 Internal Server Error` | `@app.exception_handler(Exception)` logs full traceback via `logger.exception()` and returns a generic `{"message": "Internal server error. Please try again later."}` body as a safety net |

---

## 7. Environment & Configuration Schema

Defined in [`src/config.py`](file:///c:/Users/Admin/Desktop/AI%20-travel-assistant/src/config.py) — variable list unchanged.

A `.env.example` file has been added at the project root listing all required variable names with placeholder values (no real secrets). This lets a new contributor set up `.env` correctly without needing the actual credentials, and keeps the required configuration self-documenting in the repo.

---

## 8. Testing Strategy & Verification Guidelines
*(unchanged from original — no test files have been added yet)*