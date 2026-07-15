# 💻 PRACTICAL IMPLEMENTATION GUIDE WITH CODE EXAMPLES

## 🎯 How Everything Works Together - Real Examples

### **Example 1: Complete Upload → Chat → Export Flow**

#### **Step 1: Frontend - User Uploads File (React)**
```typescript
// components/Upload/FileUploader.tsx
import axios from 'axios';

const handleFileUpload = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await axios.post(
      'http://localhost:8000/api/v1/upload',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded / progressEvent.total) * 100);
          setProgress(percent);
        }
      }
    );

    const { session_id, sheets, file_name } = response.data;
    
    // Save session for future use
    setSession({ session_id, file_name, sheets });
    setMessage(`✓ Loaded ${file_name} with sheets: ${sheets.join(', ')}`);
  } catch (error) {
    setError(`Upload failed: ${error.message}`);
  }
};
```

#### **Step 2: Backend - Process Upload (Python/FastAPI)**
```python
# app/api/routes/upload.py
from fastapi import UploadFile, APIRouter
from app.services.upload_service import UploadService

router = APIRouter(prefix="/api/v1", tags=["upload"])
upload_service = UploadService()

@router.post("/upload")
async def upload_file(file: UploadFile) -> dict:
    """
    Process Excel upload:
    1. Validate
    2. Parse
    3. Clean
    4. Convert to Parquet
    5. Create DuckDB view
    6. Index for RAG
    """
    result = await upload_service.upload(file)
    return {
        "session_id": result["session_id"],
        "file_name": result["file_name"],
        "sheets": result["sheets"],
        "total_rows": result["total_rows"],
        "total_columns": result["total_columns"]
    }
```

#### **Step 3: Backend Service - Upload Processing**
```python
# app/services/upload_service.py
class UploadService:
    async def upload(self, file: UploadFile) -> dict[str, Any]:
        # 1. VALIDATE
        await ExcelValidator.validate(file)
        
        # 2. PARSE - Read Excel
        sheets = await ExcelParser.parse(file)
        # Result: {"Sales": DataFrame, "Costs": DataFrame, ...}
        
        # 3. CLEAN - Fix data issues
        cleaned_sheets = {}
        for name, df in sheets.items():
            df = DataCleaner.clean_dataframe(df)
            # Handles: missing values, duplicates, types
            cleaned_sheets[name] = df
        
        # 4. NORMALIZE - Standardize
        for name, df in cleaned_sheets.items():
            df = DataNormalizer.normalize_dataframe(df)
            # Standardizes: column names, dates, numbers
        
        # 5. CONVERT TO PARQUET - Store efficiently
        for name, df in cleaned_sheets.items():
            ParquetConverter.to_parquet(
                df,
                f"data/parquet/{session_id}_{name}.parquet"
            )
        
        # 6. CREATE DUCKDB VIEW - Enable SQL queries
        for sheet_name, df in cleaned_sheets.items():
            view_name = f"session_{session_id}_{sheet_name}"
            self.schema_manager.create_view(view_name, df)
            # Now can: SELECT * FROM session_abc123_Sales
        
        # 7. INDEX FOR RAG - Enable semantic search
        for sheet_name, df in cleaned_sheets.items():
            schema_text = f"Table: {sheet_name}\nColumns: {df.columns}"
            self.rag_service.add_workbook_context(
                session_id, 
                sheet_name, 
                schema_text
            )
        
        # 8. CREATE SESSION
        session = SessionService.create_session(
            file.filename,
            cleaned_sheets
        )
        
        return {
            "session_id": session.session_id,
            "file_name": file.filename,
            "sheets": list(cleaned_sheets.keys()),
            "total_rows": sum(df.height for df in cleaned_sheets.values()),
            "total_columns": sum(df.width for df in cleaned_sheets.values())
        }
```

---

### **Example 2: Chat - Question to Answer with AI**

