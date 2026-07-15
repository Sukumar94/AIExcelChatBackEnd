# 🏗️ COMPLETE API ARCHITECTURE & DATA FLOW

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Diagram](#architecture-diagram)
4. [Component Details](#component-details)
5. [End-to-End Data Flows](#end-to-end-data-flows)
6. [API Endpoints](#api-endpoints)
7. [Database Schema](#database-schema)
8. [AI Integration](#ai-integration)
9. [Deployment Architecture](#deployment-architecture)

---

## 🎯 System Overview

**AI Excel Analytics Platform** is an intelligent data analysis application that combines:
- **Frontend**: React SPA (http://localhost:5173)
- **Backend**: FastAPI REST API (http://localhost:8000)
- **Database**: DuckDB (in-process analytics DB)
- **Vector DB**: FAISS (for semantic search)
- **AI Engine**: Ollama (local LLM + embeddings)
- **Data Format**: Polars DataFrames → Parquet → DuckDB

### **Core Capabilities**
✅ Upload Excel files with automatic parsing & validation  
✅ Natural language queries with AI-powered SQL generation  
✅ Automatic chart generation based on data patterns  
✅ Multi-turn conversations with context preservation  
✅ Report generation (PDF/HTML/Excel export)  
✅ Advanced analytics and statistics  
✅ Voice-based queries and responses  

---

## 🛠️ Technology Stack

### **Frontend (Client)**
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3.1 | UI framework |
| **Vite** | 5.4.21 | Build tool & dev server |
| **TypeScript** | Latest | Type safety |
| **Axios** | Latest | HTTP client |
| **Plotly.js** | Latest | Chart visualization |

**Port**: 5173  
**Commands**: `npm run dev` (dev), `npm run build` (production)

### **Backend (Server)**
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.139.0 | REST API framework |
| **Uvicorn** | 0.51.0 | ASGI server |
| **Pydantic** | 2.x | Data validation |
| **Python** | 3.13.5 | Runtime |

**Port**: 8000  
**Command**: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`

### **Data Processing**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Polars** | Latest | DataFrame processing |
| **Parquet** | - | Columnar storage format |
| **Openpyxl** | Latest | Excel file parsing |
| **DuckDB** | 1.5.4 | In-process SQL engine |

### **AI/ML**
| Technology | Purpose |
|------------|---------|
| **Ollama** | Local LLM runtime |
| **qwen2.5:7b** | Chat & inference model (7B params) |
| **nomic-embed-text** | Embedding model (768-dim vectors) |
| **FAISS** | Vector similarity search |
| **HuggingFace** | Model repository |

### **Storage & Persistence**
| Location | Format | Purpose |
|----------|--------|---------|
| `data/uploads/` | .xlsx | Uploaded Excel files |
| `data/parquet/` | .parquet | Processed data (Parquet format) |
| `data/databases/` | .db | DuckDB analytics database |
| `data/indexes/` | .index/.pkl | FAISS vector indexes + metadata |
| `data/reports/` | .pdf/.html/.xlsx | Generated reports |
| `data/charts/` | .json | Chart configurations |
| `data/temp/` | Various | Temporary processing files |

### **Dependencies**
```
Backend: FastAPI, Uvicorn, Pydantic, Polars, DuckDB, FAISS, Ollama
Frontend: React, Vite, Axios, Plotly.js
AI: Ollama (external service)
Database: DuckDB (embedded)
```

---

## 🏛️ Architecture Diagram

### **High-Level System Architecture**
```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│                    React SPA (Port 5173)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │  Chat UI     │  │  Analytics   │  │  Report/Export    │    │
│  │  (Multi-turn)│  │  Dashboard   │  │  (PDF/HTML/XLSX)  │    │
│  └──────────────┘  └──────────────┘  └───────────────────┘    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                 HTTP/REST (Axios)
                       │
┌──────────────────────┴──────────────────────────────────────────┐
│                      API LAYER (FastAPI)                        │
│                   Port 8000, Uvicorn                            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Middleware Stack                           │   │
│  │  • CORS Middleware (http://localhost:5173)            │   │
│  │  • Exception Handling Middleware                       │   │
│  │  • Logging Middleware                                  │   │
│  │  • Request Context Middleware                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────┬───────────┼───────────┬──────────┬────────┐    │
│  │ Upload API │ Chat API  │Chart API  │Report API│Export  │    │
│  │ /upload/   │ /chat/    │/chart/    │/report/  │/export/    │
│  └────────────┴───────────┼───────────┴──────────┴────────┘    │
│                           │                                     │
│  ┌───────────────────────┴───────────────────────────────┐     │
│  │           SERVICE LAYER (Business Logic)             │     │
│  │                                                       │     │
│  │  ┌─────────────────────────────────────────────┐    │     │
│  │  │ UploadService → ExcelParser → DataCleaner  │    │     │
│  │  │              → DataNormalizer               │    │     │
│  │  │              → SessionBuilder               │    │     │
│  │  └─────────────────────────────────────────────┘    │     │
│  │                                                       │     │
│  │  ┌─────────────────────────────────────────────┐    │     │
│  │  │ ChatService → AIAgent                       │    │     │
│  │  │           → QueryPlanner                    │    │     │
│  │  │           → SQL Generation (LLM)            │    │     │
│  │  │           → Answer Generation (LLM)         │    │     │
│  │  └─────────────────────────────────────────────┘    │     │
│  │                                                       │     │
│  │  ┌─────────────────────────────────────────────┐    │     │
│  │  │ ChartService → Plotly Config Generation    │    │     │
│  │  │            → Chart Rendering                │    │     │
│  │  └─────────────────────────────────────────────┘    │     │
│  │                                                       │     │
│  │  ┌─────────────────────────────────────────────┐    │     │
│  │  │ ReportService → PDFGenerator                │    │     │
│  │  │             → HTMLGenerator                 │    │     │
│  │  │             → ExcelExporter                 │    │     │
│  │  └─────────────────────────────────────────────┘    │     │
│  │                                                       │     │
│  │  ┌─────────────────────────────────────────────┐    │     │
│  │  │ AnalyticsService → Statistics               │    │     │
│  │  │               → Aggregations                 │    │     │
│  │  │               → Correlations                 │    │     │
│  │  └─────────────────────────────────────────────┘    │     │
│  │                                                       │     │
│  │  ┌─────────────────────────────────────────────┐    │     │
│  │  │ SessionService → Memory Management          │    │     │
│  │  │             → TTL Cleanup                    │    │     │
│  │  └─────────────────────────────────────────────┘    │     │
│  │                                                       │     │
│  │  ┌─────────────────────────────────────────────┐    │     │
│  │  │ VoiceService → Speech-to-Text               │    │     │
│  │  │           → Text-to-Speech                  │    │     │
│  │  └─────────────────────────────────────────────┘    │     │
│  └───────────────────────────────────────────────────────┘     │
│                           │                                     │
│  ┌────────────┬───────────┼──────────────┬────────────┐        │
│  │ AI Layer   │ Database  │ Schema Mgmt  │ Repository │        │
│  │            │ Layer     │              │            │        │
│  └────────────┴───────────┼──────────────┴────────────┘        │
└──────────────────────┬─────┴────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│   DuckDB     │ │   FAISS      │ │   File System    │
│  Analytics   │ │ Vector Index │ │  (Parquet/Data)  │
│  Database    │ │  (RAG/Search)│ │                  │
└──────────────┘ └──────────────┘ └──────────────────┘
        │
        └─────────────────┬─────────────────┐
                          │                 │
                    ┌─────▼────┐      ┌────▼────┐
                    │  Ollama   │      │ OpenAI  │
                    │  (Local)  │      │ (Cloud) │
                    │ qwen2.5:7b│      │ (Future)│
                    │ nomic-text│      │         │
                    └───────────┘      └─────────┘
```

---

## 🔧 Component Details

### **1. Frontend (React)**
```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatBox.tsx (Input & messages)
│   │   ├── MessageList.tsx (Display messages)
│   │   └── ChatContext.tsx (State management)
│   ├── Upload/
│   │   ├── FileUploader.tsx
│   │   └── UploadProgress.tsx
│   ├── Analytics/
│   │   ├── Dashboard.tsx
│   │   └── StatisticsPanels.tsx
│   └── Charts/
│       └── ChartViewer.tsx (Plotly.js)
├── services/
│   ├── api.ts (Axios config)
│   ├── chatService.ts
│   ├── uploadService.ts
│   └── reportService.ts
├── hooks/
│   ├── useChat.ts
│   ├── useUpload.ts
│   └── useSession.ts
└── types/
    └── index.ts (TypeScript definitions)
```

### **2. API Layer (FastAPI)**
```
app/
├── api/
│   ├── router.py (Main router)
│   ├── dependencies.py (Dependency injection)
│   └── routes/
│       ├── upload.py → POST /api/v1/upload
│       ├── chat.py → POST /api/v1/chat
│       ├── chart.py → GET/POST /api/v1/chart
│       ├── report.py → POST /api/v1/report
│       ├── session.py → GET/DELETE /api/v1/session
│       ├── dashboard.py → GET /api/v1/dashboard
│       ├── analytics.py → GET /api/v1/analytics
│       ├── voice.py → POST /api/v1/voice
│       └── health.py → GET /api/v1/health
```

### **3. Service Layer (Business Logic)**
```
app/services/
├── upload_service.py (File upload pipeline)
├── chat_service.py (Question answering)
├── chart_service.py (Visualization config)
├── report_service.py (Report generation)
├── session_service.py (Session management)
├── analytics_service.py (Statistics)
├── dashboard_service.py (Dashboard data)
└── voice_service.py (Speech processing)
```

### **4. AI Layer**
```
app/ai/
├── llm.py → LLMService (qwen2.5:7b interface)
├── embeddings.py → EmbeddingService (nomic-embed-text)
├── agent.py → AIAgent (Orchestrator)
├── rag.py → RAGService (FAISS + context)
├── planner.py → QueryPlanner (Intent detection)
├── memory.py → ConversationMemory (History)
├── prompt_manager.py → System prompts
├── response_builder.py → Response formatting
├── nlp.py → NLP utilities
└── session_context.py → Session AI context
```

### **5. Database Layer**
```
app/database/
├── connection.py → DatabaseManager (Singleton)
├── duckdb_manager.py → DuckDB operations
├── schema_manager.py → Schema creation & SQL
├── metadata_store.py → Chat history & metadata
└── repositories/
    ├── duckdb_repository.py
    ├── metadata_repository.py
    ├── session_repository.py
    └── vector_repository.py
```

### **6. Data Processing**
```
app/excel/
├── parser.py → ExcelParser (Read .xlsx)
├── loader.py → ExcelLoader (Polars)
├── validator.py → ExcelValidator (Validation)
├── cleaner.py → DataCleaner (Data cleaning)
├── normalizer.py → DataNormalizer (Normalization)
├── parquet_converter.py → Parquet conversion
├── metadata.py → MetadataExtractor
└── session_builder.py → SessionBuilder
```

### **7. Tools System**
```
app/tools/
├── base_tool.py → BaseTool (Abstract)
├── chart_tool.py → ChartTool
├── sql_tool.py → SQLTool
├── statistics_tool.py → StatisticsTool
├── report_tool.py → ReportTool
├── export_tool.py → ExportTool
├── recommendation_tool.py → RecommendationTool
└── dashboard_tool.py → DashboardTool
```

---

## 🔄 End-to-End Data Flows

### **FLOW 1: File Upload & Processing**
```
┌─────────────────┐
│  User Selects   │
│  Excel File     │
└────────┬────────┘
         │
         ▼ (Form Data)
    ┌──────────────────┐
    │  Browser FormData │
    │  [file blob]     │
    └────────┬─────────┘
             │
             ▼ (HTTP POST)
    ┌────────────────────────────────────┐
    │  /api/v1/upload Endpoint           │
    │  ↓                                 │
    │  UploadService.upload()            │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 1: Validation               │
    │  ├─ Check file size (< 500MB)     │
    │  ├─ Check extension (.xlsx)        │
    │  ├─ Check MIME type               │
    │  └─ Scan for malware (optional)   │
    └────────┬─────────────────────────┘
             │ ✓
    ┌────────▼──────────────────────────┐
    │  Step 2: Save Upload              │
    │  ├─ Save to data/uploads/         │
    │  └─ Generate session_id           │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 3: Parse Excel              │
    │  ├─ Use Polars.read_excel()       │
    │  ├─ Extract all sheets            │
    │  ├─ Get column names & types      │
    │  └─ Calculate row/column counts   │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 4: Data Cleaning            │
    │  ├─ Handle missing values         │
    │  ├─ Remove duplicates             │
    │  ├─ Fix data types                │
    │  └─ Trim whitespace               │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 5: Data Normalization       │
    │  ├─ Standardize column names      │
    │  ├─ Normalize dates               │
    │  ├─ Convert numbers               │
    │  └─ Handle categorical data       │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 6: Metadata Extraction      │
    │  ├─ Detect data types             │
    │  ├─ Calculate statistics          │
    │  ├─ Identify key columns          │
    │  └─ Extract schema info           │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 7: Convert to Parquet       │
    │  ├─ Save to data/parquet/         │
    │  ├─ Compress data                 │
    │  └─ Generate metadata file        │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 8: Create DuckDB Views      │
    │  ├─ Create view for each sheet    │
    │  ├─ Name: session_XXX_SheetName   │
    │  ├─ Enable SQL queries            │
    │  └─ Index key columns             │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 9: RAG Indexing             │
    │  ├─ Embed schema (nomic-embed)    │
    │  ├─ Store in FAISS index          │
    │  ├─ Save metadata                 │
    │  └─ Enable semantic search        │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │  Step 10: Create Session          │
    │  ├─ Store session in memory       │
    │  ├─ Save metadata to DB           │
    │  ├─ Set TTL (2 hours)             │
    │  └─ Return session info           │
    └────────┬─────────────────────────┘
             │
             ▼ (HTTP 200 + JSON)
    ┌────────────────────────────────────┐
    │  Response to Client                │
    │  {                                 │
    │    session_id: "abc123",           │
    │    file_name: "Sales.xlsx",        │
    │    sheets: ["Sales", "Costs"],     │
    │    total_rows: 50000,              │
    │    total_columns: 12               │
    │  }                                 │
    └────────────────────────────────────┘
             │
             ▼
    ┌────────────────────────────────────┐
    │  Browser Updates UI                │
    │  - Show file name                  │
    │  - List available sheets           │
    │  - Enable chat input               │
    └────────────────────────────────────┘
```

### **FLOW 2: Chat Question → Answer (Core AI Flow)**
```
┌─────────────────────┐
│  User Types Question │
│  "Total sales by    │
│   category?"        │
└────────────┬────────┘
             │
             ▼ (HTTP POST /api/v1/chat)
    ┌───────────────────────────────────────────┐
    │  ChatService.ask()                        │
    │  Input:                                   │
    │  - session_id: "abc123"                   │
    │  - question: "Total sales by category?"   │
    │  - sheet_name: "Sales"                    │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  1. Get Session & Schema                  │
    │  ├─ Load session from memory              │
    │  ├─ Get sheet data                        │
    │  ├─ Extract column info                   │
    │  └─ Build schema context                  │
    │     "Columns: category, sales, date..."   │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  2. Get Previous Context                  │
    │  ├─ Load last 5 chat messages             │
    │  ├─ Get conversation history              │
    │  └─ Retrieve similar previous Q&As (RAG)  │
    │     from FAISS vector index               │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  3. Query Planner (LLM)                   │
    │  ├─ Analyze question                      │
    │  ├─ LLM generates:                        │
    │  │  {                                     │
    │  │    "needs_sql": true,                  │
    │  │    "needs_chart": true,                │
    │  │    "intent": "aggregation",            │
    │  │    "explanation": "Group by category"  │
    │  │  }                                     │
    │  └─ Decide next steps                     │
    └────────┬──────────────────────────────────┘
             │ (needs_sql=true, needs_chart=true)
    ┌────────▼──────────────────────────────────┐
    │  4. SQL Generation (LLM via AIAgent)      │
    │  ├─ Build prompt:                        │
    │  │  "You are SQL expert.                  │
    │  │   Table: session_abc123_Sales          │
    │  │   Columns: category, sales, date       │
    │  │   Question: Total sales by category?"  │
    │  │   Previous answers: ...                │
    │  │   Generate DuckDB SQL only."           │
    │  ├─ LLM (qwen2.5:7b) generates SQL:       │
    │  │  SELECT category,                      │
    │  │  SUM(sales) as total_sales             │
    │  │  FROM session_abc123_Sales             │
    │  │  GROUP BY category                     │
    │  │  ORDER BY total_sales DESC             │
    │  └─ Validate SQL output                   │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  5. Execute SQL (DuckDB)                  │
    │  ├─ Run SQL query                         │
    │  ├─ Get results:                          │
    │  │  category    | total_sales             │
    │  │  Electronics | 45000                   │
    │  │  Clothing    | 32000                   │
    │  │  Home        | 28000                   │
    │  └─ Return result set (JSON)              │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  6. Answer Generation (LLM)               │
    │  ├─ Build prompt:                         │
    │  │  "Convert SQL results to answer:       │
    │  │   Question: Total sales by category?   │
    │  │   SQL: SELECT category, SUM(sales)...  │
    │  │   Results: [...]                       │
    │  │   Generate natural language answer."   │
    │  ├─ LLM generates:                        │
    │  │  "Total sales by category shows:       │
    │  │   Electronics leads with $45,000,      │
    │  │   followed by Clothing at $32,000,     │
    │  │   and Home & Garden at $28,000."       │
    │  └─ Format as response text               │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  7. Chart Generation (LLM)                │
    │  ├─ Build prompt:                         │
    │  │  "Generate Plotly config for:          │
    │  │   Question: Total sales by category?   │
    │  │   Data: [Electronics: 45000, ...]      │
    │  │   Suggest chart type"                  │
    │  ├─ LLM generates config:                 │
    │  │  {                                     │
    │  │    "type": "bar",                      │
    │  │    "x": ["Electronics", "Clothing"],   │
    │  │    "y": [45000, 32000],                │
    │  │    "title": "Sales by Category"        │
    │  │  }                                     │
    │  └─ Return chart config                   │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  8. Save to Chat History                  │
    │  ├─ Save question to metadata store       │
    │  ├─ Save answer                           │
    │  ├─ Save SQL query                        │
    │  ├─ Save chart config                     │
    │  └─ Index for future RAG retrieval        │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼──────────────────────────────────┐
    │  9. Build Response                        │
    │  {                                        │
    │    "answer": "Total sales by category...", │
    │    "sql_query": "SELECT category...",      │
    │    "chart_config": {type:"bar"...},        │
    │    "sources": ["previous_similar_Q&A"]    │
    │  }                                        │
    └────────┬──────────────────────────────────┘
             │
             ▼ (HTTP 200 + JSON)
    ┌───────────────────────────────────────────┐
    │  Response Sent to Browser                 │
    └────────┬──────────────────────────────────┘
             │
    ┌────────▼───────────────────────────────────┐
    │  Browser Updates UI                        │
    │  ├─ Display answer text                    │
    │  ├─ Show SQL in collapsible section        │
    │  ├─ Render chart using Plotly.js           │
    │  └─ Add message to conversation history    │
    └────────────────────────────────────────────┘
```

### **FLOW 3: Report Generation**
```
User Requests Report
        │
        ▼
    ReportService.generate()
        │
        ├─ Collect all analyses
        ├─ Compile chat history
        ├─ Generate summary statistics
        └─ Create visualizations
        │
        ├─ PDF Format: Use ReportLab
        ├─ HTML Format: Use Jinja2 templates
        └─ Excel Format: Use openpyxl
        │
        ▼
    Save to data/reports/
        │
        ▼
    Return download URL
```

### **FLOW 4: Export Data**
```
User Requests Export
        │
        ▼
    ExportService.export()
        │
        ├─ Format: Parquet/Excel/CSV
        ├─ Include metadata
        ├─ Compress if needed
        └─ Generate download
        │
        ▼
    File returned to browser
```

---

## 🔌 API Endpoints

### **Health & Info**
```
GET  /api/v1/health
     Response: {status: "healthy", version: "2.0.0"}

GET  /docs
     → Interactive Swagger UI documentation
```

### **Upload Routes**
```
POST /api/v1/upload
     Body: FormData with file
     Response: {session_id, file_name, sheets, total_rows, columns}

GET  /api/v1/upload/status/{session_id}
     Response: Upload progress and status
```

### **Chat Routes**
```
POST /api/v1/chat
     Body: {
       session_id: string,
       question: string,
       sheet_name?: string
     }
     Response: {
       answer: string,
       sql_query?: string,
       chart_config?: object,
       sources?: string[]
     }

GET  /api/v1/chat/history/{session_id}
     Response: [{question, answer, timestamp}, ...]
```

### **Chart Routes**
```
GET  /api/v1/chart/{session_id}
     Response: List of generated charts

POST /api/v1/chart/generate
     Body: {session_id, question}
     Response: {chart_config}

GET  /api/v1/chart/{session_id}/{chart_id}
     Response: Specific chart config
```

### **Report Routes**
```
POST /api/v1/report/generate
     Body: {session_id, format: "pdf|html|xlsx"}
     Response: {report_url, file_name}

GET  /api/v1/report/{report_id}
     Response: Report file (download)
```

### **Session Routes**
```
GET  /api/v1/session/{session_id}
     Response: Session metadata and info

DELETE /api/v1/session/{session_id}
       Response: {success: true}

GET  /api/v1/session
     Response: List of active sessions
```

### **Analytics Routes**
```
GET  /api/v1/analytics/{session_id}/{sheet_name}
     Response: Statistics, distributions, correlations

POST /api/v1/analytics/summary
     Body: {session_id}
     Response: Executive summary statistics
```

### **Dashboard Routes**
```
GET  /api/v1/dashboard/{session_id}
     Response: Dashboard data (charts, metrics, stats)
```

### **Voice Routes**
```
POST /api/v1/voice/transcribe
     Body: FormData with audio file
     Response: {text: "transcribed text"}

POST /api/v1/voice/synthesize
     Body: {text: string}
     Response: Audio file (mp3)
```

---

## 💾 Database Schema

### **DuckDB Views (Per Session)**
```sql
-- Created for each uploaded sheet
CREATE VIEW session_{SESSION_ID}_{SHEET_NAME} AS
SELECT 
    column1 TYPE,
    column2 TYPE,
    ...
FROM parquet('data/parquet/{SESSION_ID}_{SHEET_NAME}.parquet')

-- Indexes on frequently queried columns
CREATE INDEX idx_session_{SESSION_ID}_{COLUMN} 
ON session_{SESSION_ID}_{SHEET_NAME}(COLUMN)
```

### **Metadata Store (SQLite or DuckDB)**
```sql
-- Sessions table
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    file_name TEXT,
    upload_time TIMESTAMP,
    last_accessed TIMESTAMP,
    total_sheets INTEGER,
    metadata JSON
)

-- Chat history
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    question TEXT,
    answer TEXT,
    sql_query TEXT,
    chart_config JSON,
    timestamp TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
)

-- Vector embeddings (FAISS)
CREATE TABLE embeddings (
    id INTEGER PRIMARY KEY,
    session_id TEXT,
    text TEXT,
    embedding VECTOR(768),  -- nomic-embed-text dimension
    timestamp TIMESTAMP
)
```

### **FAISS Index Structure**
```
FAISS Index (Flat L2)
├── Dimension: 768 (nomic-embed-text)
├── Index Type: Flat (Exact similarity)
├── Metric: L2 distance
└── Data:
    ├── Workbook schemas
    ├── Question embeddings
    ├── Previous answers
    └── Metadata (session_id, type, timestamp)
```

---

## 🧠 AI Integration

### **LLM Service (qwen2.5:7b)**
```python
# Models: qwen2.5:7b (7 billion parameters)
# Provider: Ollama (local, offline)
# Connection: http://localhost:11434

# Used for:
1. SQL Generation - Convert NL to SQL
2. Answer Generation - Convert results to NL
3. Chart Generation - Create visualization configs
4. Intent Detection - Classify question type
5. JSON Extraction - Parse structured outputs

# Configuration:
Temperature: 0.1  # Low = consistent, factual
Max Tokens: 4096  # Max response length
Timeout: 1s       # Fast fallback to demo mode
```

### **Embedding Service (nomic-embed-text)**
```python
# Model: nomic-embed-text
# Dimension: 768
# Provider: Ollama
# Connection: http://localhost:11434

# Used for:
1. Schema Embedding - Encode workbook schemas
2. Query Embedding - Encode user questions
3. Document Embedding - Embed previous Q&As
4. Semantic Search - Find similar queries

# Index: FAISS with Flat L2 distance
```

### **RAG (Retrieval-Augmented Generation)**
```
1. User asks question
   │
   ▼
2. Embed question with nomic-embed-text
   │
   ▼
3. Search FAISS index for similar documents (k=3)
   │
   ▼
4. Get top-3 most similar previous Q&As
   │
   ▼
5. Include as context in LLM prompt
   │
   ▼
6. LLM generates answer with better context
```

---

## 🚀 Deployment Architecture

### **Development Setup**
```
Local Machine:
  ├─ Frontend (React) → http://localhost:5173
  ├─ Backend (FastAPI) → http://localhost:8000
  ├─ Ollama (Local LLM) → http://localhost:11434
  ├─ DuckDB (File) → data/databases/analytics.db
  └─ FAISS (File) → data/indexes/
```

### **Production Setup**
```
Server:
  ├─ Frontend (React SPA)
  │  ├─ Built with Vite → Optimized bundle
  │  ├─ Served via Nginx → Static files
  │  └─ CDN (Optional) → Global distribution
  │
  ├─ Backend (FastAPI)
  │  ├─ Uvicorn (ASGI server)
  │  ├─ Gunicorn (Process manager) → 4+ workers
  │  ├─ Nginx (Reverse proxy) → Load balancing
  │  └─ SSL/TLS → Encrypted connections
  │
  ├─ Database (DuckDB)
  │  ├─ File path: /data/databases/
  │  ├─ Backups: Automated daily
  │  └─ Replication: Optional
  │
  ├─ Vector DB (FAISS)
  │  ├─ Index file: /data/indexes/
  │  └─ Backups: Daily
  │
  ├─ AI Service (Ollama)
  │  ├─ Local or Remote
  │  ├─ GPU Acceleration: Recommended
  │  └─ Resource Monitoring
  │
  └─ Storage
     ├─ Uploads: /data/uploads/
     ├─ Parquet: /data/parquet/
     ├─ Reports: /data/reports/
     └─ Temp: /data/temp/
```

### **Containerized Deployment (Docker)**
```yaml
version: '3.8'
services:
  frontend:
    image: ai-excel-frontend:latest
    ports:
      - "80:3000"
    environment:
      - REACT_APP_API_URL=http://backend:8000

  backend:
    image: ai-excel-backend:latest
    ports:
      - "8000:8000"
    environment:
      - OLLAMA_URL=http://ollama:11434
      - DATABASE_PATH=/data/databases/
    volumes:
      - ./data:/data
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0:11434

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=analytics
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  ollama_models:
  postgres_data:
```

### **Scaling Strategy**
```
1. Frontend Scaling
   - Static files cached via CDN
   - Geographic distribution
   - No backend calls needed

2. Backend Scaling
   - Horizontal scaling: Multiple Uvicorn instances
   - Load balancing: Nginx round-robin
   - Session storage: Redis (optional)

3. Database Scaling
   - DuckDB: Single file or read replicas
   - Metadata: PostgreSQL for distributed data
   - FAISS: Distributed index sharding (future)

4. AI Service Scaling
   - Multiple Ollama instances
   - Load balancing across GPUs
   - Model caching and warm-start
```

---

## 📊 Request/Response Examples

### **Example 1: File Upload**
```json
Request:
POST /api/v1/upload
Content-Type: multipart/form-data
[Binary file data]

Response (200):
{
  "session_id": "sess_5f8d9e2c7a1b4c3d",
  "file_name": "Sales_Q1_2024.xlsx",
  "sheets": ["Sales", "Costs", "Forecast"],
  "total_rows": 150000,
  "total_columns": 15,
  "upload_timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "date_columns": ["Date", "Timestamp"],
    "numeric_columns": ["Sales", "Units", "Cost"],
    "string_columns": ["Category", "Region", "Product"]
  }
}
```

### **Example 2: Chat Question**
```json
Request:
POST /api/v1/chat
Content-Type: application/json
{
  "session_id": "sess_5f8d9e2c7a1b4c3d",
  "question": "What are the top 5 products by revenue?",
  "sheet_name": "Sales"
}

Response (200):
{
  "answer": "The top 5 products by revenue are: 1) Laptop ($2.5M), 2) Smartphone ($1.8M), 3) Tablet ($1.2M), 4) Monitor ($890K), 5) Keyboard ($560K). Together they account for $6.95M or 78% of total revenue.",
  "sql_query": "SELECT product, SUM(sales) as revenue FROM session_5f8d9e2c7a1b4c3d_Sales GROUP BY product ORDER BY revenue DESC LIMIT 5",
  "chart_config": {
    "type": "bar",
    "title": "Top 5 Products by Revenue",
    "x": ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard"],
    "y": [2500000, 1800000, 1200000, 890000, 560000],
    "x_label": "Product",
    "y_label": "Revenue ($)"
  },
  "sources": ["previous_Q&A_similar_to_top_products"]
}
```

### **Example 3: Report Generation**
```json
Request:
POST /api/v1/report/generate
Content-Type: application/json
{
  "session_id": "sess_5f8d9e2c7a1b4c3d",
  "format": "pdf"
}

Response (200):
{
  "report_id": "rpt_abc123xyz",
  "file_name": "Sales_Report_2024.pdf",
  "format": "pdf",
  "file_size": 2500000,
  "download_url": "/api/v1/report/rpt_abc123xyz/download",
  "created_at": "2024-01-15T10:35:00Z",
  "expires_at": "2024-01-22T10:35:00Z"
}
```

---

## 🔐 Security Measures

### **Input Validation**
- File type checking (only .xlsx)
- File size limits (500MB max)
- SQL injection prevention (parameterized queries)
- XSS protection (input sanitization)

### **Authentication (Optional)**
- API key validation (via headers)
- JWT tokens (future)
- Rate limiting (per IP/session)

### **Data Protection**
- Session TTL (2 hours default)
- Automatic session cleanup
- Secure file deletion after processing
- Encrypted storage (optional)

### **CORS Policy**
- Allowed origins: http://localhost:5173 (dev)
- Allowed methods: GET, POST, DELETE, OPTIONS
- Allowed headers: Content-Type, Authorization

---

## 📈 Performance Characteristics

| Operation | Time | Throughput |
|-----------|------|-----------|
| File Upload (100MB) | 2-5s | Depends on connection |
| File Processing | 5-10s | Depends on rows/columns |
| SQL Execution | 100-500ms | Depends on query complexity |
| LLM Query | 1-2s | Temperature 0.1 for consistency |
| Report Generation | 5-15s | Depends on format & data |
| Chat Response (end-to-end) | 3-5s | LLM + SQL + formatting |

---

## 🎓 Key Architectural Decisions

### **Why DuckDB?**
- In-process SQL engine
- No server setup needed
- Excellent performance for analytics
- Columnar storage (Parquet native)

### **Why FAISS?**
- Fast similarity search
- No external service needed
- Embedded in Python code
- Flat index for exact results

### **Why Ollama?**
- Local LLM (privacy-first)
- No API keys needed
- Offline capability
- Easy model switching

### **Why Polars?**
- Fast DataFrame operations
- Memory efficient
- Modern Python API
- Strong type safety

### **Why FastAPI?**
- Modern async support
- Automatic API documentation
- Type safety with Pydantic
- High performance

---

## 📚 Full Data Pipeline Summary

```
Excel File
    ↓ (Upload)
Polars DataFrame
    ↓ (Clean & Normalize)
Cleaned DataFrame
    ↓ (Convert)
Parquet Format
    ↓ (Index)
DuckDB View + FAISS Vector Index
    ↓ (Query)
User Question (NL)
    ↓ (Embed & RAG)
Context + Similar Examples
    ↓ (LLM)
SQL Query + Answer + Chart Config
    ↓ (Execute & Render)
User Response with Visualization
```

---

This comprehensive document covers the complete architecture, technology stack, data flows, and integration details of the AI Excel Analytics Platform!
