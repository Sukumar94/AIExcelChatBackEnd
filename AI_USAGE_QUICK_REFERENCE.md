# 🤖 AI USAGE - Quick Reference

## 📍 Where AI is Used in the Application

### **1️⃣ CHAT FEATURE** (app/services/chat_service.py)
**What**: Answer questions about Excel data  
**AI Used**: LLMService (qwen2.5:7b)  
**Purpose**: Convert natural language → SQL → Results → Natural language answer  

### **2️⃣ SQL GENERATION** (app/ai/agent.py → _generate_sql)
**What**: Create SQL queries from user questions  
**AI Used**: LLMService (qwen2.5:7b)  
**Purpose**: "Show me total sales" → SELECT SUM(sales) FROM data  

### **3️⃣ CHART GENERATION** (app/ai/agent.py → _generate_chart_config)
**What**: Create visualization configurations  
**AI Used**: LLMService (qwen2.5:7b)  
**Purpose**: Generate Plotly chart configs based on data and intent  

### **4️⃣ SEMANTIC SEARCH / RAG** (app/ai/rag.py)
**What**: Find relevant previous questions and workbook context  
**AI Used**: EmbeddingService (nomic-embed-text)  
**Purpose**: Give LLM context about similar previous queries  

### **5️⃣ ANSWER GENERATION** (app/ai/agent.py → _generate_answer_from_results)
**What**: Create natural language answers from SQL results  
**AI Used**: LLMService (qwen2.5:7b)  
**Purpose**: Convert numbers/data into human-readable explanations  

### **6️⃣ QUESTION ANALYSIS** (app/ai/planner.py)
**What**: Understand what user is asking  
**AI Used**: LLMService (qwen2.5:7b)  
**Purpose**: Determine if SQL needed, if chart needed, what intent is  

### **7️⃣ CONVERSATION CONTEXT** (app/ai/memory.py + session_context.py)
**What**: Maintain conversation history  
**AI Used**: LLMService receives previous messages  
**Purpose**: Enable multi-turn conversations with continuity  

---

## 🧠 AI Models Used

| Model | Purpose | Provider | Size | Used For |
|-------|---------|----------|------|----------|
| **qwen2.5:7b** | Chat & inference | Ollama | 7B params | SQL, answers, charts, planning |
| **nomic-embed-text** | Embeddings | Ollama | - | RAG retrieval, semantic search |

---

## 🔄 Data Flow: User Question → Answer

```
User: "What is total sales?"
           │
           ▼ (LLM analyzes via QueryPlanner)
        Understand question
           │
           ▼ (RAG retrieves similar questions)
        Get context
           │
           ▼ (LLM generates via AIAgent)
        CREATE SQL: SELECT SUM(sales)
           │
           ▼ (DuckDB executes)
        Results: 45000
           │
           ▼ (LLM generates answer)
        "Total sales are $45,000"
           │
           ▼ (LLM generates chart)
        Chart config: pie/bar/line
           │
           ▼
        Return to user
```

---

## 📁 Key AI Files

```
app/ai/
├── llm.py                 # LLM Service (qwen2.5:7b)
├── embeddings.py          # Embedding Service (nomic-embed-text)
├── agent.py               # AIAgent (orchestrator)
├── rag.py                 # RAG Service (FAISS + context retrieval)
├── planner.py             # QueryPlanner (question analysis)
├── memory.py              # ConversationMemory (history tracking)
├── prompt_manager.py      # System prompts & templates
├── response_builder.py    # Response formatting
├── nlp.py                 # NLP utilities (non-LLM)
└── session_context.py     # Session AI context
```

---

## ⚙️ Configuration

### **Models**
```python
# app/core/config.py
llm_model = "qwen2.5:7b"
embedding_model = "nomic-embed-text"
ollama_url = "http://localhost:11434"
```

### **Parameters**
```python
temperature = 0.1         # Low = consistent, factual
max_tokens = 4096         # Max response length
embedding_dim = 768       # nomic-embed-text output size
rag_top_k = 3             # Retrieve top-3 similar docs
max_history = 10          # Keep last 10 messages
```

---

## 🎯 AI Usage by Service

| Service | AI Used? | For What |
|---------|----------|----------|
| Chat Service | ✅ Yes | Answer questions |
| Upload Service | ❌ No | File processing |
| Report Service | ❌ No | Report generation |
| Export Service | ❌ No | Data export |
| Dashboard Service | ❌ No | Dashboard rendering |
| Analytics Service | ❌ No | Analytics computation |
| Voice Service | ❌ No | Audio processing |

---

## 🚀 External Service

**Ollama** (http://localhost:11434)
- Provides LLM models
- Provides embedding models
- Must be running for full AI capability
- Falls back to demo mode if unavailable

---

## 💡 Key AI Capabilities

### ✅ What AI Can Do
- Understand natural language questions about data
- Generate accurate SQL queries
- Create appropriate visualizations
- Provide contextual answers
- Maintain conversation history
- Learn from previous queries (RAG)

### ❌ What AI Cannot Do
- Modify Excel files directly
- Run arbitrary code
- Access external databases
- Generate images/audio
- Delete or corrupt data

---

## 🔍 AI Usage Locations (Code)

**In Chat Flow:**
1. `app/services/chat_service.py` → Receives user question
2. `app/ai/planner.py` → LLM analyzes question type
3. `app/ai/rag.py` → Retrieves relevant context
4. `app/ai/agent.py` → LLM generates SQL
5. `app/database/` → Executes SQL
6. `app/ai/agent.py` → LLM generates answer & chart
7. `app/ai/response_builder.py` → Formats response

**Direct LLM Calls:**
- `LLMService.chat()` - Multi-turn chat
- `LLMService.ask()` - Single question
- `LLMService.extract_json()` - Structured output

**Embedding Calls:**
- `EmbeddingService.embed()` - Single text
- `EmbeddingService.embed_batch()` - Multiple texts

**RAG Operations:**
- `RAGService.add_workbook_context()` - Index schemas
- `RAGService.add_query_history()` - Store Q&As
- `RAGService.retrieve()` - Find similar docs

---

## 📊 Performance

| Operation | Time |
|-----------|------|
| Embedding | ~100ms |
| SQL generation | ~500ms-1s |
| SQL execution | ~100-500ms |
| Answer generation | ~500ms-1s |
| Chart generation | ~300-500ms |
| **Total per question** | **~2-4 seconds** |

---

## 🎓 Example: "What is our best selling product?"

```python
# 1. Question received
question = "What is our best selling product?"

# 2. QueryPlanner analyzes (LLM)
→ intent: "extreme" (find maximum)
→ needs_sql: True
→ needs_chart: True

# 3. RAG retrieves context
→ Similar Q: "Top product by sales"
→ Schema: columns=[product, sales]

# 4. AIAgent generates SQL (LLM)
SELECT product, SUM(sales) as total_sales
FROM orders
GROUP BY product
ORDER BY total_sales DESC
LIMIT 1

# 5. DuckDB executes
→ Results: {"product": "Laptop", "total_sales": 250000}

# 6. AIAgent generates answer (LLM)
→ "Our best selling product is Laptop with $250,000 in sales"

# 7. AIAgent generates chart (LLM)
→ Config: pie chart / bar chart with top 5 products

# 8. Response sent to user
{
  "answer": "Our best selling product is Laptop...",
  "sql_query": "SELECT product...",
  "chart_config": {...},
  "sources": ["previous_Q&A"]
}
```

---

## 🔗 Full Documentation

For complete details, see: **AI_COMPONENTS_DETAILED.md**