#### **Step 1: Frontend - User Asks Question**
```typescript
// components/Chat/ChatBox.tsx
const handleSendMessage = async (message: string) => {
  const response = await axios.post(
    `http://localhost:8000/api/v1/chat`,
    {
      session_id: session.session_id,
      question: message,
      sheet_name: selectedSheet
    }
  );

  const { answer, sql_query, chart_config, sources } = response.data;
  
  // Add to chat history
  addMessage({
    role: 'user',
    content: message,
    timestamp: new Date()
  });
  
  // Add AI response
  addMessage({
    role: 'assistant',
    content: answer,
    sql_query,
    chart_config,
    sources,
    timestamp: new Date()
  });

  // Display chart if provided
  if (chart_config) {
    displayChart(chart_config);
  }
};
```

#### **Step 2: Backend - Chat Endpoint**
```python
# app/api/routes/chat.py
from app.services.chat_service import ChatService

@router.post("/chat")
async def chat(request: ChatRequest) -> dict:
    """
    Process chat message:
    1. Validate session
    2. Get schema context
    3. Call ChatService
    4. Return answer + SQL + chart
    """
    chat_service = ChatService()
    result = chat_service.ask(
        session_id=request.session_id,
        question=request.question,
        sheet_name=request.sheet_name
    )
    return result
```

#### **Step 3: ChatService - Orchestration**
```python
# app/services/chat_service.py
class ChatService:
    def ask(self, session_id: str, question: str, sheet_name: str) -> dict:
        # Get session & sheet
        session = SessionService.get_session(session_id)
        sheet = session.sheets[sheet_name]
        
        # Get schema context
        schema_context = self._build_schema_context(
            session_id,
            sheet_name,
            sheet
        )
        # Result: "Table: Sales\nColumns:\n- category: string\n- sales: float\n..."
        
        # Get chat history
        chat_history = self.metadata_store.get_chat_history(
            session_id,
            limit=5
        )
        
        # Process through AI Agent
        result = self.agent.process(
            question=question,
            schema_context=schema_context,
            sheet_name=sheet_name,
            session_id=session_id,
            chat_history=chat_history
        )
        
        # Save to history
        self.metadata_store.save_chat_message(
            session_id=session_id,
            question=question,
            answer=result.get("answer"),
            sql_query=result.get("sql_query"),
            chart_config=result.get("chart_config")
        )
        
        return result
```

#### **Step 4: AIAgent - Main Logic**
```python
# app/ai/agent.py
class AIAgent:
    def process(self, question: str, schema_context: str, sheet_name: str, 
                session_id: str, chat_history: list) -> dict:
        
        # 1. Get RAG context
        rag_context = self.rag.get_relevant_context(question, session_id)
        # Result: "Previous Q: 'Total sales?'\nAnswer: 'SELECT SUM(sales)...'\n..."
        
        # 2. Build chat history context
        history_context = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in chat_history[-5:]
        ])
        
        # 3. Generate SQL
        sql_query = self._generate_sql(
            question=question,
            schema_context=schema_context,
            sheet_name=sheet_name,
            session_id=session_id,
            history_context=history_context,
            rag_context=rag_context
        )
        
        # 4. Execute SQL
        results = self.schema_manager.execute_query(sql_query)
        
        # 5. Generate answer
        answer = self._generate_answer_from_results(
            question=question,
            sql_query=sql_query,
            results=results,
            row_count=len(results),
            schema_context=schema_context
        )
        
        # 6. Generate chart
        chart_config = self._generate_chart_config(
            question=question,
            results=results,
            schema_context=schema_context
        )
        
        return {
            "answer": answer,
            "sql_query": sql_query,
            "chart_config": chart_config
        }
