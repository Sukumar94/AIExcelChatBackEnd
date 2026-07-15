# 🎨 ARCHITECTURE VISUAL GUIDE & QUICK REFERENCE

## 📱 User Journey Map

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
   ┌────────────┐                     ┌──────────────┐
   │ Upload File│                     │ Chat with AI │
   └────┬───────┘                     └────┬─────────┘
        │                                  │
        ▼                                  ▼
   ┌─────────────────────────────────────────────┐
   │     Frontend (React @ port 5173)            │
   │  - File selector / Chat interface           │
   │  - Chart visualization                      │
   │  - Message history                          │
   └────────────────┬────────────────────────────┘
                    │ HTTP REST
                    ▼
   ┌─────────────────────────────────────────────┐
   │     Backend (FastAPI @ port 8000)           │
   │  - Validate & process                       │
   │  - Run AI agents                            │
   │  - Query database                           │
   └────────┬─────────────┬─────────────┬────────┘
            │             │             │
            ▼             ▼             ▼
     ┌────────────┐ ┌────────────┐ ┌──────────────┐
     │  DuckDB    │ │   FAISS    │ │   Ollama     │
     │  (SQL DB)  │ │  (Vector)  │ │   (LLM)      │
     └────────────┘ └────────────┘ └──────────────┘
```

---

## 🔄 Data Flow Simplified

```
┌─────────────┐
│  UPLOAD     │ → ExcelParser → DataCleaner → Parquet
└─────────────┘                                  ↓
                                           DuckDB View
                                                 ↓
                                           FAISS Index
                                                 ↓
                                            RAG Storage
```

```
┌─────────────┐
│  CHAT       │ → QueryPlanner (LLM) → Intent
└─────────────┘                          ↓
                                    RAG Retrieval
                                         ↓
                                 SQLGeneration (LLM)
                                         ↓
                                    DuckDB Execute
                                         ↓
                                AnswerGeneration (LLM)
                                         ↓
                                 ChartGeneration (LLM)
                                         ↓
                                    Response to User
```

---

## 🏗️ Layers Architecture (Simplified)

```
┌─────────────────────────────────────────┐
│         CLIENT LAYER (React)            │
│   UI Components + State Management      │
└─────────────────────────────────────────┘
                    │
        ────────────┴────────────
        │                       │
┌───────▼─────────┐    ┌────────▼──────────┐
│ HTTP Requests   │    │ WebSocket (Future)│
└───────┬─────────┘    └───────────────────┘
        │
┌───────▼──────────────────────────────────┐
│     API LAYER (FastAPI)                  │
│  ├─ Route handlers                       │
│  ├─ Input validation (Pydantic)          │
│  ├─ Response formatting                  │
│  └─ Middleware (CORS, logging, etc.)     │
└───────┬──────────────────────────────────┘
        │
┌───────▼──────────────────────────────────┐
│    SERVICE LAYER (Business Logic)        │
│  ├─ UploadService                        │
│  ├─ ChatService                          │
│  ├─ ChartService                         │
│  ├─ ReportService                        │
│  ├─ AnalyticsService                     │
│  └─ SessionService                       │
└───────┬──────────────────────────────────┘
        │
┌───────▼──────────────────────────────────┐
│    AI LAYER                              │
│  ├─ LLMService (qwen2.5:7b)             │
│  ├─ EmbeddingService (nomic-embed-text) │
│  ├─ AIAgent (Orchestrator)              │
│  ├─ RAGService (FAISS + Context)        │
│  └─ QueryPlanner                        │
└───────┬──────────────────────────────────┘
        │
┌───────▼──────────────────────────────────┐
│    DATA LAYER                            │
│  ├─ DuckDB (Analytics DB)               │
│  ├─ FAISS Index (Vector Search)         │
│  ├─ Metadata Store (Chat History)       │
│  └─ File System (Parquet, Reports)      │
└───────────────────────────────────────────┘
```

---

## 🔌 API Endpoint Groups

```
Health & Status
├─ GET /api/v1/health

Upload & Session Management
├─ POST   /api/v1/upload              (Upload file)
├─ GET    /api/v1/session/{id}        (Get session)
├─ DELETE /api/v1/session/{id}        (Delete session)
└─ GET    /api/v1/session             (List sessions)

Chat & Conversation
├─ POST   /api/v1/chat                (Send message)
└─ GET    /api/v1/chat/history/{id}   (Get history)

Charts & Visualization
├─ GET    /api/v1/chart/{id}          (Get charts)
└─ POST   /api/v1/chart/generate      (Generate chart)

Analytics & Reports
├─ GET    /api/v1/analytics/{id}      (Get statistics)
├─ POST   /api/v1/report/generate     (Generate report)
├─ GET    /api/v1/dashboard/{id}      (Dashboard data)
└─ GET    /api/v1/report/{id}         (Download report)

