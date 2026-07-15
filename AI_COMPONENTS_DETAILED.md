# 🤖 AI COMPONENTS IN APPLICATION - Complete Overview

## 📊 Summary: Where AI is Used & What For

This document maps all AI/LLM integration points in the AI Excel Chat Platform.

---

## 🏗️ AI Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER QUESTION                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │     QUERY PLANNER (QueryPlanner)        │
        │  - Analyzes question type               │
        │  - Determines if SQL/chart needed       │
        │  - Uses LLM for question understanding  │
        └──────────────┬──────────────────────────┘
                       │
        ┌──────────────┴──────────────────────────┐
        │                                          │
        ▼                                          ▼
   ┌─────────────────────┐          ┌───────────────────────┐
   │   AI AGENT          │          │  RAG SERVICE          │
   │ (AIAgent)           │          │ (Retrieval-Augmented) │
   │                     │          │                       │
   │ 1. SQL Generation   │◄─────────│ - Semantic Search     │
   │    (via LLM)        │          │ - Previous Q&A        │
   │                     │          │ - Schema Context      │
   │ 2. Answer Generation│          │                       │
   │    (via LLM)        │          │ Uses: Embeddings      │
   │                     │          │ (via EmbeddingService)│
   │ 3. Chart Config Gen │          └───────────────────────┘
   │    (via LLM)        │
   │                     │
   └────────┬────────────┘
            │
    ┌───────┴────────────────┐
    │                         │
    ▼                         ▼
┌──────────────────┐  ┌──────────────────┐
│  SQL EXECUTION   │  │  CHART CONFIG    │
│ (DuckDB)         │  │  (LLM Generated) │
│                  │  │                  │
│ Returns: Results │  │  Returns: Config │
└────────┬─────────┘  └──────────────────┘
         │
         ▼
   ┌─────────────────────┐
   │ NL ANSWER RESPONSE  │
   │ (From LLM)          │
   │                     │
   │ User-friendly text  │
   │ + SQL Query         │
   │ + Chart Config      │
   └─────────────────────┘