```

#### **Step 5: SQL Generation (LLM)**
```python
# app/ai/agent.py
def _generate_sql(self, question: str, schema_context: str, 
                  sheet_name: str, session_id: str, 
                  history_context: str, rag_context: str) -> str:
    
    view_name = f"session_{session_id}_{sheet_name}"
    
    # Build prompt for LLM
    prompt = f"""You are an expert SQL analyst. Generate a DuckDB SQL query.

Table Name: {view_name}

Schema:
{schema_context}

Previous conversation:
{history_context}

Similar previous questions:
{rag_context}

Question: {question}

Generate ONLY the SQL query. No explanation, no markdown.
Rules:
1. Use {view_name} as table name
2. Use DuckDB syntax
3. Use GROUP BY with aggregations where appropriate
4. Use ORDER BY for sorting
5. Return ONLY the SQL, no explanation"""

    # Call LLM
    response = self.llm.ask(prompt)
    
    # Clean response
    sql_query = response.strip()
    sql_query = re.sub(r"```sql\s*", "", sql_query)
    sql_query = re.sub(r"```\s*", "", sql_query)
    
    return sql_query.strip()
    
    # Example output:
    # SELECT category, SUM(sales) as total_sales
    # FROM session_abc123_Sales
    # GROUP BY category
    # ORDER BY total_sales DESC
```

#### **Step 6: SQL Execution (DuckDB)**
```python
# app/database/schema_manager.py
def execute_query(self, query: str) -> list[dict]:
    """Execute SQL query and return results as dicts"""
    try:
        relation = self.db.execute(query)
        # Convert to list of dicts
        return relation.df().to_dicts()
        
        # Example result:
        # [
        #     {"category": "Electronics", "total_sales": 45000},
        #     {"category": "Clothing", "total_sales": 32000},
        #     {"category": "Home", "total_sales": 28000}
        # ]
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise
```

#### **Step 7: Answer Generation (LLM)**
```python
# app/ai/agent.py
def _generate_answer_from_results(self, question: str, sql_query: str,
                                  results: list[dict], row_count: int,
                                  schema_context: str) -> str:
    
    results_str = json.dumps(results[:10], indent=2, default=str)
    
    prompt = f"""You are a data analyst. Given a question, SQL query, and results,
provide a clear, concise natural language answer.

Question: {question}

SQL Query: {sql_query}

Results ({row_count} rows returned):
{results_str}

Provide a helpful answer. Include specific numbers from results.
If many rows, summarize key findings. Do NOT mention the SQL query."""

    response = self.llm.ask(prompt)
    
    return response
    
    # Example output:
    # "Based on the data analysis, total sales by category shows:
    #  Electronics leads with $45,000, followed by Clothing at $32,000,
    #  and Home & Garden at $28,000. Electronics accounts for 45% of
    #  total sales across all categories."
```

#### **Step 8: Chart Generation (LLM)**
```python
# app/ai/agent.py
def _generate_chart_config(self, question: str, results: list[dict],
                          schema_context: str) -> dict:
    
    results_str = json.dumps(results[:20], indent=2, default=str)
    
    prompt = f"""Generate a Plotly chart configuration for this data.

Question: {question}

Data ({len(results)} rows):
{results_str}

Return JSON only with these fields:
{{
    "type": "bar|line|pie|scatter|histogram",
    "title": "...",
    "x": [...],
    "y": [...],
    "x_label": "...",
    "y_label": "..."
}}"""

    response = self.llm.extract_json(prompt)
    
    return response
    
    # Example output:
    # {
    #     "type": "bar",
    #     "title": "Sales by Category",
    #     "x": ["Electronics", "Clothing", "Home"],
    #     "y": [45000, 32000, 28000],
    #     "x_label": "Category",
    #     "y_label": "Sales ($)"
    # }