Voice (Optional)
├─ POST   /api/v1/voice/transcribe    (Speech to text)
└─ POST   /api/v1/voice/synthesize    (Text to speech)
```

---

## 📊 Data Storage Locations

```
Project Root
├── data/
│   ├── uploads/          ← Raw Excel files
│   ├── parquet/          ← Processed Parquet files
│   ├── databases/
│   │   └── analytics.db  ← DuckDB file
│   ├── indexes/
│   │   ├── faiss.index   ← FAISS vector index
│   │   └── documents.pkl ← Index metadata
│   ├── reports/          ← Generated reports
│   ├── charts/           ← Chart configurations
│   └── temp/             ← Temporary files
├── app/
│   ├── api/              ← API routes
│   ├── services/         ← Business logic
│   ├── ai/               ← AI/LLM integration
│   ├── database/         ← Database layer
│   ├── excel/            ← Excel processing
│   ├── models/           ← Data models
│   ├── core/             ← Configuration
│   └── middleware/       ← Middleware
└── docs/                 ← Documentation
```

---

## 🧠 AI Components Relationship

```
┌─────────────────────────────────┐
│     User Question               │
└──────────────┬──────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  QueryPlanner        │
    │  (Intent Detection)  │
    │  Uses: LLMService    │
    └──────────┬───────────┘
               │
      ┌────────┴────────┐
      │                 │
      ▼                 ▼
   ┌────────────┐  ┌──────────────┐
   │ RAGService │  │ AIAgent      │
   │ (Retrieve) │  │ (Generate)   │
   │            │  │              │
   │ FAISS      │  │ ├─ SQL Gen   │
   │ Vector DB  │  │ ├─ Execute   │
   │            │  │ ├─ Answer Gen│
   │ Embeddings │  │ └─ Chart Gen │
   │ (768-dim)  │  │              │
   │            │  │ Uses:        │
   │ Stores:    │  │ - LLMService │
   │ - Schemas  │  │ - DuckDB     │
   │ - Q&As     │  │ - Embeddings │
   │ - History  │  │ - Prompts    │
   └────────────┘  └──────────────┘
      │                   │
      └─────────┬─────────┘
                │
                ▼
    ┌──────────────────────┐
    │  Response Builder    │
    │  (Format Output)     │
    └──────────────────────┘
                │
                ▼
    ┌──────────────────────┐
    │  User Response       │
    │  • Answer text       │
    │  • SQL query         │
    │  • Chart config      │
    │  • Sources           │
    └──────────────────────┘
```

---

## 🔄 Complete Request-Response Cycle

```
1. USER ACTION (Browser)
   └─ Click "Upload" or "Send Message"

2. REQUEST PREPARATION (React)
   └─ Package data as JSON/FormData
   └─ Add headers (Content-Type, etc.)

3. HTTP TRANSMISSION
   └─ HTTPS to http://localhost:8000/api/v1/*
   └─ Method: POST/GET

4. SERVER RECEIVES (FastAPI)
   └─ Route match
   └─ Dependency injection
   └─ Middleware processing

5. REQUEST VALIDATION (Pydantic)
   └─ Check types
   └─ Validate constraints
   └─ Raise errors if invalid

6. SERVICE PROCESSING
   ├─ UploadService: Parse/Clean/Convert
   └─ ChatService: Query/Answer/Chart

7. AI PROCESSING (if needed)
   ├─ LLMService: Generate SQL/Answers
   ├─ EmbeddingService: Encode queries
   └─ RAGService: Retrieve context

8. DATABASE QUERIES
   ├─ DuckDB: Execute SQL
   ├─ FAISS: Search vectors
   └─ File system: Read/Write

9. RESPONSE BUILDING (ResponseBuilder)
   └─ Format results
   └─ Add metadata
   └─ Convert to JSON

10. HTTP RESPONSE (FastAPI)
    └─ Status code: 200/400/500
    └─ Headers: Content-Type: application/json
    └─ Body: JSON response

11. BROWSER RECEIVES (Axios)
    └─ Parse JSON response
    └─ Handle errors if any

12. UI UPDATE (React)
    └─ Update state
    └─ Re-render components
    └─ Display results to user

13. USER SEES
    ├─ Chat message
    ├─ Chart visualization
    ├─ Generated report
    └─ Statistics
```

---

## 📈 Technology Stack Summary

```
FRONTEND
├─ React 18.3.1       (UI Framework)
├─ Vite 5.4.21        (Build tool)
├─ TypeScript          (Type safety)
├─ Axios               (HTTP client)
└─ Plotly.js           (Charts)

BACKEND
├─ FastAPI 0.139      (API framework)
├─ Uvicorn 0.51       (ASGI server)
├─ Pydantic 2.x       (Validation)
└─ Python 3.13.5      (Runtime)

DATA PROCESSING
├─ Polars              (DataFrames)
├─ Parquet             (Storage format)
└─ Openpyxl            (Excel parsing)

DATABASE
├─ DuckDB 1.5.4       (SQL engine)
├─ FAISS              (Vector DB)
└─ File system        (Metadata)

AI/ML
├─ Ollama             (LLM runtime)
├─ qwen2.5:7b         (Chat model)
├─ nomic-embed-text   (Embedding model)
└─ httpx              (HTTP client)