```

---

## 🧠 1. LLM SERVICE (app/ai/llm.py)

### **Purpose**
Main Language Model wrapper - connects to local Ollama for AI inference

### **Models Used**
- **Primary**: `qwen2.5:7b` - 7 billion parameter chat model
- **Backup**: Demo mode with pattern matching when Ollama unavailable

### **Key Features**
✅ Chat completions (multi-turn conversations)  
✅ Single-turn prompts (simple Q&A)  
✅ JSON extraction (structured output parsing)  
✅ Fallback/demo mode for development  

### **Used By**
- AIAgent (SQL generation, answer generation, chart generation)
- QueryPlanner (question analysis)
- Session context management
- Chat service

### **Configuration**
```python
LLM_MODEL = "qwen2.5:7b"
OLLAMA_URL = "http://localhost:11434"
TEMPERATURE = 0.1  # Low for consistency
MAX_TOKENS = 4096
```

---

## 🔗 2. EMBEDDING SERVICE (app/ai/embeddings.py)

### **Purpose**
Generate vector embeddings for semantic search and RAG retrieval

### **Models Used**
- **Primary**: `nomic-embed-text` - 768-dimensional embeddings
- **Fallback**: Zero vectors when Ollama unavailable

### **Key Functions**
✅ `embed()` - Single text embedding  
✅ `embed_batch()` - Multiple texts at once  
✅ `embed_dataframe_context()` - Embed data summaries  

### **Used By**
- RAGService (document indexing and similarity search)
- Workbook context encoding
- Query history encoding

### **Configuration**
```python
EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_DIMENSION = 768  # nomic-embed-text output size
```

---

## 🎯 3. QUERY PLANNER (app/ai/planner.py)

### **Purpose**
Analyze user questions to determine the best response strategy

### **AI Analysis Performed**
- Question type classification
- Intent detection
- Whether SQL is needed
- Whether chart visualization is needed

### **Output Format**
```json
{
  "needs_sql": true/false,
  "needs_chart": true/false,
  "intent": "summary|analysis|comparison|trend|distribution|general",
  "explanation": "brief explanation"
}
```

### **Used By**
- Chat service (to route to correct handler)

---

## 🤖 4. AI AGENT (app/ai/agent.py)

### **Purpose**
Orchestrates the complete AI workflow for answering user questions

### **Multi-Step Process**
1. **Question Understanding** (via LLM)
   - Analyze what user is asking
   - Identify key concepts and entities

2. **SQL Generation** (via LLM)
   - Convert natural language to DuckDB SQL
   - Uses schema context and RAG context
   - Respects conversation history

3. **SQL Execution** (DuckDB)
   - Runs generated SQL against uploaded data
   - Handles errors gracefully

4. **Answer Generation** (via LLM)
   - Creates natural language response
   - References specific numbers from results
   - Summarizes findings

5. **Chart Configuration** (via LLM)
   - Generates Plotly chart config
   - Suggests appropriate visualization type
   - Based on data characteristics

### **Methods**
- `process()` - Main entry point
- `_generate_sql()` - LLM-based SQL generation
- `_generate_answer_from_results()` - Convert SQL results to natural language
- `_generate_chart_config()` - Create visualization config

### **Used By**
- Chat service (question answering)

---

## 📚 5. RAG SERVICE (app/ai/rag.py)

### **Purpose**
Retrieval-Augmented Generation - provides context to LLM queries

### **Components**
- **Vector Index**: FAISS (Facebook AI Similarity Search)
- **Embedder**: EmbeddingService (768-dim vectors)
- **Storage**: Pickle files in `data/indexes/`

### **Stored Context**
1. **Workbook Schemas**
   - Table structures
   - Column definitions
   - Data types

2. **Query History**
   - Previous questions asked
   - Their SQL queries
   - Results returned

3. **Document Metadata**
   - Session IDs
   - Sheet names
   - Timestamps

### **Methods**
- `add_workbook_context()` - Index sheet schemas
- `add_query_history()` - Store Q&A pairs
- `retrieve()` - Find similar documents
- `get_relevant_context()` - Format context for LLM

### **Retrieval Process**
```
User Question
     │
     ▼
Generate Embedding (EmbeddingService)
     │
     ▼
FAISS Similarity Search (top-3 matches)
     │
     ▼
Filter by Session ID
     │
     ▼
Format as Text Context
     │
     ▼
Pass to LLM Prompt
```

### **Used By**
- AIAgent (as context for SQL/answer generation)

---

## 💬 6. CONVERSATION MEMORY (app/ai/memory.py)

### **Purpose**
Maintain conversation history per session for multi-turn chat

### **Features**
✅ Per-session history storage  
✅ Configurable max history (default: 10 messages)  
✅ Role tracking (user/assistant)  
✅ Formatted output for LLM context  

### **Storage Structure**
```python
{
  "session_123": [
    {"role": "user", "content": "What is total sales?"},
    {"role": "assistant", "content": "Total sales are $..."}
  ]
}
```

### **Used By**
- SessionContext (AI context management)
- Chat service (maintaining conversation flow)

---

## 📝 7. PROMPT MANAGER (app/ai/prompt_manager.py)

### **Purpose**
Templates and system prompts for consistent LLM behavior

### **System Prompt**
Defines AI assistant role:
- Data analyst assistant
- Based on uploaded workbook data
- Provides SQL generation, charting, statistics

### **Prompt Templates**
- SQL generation prompts
- Answer generation prompts
- Chart config generation prompts
- JSON extraction prompts

### **Used By**
- LLMService (system prompts for chat)
- AIAgent (SQL/answer generation prompts)

---

## 🗣️ 8. NLP UTILITIES (app/ai/nlp.py)

### **Purpose**
Natural Language Processing helpers (non-LLM)

### **Functions**
1. **extract_keywords()** - Remove stop words, extract important terms
2. **detect_question_type()** - Classify question:
   - Count (how many, how much)
   - Factual (what is)
   - Retrieval (show, list, find)
   - Comparison (compare, versus)
   - Trend (over time, change)
   - Aggregation (sum, average)
   - Extreme (highest, lowest)
   - Visualization (chart, graph)

### **Used By**
- Query analysis
- Question type detection
- Intent-based routing

---

## 🎨 9. RESPONSE BUILDER (app/ai/response_builder.py)

### **Purpose**
Format AI outputs into standardized API responses

### **Response Structure**
```json
{
  "answer": "Natural language response from LLM",
  "sql_query": "Generated SQL query used",
  "chart_config": {"type": "bar", "data": {...}},
  "sources": ["sheet_name", "previous_qa"]
}
```

### **Used By**
- Chat service (API response formatting)

---

## 🔄 10. SESSION CONTEXT (app/ai/session_context.py)

### **Purpose**
Manage AI context per user session

### **Context Includes**
- File name and metadata
- Sheet names and structure
- Conversation history
- User and assistant messages

### **Used By**
- Chat service (session-specific AI processing)

---

## 🛠️ COMPLETE WORKFLOW: User Question to Answer

### **Step-by-Step Process**

```
1. USER UPLOADS EXCEL
   │
   ├─ Sheet metadata extracted
   ├─ Schema context created
   └─ RAG indexed (schemas stored)