```

#### **Step 9: Frontend - Display Results**
```typescript
// components/Chat/MessageList.tsx
const Message = ({ msg }: { msg: ChatMessage }) => {
  if (msg.role === 'user') {
    return <div className="user-message">{msg.content}</div>;
  }

  return (
    <div className="assistant-message">
      {/* Answer text */}
      <p className="answer">{msg.content}</p>

      {/* SQL query in collapsible */}
      {msg.sql_query && (
        <details>
          <summary>📊 SQL Used</summary>
          <pre><code>{msg.sql_query}</code></pre>
        </details>
      )}

      {/* Chart visualization */}
      {msg.chart_config && (
        <ChartViewer config={msg.chart_config} />
      )}

      {/* Sources */}
      {msg.sources?.length > 0 && (
        <div className="sources">
          Sources: {msg.sources.join(', ')}
        </div>
      )}
    </div>
  );
};
```

---

### **Example 3: RAG (Retrieval-Augmented Generation)**

#### **How Previous Questions Help**
```python
# app/ai/rag.py
class RAGService:
    def get_relevant_context(self, query: str, session_id: str, k: int = 3) -> str:
        """
        1. Embed the new question
        2. Search for similar previous questions
        3. Return them as context for LLM
        """
        
        # 1. Generate embedding for current question
        query_embedding = self.embedder.embed(query)
        # Result: [0.234, -0.156, 0.891, ...] (768 dimensions)
        
        # 2. Search FAISS index for top-k similar
        distances, indices = self.index.search(
            np.array([query_embedding], dtype=np.float32),
            k=k
        )
        
        # 3. Retrieve corresponding documents
        results = []
        for idx in indices[0]:
            doc = self.documents[idx]
            results.append(doc)
        
        # 4. Format as text for LLM
        context_parts = []
        for r in results:
            context_parts.append(
                f"Q: {r['text']}\n"
                f"A: {r['metadata']['answer']}\n"
                f"SQL: {r['metadata']['sql_query']}"
            )
        
        return "\n\n---\n\n".join(context_parts)
```

#### **Example RAG Context**
```
Previous similar questions:

Q: What is the total revenue?
A: The total revenue across all products is $8.2 million.
SQL: SELECT SUM(sales) as total_revenue FROM session_abc123_Sales

---

Q: Show revenue by product
A: Revenue by product shows...
SQL: SELECT product, SUM(sales) FROM session_abc123_Sales GROUP BY product

---

Q: Which product has highest sales?
A: The highest-selling product is...
SQL: SELECT product, SUM(sales) as total FROM session_abc123_Sales ORDER BY total DESC LIMIT 1
```

---

### **Example 4: Multi-Turn Conversation**

#### **How Conversation Memory Works**
```python
# app/ai/memory.py
class ConversationMemory:
    def __init__(self):
        self._histories = defaultdict(lambda: deque(maxlen=10))
    
    def add_message(self, session_id: str, role: str, content: str):
        self._histories[session_id].append({
            "role": role,
            "content": content
        })
    
    def get_formatted_context(self, session_id: str) -> str:
        history = self.get_history(session_id)
        if not history:
            return ""
        
        parts = []
        for msg in history[-5:]:  # Last 5 messages
            role = "User" if msg["role"] == "user" else "Assistant"
            parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(parts)

# Usage in chat flow:
history_context = ConversationMemory().get_formatted_context(session_id)