UTILITIES
├─ Logging            (Application logs)
├─ ReportLab          (PDF generation)
├─ Jinja2             (HTML templates)
└─ SQLAlchemy         (Optional ORM)
```

---

## ⚡ Performance Timeline

```
File Upload (100MB)
└─ 2-5 seconds total
   ├─ Validation: 200ms
   ├─ Parsing: 1-2s
   ├─ Cleaning: 500ms-1s
   ├─ Conversion: 500ms-1s
   └─ Indexing: 1s

Chat Query
└─ 3-5 seconds total
   ├─ Query Planning: 500ms-1s
   ├─ RAG Retrieval: 100-200ms
   ├─ SQL Generation: 500ms-1s
   ├─ SQL Execution: 100-500ms
   ├─ Answer Generation: 500ms-1s
   ├─ Chart Generation: 300-500ms
   └─ Response Formatting: 100ms

Report Generation
└─ 5-15 seconds total
   ├─ Data Collection: 1-2s
   ├─ Chart Generation: 2-5s
   ├─ Document Rendering: 2-5s
   └─ PDF Conversion: 1-3s
```

---

## 🔐 Security Layers

```
NETWORK
└─ HTTPS/TLS encryption
└─ CORS validation
└─ Rate limiting

APPLICATION
├─ Input validation (Pydantic)
├─ SQL injection prevention (Parameterized)
├─ XSS protection (Sanitization)
└─ CSRF tokens

AUTHENTICATION (Optional)
├─ API Keys
├─ JWT Tokens
└─ Session management

DATA
├─ Encrypted storage (Optional)
├─ Automatic cleanup (TTL)
├─ Access control (ACLs)
└─ Audit logging
```

---

## 🚀 Deployment Matrix

```
ENVIRONMENT   FRONTEND    BACKEND     DATABASE    OLLAMA
─────────────────────────────────────────────────────────
Development   npm dev     uvicorn     File        Local
              (5173)      (8000)      DuckDB      (11434)

Production    Nginx       Gunicorn    DuckDB      Local/Cloud
              (80/443)    (multiple)  (replicated) (GPU)

Docker        Alpine      Python      Volume      Container
              Image       Image       Mount       Image

Kubernetes    Pod         Pod         PVC         Pod
              Service     Service     StatefulSet Service
```

---

## 📞 Key Contacts & Resources

```
Internal Services:
├─ Frontend: http://localhost:5173 (dev)
├─ Backend API: http://localhost:8000 (dev)
├─ API Docs: http://localhost:8000/docs (Swagger)
└─ Ollama: http://localhost:11434 (LLM service)

Configuration:
├─ app/core/config.py (Main settings)
├─ app/core/constants.py (Constants)
└─ .env (Environment variables)

External Services:
├─ Ollama (Local LLM runtime)
├─ HuggingFace (Model hub)
└─ (Optional) OpenAI API (Future)

Data Directories:
├─ data/uploads/ (Excel files)
├─ data/databases/ (DuckDB)
├─ data/indexes/ (FAISS)
└─ data/reports/ (Generated files)
```

---

## ✅ Checklist: From Request to Response

```
User Action
  ✓ Click button or enter text
  
Frontend Processing
  ✓ Package data
  ✓ Validate locally
  ✓ Show loading state
  
HTTP Transmission
  ✓ Send request
  ✓ Include headers
  
Server Reception
  ✓ Route request
  ✓ Apply middleware
  
Data Validation
  ✓ Check types
  ✓ Validate constraints
  
Service Processing
  ✓ Load session
  ✓ Process data
  
AI Processing (if needed)
  ✓ Query LLM
  ✓ Generate response
  ✓ Create visualizations
  
Database Operations
  ✓ Execute queries
  ✓ Store results
  
Response Preparation
  ✓ Format output
  ✓ Add metadata
  
HTTP Response
  ✓ Set status code
  ✓ Send JSON
  
Frontend Receiving
  ✓ Parse response
  ✓ Handle errors
  
UI Update
  ✓ Update state
  ✓ Re-render
  
User Sees
  ✓ Results displayed
  ✓ Charts rendered
  ✓ Messages updated
```

---

## 🎯 Quick Navigation

| Need | File | Purpose |
|------|------|---------|
| **System Overview** | ARCHITECTURE_COMPLETE.md | Full technical details |
| **AI Components** | AI_COMPONENTS_DETAILED.md | LLM & embeddings info |
| **API Endpoints** | ARCHITECTURE_COMPLETE.md (section 6) | All routes |
| **Data Flow** | ARCHITECTURE_COMPLETE.md (section 5) | Step-by-step flows |
| **Setup Instructions** | START_HERE.md | Getting started |
| **Deployment** | ARCHITECTURE_COMPLETE.md (section 9) | Production guide |
| **This Guide** | You're reading it! | Visual reference |

---

## 📝 Notes

- All times are approximate and depend on data size/complexity
- System handles 10,000+ row Excel files efficiently
- LLM responses take 1-2 seconds due to local inference
- Production deployment recommended with load balancing
- DuckDB supports 2GB+ datasets without optimization
- FAISS index optimized for up to 100,000 embeddings