2. USER ASKS QUESTION
   │
   ├─ Query Planner analyzes (LLM)
   ├─ Determines if SQL needed (LLM)
   └─ Checks if chart needed (LLM)

3. AI AGENT PROCESSES
   │
   ├─ RAG retrieves relevant context
   │  └─ Previous Q&As similar to current
   │  └─ Workbook schema information
   │
   ├─ Generate SQL (LLM)
   │  ├─ Input: question + schema + history
   │  ├─ Output: DuckDB SQL query
   │  └─ Embedded in natural context
   │
   ├─ Execute SQL (DuckDB)
   │  └─ Get results from workbook data
   │
   ├─ Generate Answer (LLM)
   │  ├─ Input: question + results + context
   │  ├─ Output: Natural language summary
   │  └─ References specific numbers
   │
   └─ Generate Chart (LLM)
      ├─ Input: data + question intent
      ├─ Output: Plotly configuration
      └─ Type: bar, line, scatter, etc.

4. RESPONSE RETURNED TO USER
   │
   ├─ Answer text
   ├─ SQL query (for transparency)
   ├─ Chart visualization
   └─ Sources (previous similar questions)

5. HISTORY RECORDED
   │
   ├─ Question stored in memory
   ├─ Answer stored in memory
   ├─ Q&A indexed in RAG
   └─ Available for future context
```

---

## 🎯 AI Usage by Feature

| Feature | AI Component | Purpose |
|---------|--------------|---------|
| **Chat** | AIAgent + LLM | Answer questions about data |
| **SQL Generation** | LLM + Planner | Convert natural language to SQL |
| **Chart Generation** | LLM | Create visualization configs |
| **Semantic Search** | Embeddings + RAG | Find similar previous questions |
| **Question Analysis** | QueryPlanner + NLP | Understand user intent |
| **Answer Formatting** | LLM | Create natural language responses |
| **Context Retrieval** | RAG + Embeddings | Find relevant workbook context |
| **Conversation Flow** | Memory + LLM | Maintain multi-turn chat history |

---

## 🔧 Configuration Files

### **Main Config** (app/core/config.py)
```python
llm_model = "qwen2.5:7b"
embedding_model = "nomic-embed-text"
ollama_url = "http://localhost:11434"
llm_temperature = 0.1
llm_max_tokens = 4096
faiss_path = "data/indexes"
```

### **Constants** (app/core/constants.py)
```python
DEFAULT_LLM_MODEL = "qwen2.5:7b"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_BASE_URL = "http://localhost:11434"
FAISS_INDEX_DIMENSION = 768
```

---

## 🚀 External Dependencies

### **AI Services**
- **Ollama** - Local LLM inference
  - Models: qwen2.5:7b, nomic-embed-text
  - URL: http://localhost:11434

### **Vector Search**
- **FAISS** - Similarity search
  - Library: facebook-ai-similarity-search
  - Index type: IndexFlatL2 (exact L2 distance)

### **Python Libraries**
- `ollama` - Client for Ollama
- `faiss` - Vector search index
- `numpy` - Numerical operations
- `httpx` - HTTP client for service checks

---

## 📊 Data Flow Diagram

```
Excel File Upload
       │
       ▼