# Result:
# User: What is total sales?
# Assistant: Total sales are $8.2 million.
# User: Break it down by category
# Assistant: Sales by category are...
# User: And total by region?
# Assistant: [Current response]
```

---

### **Example 5: LLM Service with Fallback**

#### **Demo Mode When Ollama Unavailable**
```python
# app/ai/llm.py
class LLMService:
    def __init__(self):
        self.available = self._check_ollama_available()
        if not self.available:
            logger.warning("Ollama unavailable. Running in DEMO MODE")
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            import httpx
            client = httpx.Client(timeout=1.0)
            response = client.get(f"{settings.ollama_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def chat(self, messages: list[dict], system_prompt: str = None) -> str:
        if self.available:
            # Use real LLM
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[...],
                    options={
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                )
                return response["message"]["content"]
            except Exception as e:
                logger.error(f"Ollama failed: {e}")
                self.available = False
                return self._get_demo_response(messages[-1]["content"])
        else:
            # Use demo mode
            return self._get_demo_response(messages[-1]["content"])
    
    def _get_demo_response(self, user_input: str) -> str:
        """Generate demo response when Ollama unavailable"""
        prompt_lower = user_input.lower()
        
        if "total" in prompt_lower or "sum" in prompt_lower:
            return "Based on the data analysis, the total value is approximately $8.2M across all categories."
        
        if "category" in prompt_lower:
            return "The dataset contains 5 main categories: Electronics, Clothing, Home & Garden, Sports, and Books."
        
        if "average" in prompt_lower or "mean" in prompt_lower:
            return "The average value across the dataset is approximately $3,200 per entry."
        
        return "Based on the data provided, here are the key insights from your Excel file..."
```

---

### **Example 6: API Response Formatting**

#### **Complete Response Object**
```python
# app/ai/response_builder.py
class ResponseBuilder:
    @staticmethod
    def build_chat_response(
        answer: str,
        sql_query: str | None = None,
        chart_config: dict | None = None,
        sources: list[str] | None = None
    ) -> dict:
        return {
            "status": "success",
            "answer": answer,
            "sql_query": sql_query,
            "chart_config": chart_config,
            "sources": sources or [],
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "processing_time_ms": 3500,
                "model": "qwen2.5:7b",
                "version": "2.0.0"
            }
        }

# Frontend receives:
{
    "status": "success",
    "answer": "Total sales by category shows Electronics leading with $45,000, followed by Clothing at $32,000...",
    "sql_query": "SELECT category, SUM(sales) FROM session_abc123_Sales GROUP BY category ORDER BY SUM(sales) DESC",
    "chart_config": {
        "type": "bar",
        "title": "Sales by Category",
        "x": ["Electronics", "Clothing", "Home"],
        "y": [45000, 32000, 28000]
    },
    "sources": ["previous_Q&A_similar_to_top_sales"],
    "timestamp": "2024-01-15T10:35:22.123456",
    "metadata": {
        "processing_time_ms": 3500,
        "model": "qwen2.5:7b",
        "version": "2.0.0"
    }
}
```

---

## 🔑 Key Implementation Patterns

### **Dependency Injection Pattern**
```python
# app/api/dependencies.py
from functools import lru_cache

@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    return ChatService()

@lru_cache(maxsize=1)
def get_upload_service() -> UploadService:
    return UploadService()

# In routes:
@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    service: ChatService = Depends(get_chat_service)
) -> dict:
    return service.ask(...)
```

### **Error Handling Pattern**
```python
# Middleware for global error handling
@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"detail": str(e), "error_type": "ValueError"}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
```

### **Session Management Pattern**
```python
# Thread-safe singleton
class DatabaseManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

---

## 📊 Data Flow Visualization

```
User ─→ [React]
        ├─→ HTTP Request
        └─→ [FastAPI Route Handler]
            ├─→ Validate Input (Pydantic)
            ├─→ Get Service (Dependency Injection)
            ├─→ [Service Layer]
            │   ├─→ Load Session
            │   ├─→ Prepare Context
            │   └─→ [AI Layer]
            │       ├─→ LLMService.chat()
            │       │   ├─→ Check Ollama Available
            │       │   ├─→ If yes: Call qwen2.5:7b
            │       │   └─→ If no: Return Demo Response
            │       ├─→ EmbeddingService.embed()
            │       ├─→ RAGService.retrieve()
            │       └─→ AIAgent.process()
            ├─→ [Database Layer]
            │   ├─→ DuckDB: Execute SQL
            │   ├─→ FAISS: Vector Search
            │   └─→ MetadataStore: Save History
            ├─→ [Response Layer]
            │   ├─→ Format Response
            │   └─→ Add Metadata
            └─→ HTTP Response (JSON)
        ┌─→ Parse Response
        ├─→ Update State (React)
        └─→ Re-render UI
        │
        └─→ [Browser Display]
            ├─→ Answer Text
            ├─→ SQL Query
            ├─→ Chart Visualization
            └─→ Chat History
```

---

All of this happens seamlessly from the user's perspective - they just type a question and get an answer with visualizations!