┌──────────────────────────────────────────────┐
│ Schema Extraction & RAG Indexing             │
│ - Extract column names, types                │
│ - Embed schema (EmbeddingService)            │
│ - Store in FAISS index                       │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│ User Question Processing                     │
│ - Query Planner analyzes (LLM)               │
│ - Gets intent and strategy                   │
└────────────┬─────────────────────────────────┘
             │
      ┌──────┴──────────────────────────┐
      │                                  │
      ▼                                  ▼
┌──────────────────────┐    ┌──────────────────────┐
│ RAG Retrieval        │    │ LLM Processing       │
│ - Embed question     │    │ - SQL generation     │
│ - Search FAISS       │    │ - Answer generation  │
│ - Get context        │    │ - Chart generation   │
└──────────┬───────────┘    └──────────┬───────────┘
           │                           │
           └──────────┬────────────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │ SQL Execution         │
          │ (DuckDB)              │
          └───────────┬───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │ Response Formatting   │
          │ - Answer              │
          │ - SQL Query           │
          │ - Chart Config        │
          │ - Sources             │
          └───────────┬───────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │ Return to User        │
          └───────────────────────┘
```

---

## 🎓 Summary Table

| Component | AI Used | Purpose | Models |
|-----------|---------|---------|--------|
| LLMService | ✅ | Chat & inference | qwen2.5:7b |
| EmbeddingService | ✅ | Vector embeddings | nomic-embed-text |
| QueryPlanner | ✅ | Question analysis | qwen2.5:7b |
| AIAgent | ✅ | Main orchestrator | qwen2.5:7b |
| RAGService | ✅ | Context retrieval | nomic-embed-text |
| ConversationMemory | ❌ | History storage | N/A |
| PromptManager | ❌ | Template management | N/A |
| ResponseBuilder | ❌ | Response formatting | N/A |
| NLPUtils | ❌ | Basic text processing | N/A |
| SessionContext | ❌ | Session data | N/A |

---

## 🔑 Key AI Parameters

```python
# Temperature (creativity vs consistency)
TEMPERATURE = 0.1  # Low = consistent, factual
# Value: 0.0 = deterministic, 1.0 = creative

# Max tokens (output length)
MAX_TOKENS = 4096  # Max response length

# Embedding dimension
EMBEDDING_DIM = 768  # nomic-embed-text output

# RAG retrieval
TOP_K = 3  # Return top-3 similar documents
FAISS_TYPE = "Flat"  # Exact distance computation

# Conversation history
MAX_HISTORY = 10  # Keep last 10 messages
```

---

## 🎯 When Ollama is Unavailable

The system gracefully falls back to **DEMO MODE**:

✅ LLMService returns pattern-matched demo responses  
✅ EmbeddingService returns zero vectors  
✅ RAG still works (with zero vectors)  
✅ Basic Q&A still available  
✅ No SQL errors - just reduced AI capability  

This allows development without Ollama installed!

---

## 📈 Performance Notes

- **Embeddings**: ~100ms per text
- **SQL Generation**: ~500ms-1s
- **Answer Generation**: ~500ms-1s
- **Chart Generation**: ~300ms-500ms
- **Total**: ~2-4 seconds per question

Temperature 0.1 ensures consistency but may limit creativity.

