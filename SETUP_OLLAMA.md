# AI Excel Chat Platform - Setup & Troubleshooting Guide

## 🟢 Status: API Running in DEMO MODE

The backend API is running successfully but is currently in **DEMO MODE** because Ollama is not installed/running.

**This is normal for development!** The app will still work with basic responses. To enable full AI capabilities, follow the setup instructions below.

---

## ❌ Current Issue: Ollama Not Available

**Error Messages Seen:**
```
ERROR | app.ai.llm | Ollama chat failed: model 'qwen2.5:7b' not found (status code: 404)
ERROR | app.ai.embeddings | Embedding failed: model "nomic-embed-text" not found
```

**What This Means:**
- Ollama service is not running at `http://localhost:11434`
- The LLM model `qwen2.5:7b` is not installed
- The embedding model `nomic-embed-text` is not installed

---

## ✅ SOLUTION: Install & Setup Ollama

### **Step 1: Download and Install Ollama**

**Windows:**
1. Download: https://ollama.ai/download/windows
2. Run the installer
3. Accept all prompts
4. Ollama will start automatically

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

### **Step 2: Start Ollama Service**

**Windows (after installation):**
- Ollama starts automatically in the background
- Check tray icon (should show Ollama running)

**macOS/Linux:**
```bash
ollama serve
```

The service will be available at `http://localhost:11434`

### **Step 3: Pull Required Models**

Open a new terminal and run:

```bash
# Main LLM model (used for chat and SQL generation)
ollama pull qwen2.5:7b

# Embedding model (used for semantic search)
ollama pull nomic-embed-text
```

**Time Required:**
- `qwen2.5:7b`: ~5-10 GB download, 5-15 minutes
- `nomic-embed-text`: ~300 MB download, 1-2 minutes

**Total:** Plan for 20-30 minutes depending on internet speed

### **Step 4: Verify Installation**

Check if models are installed:
```bash
ollama list
```

Expected output:
```
qwen2.5:7b          latest  4.4 GB   
nomic-embed-text    latest  274 MB   
```

### **Step 5: Restart the Backend API**

Once Ollama is running with models installed:

**Terminal 1 (Ollama):**
```bash
ollama serve
# Output: Listening on 127.0.0.1:11434
```

**Terminal 2 (Backend):**
```bash
cd D:\AIPythonExcelChat\PythonAIBackend
python main.py
# Should now connect to Ollama automatically
```

**Check Logs:**
```
INFO | app.ai.llm | Ollama service available at http://localhost:11434
```

---

## 🧪 Testing After Setup

### **Test 1: Health Check**
```bash
curl http://localhost:8000/api/v1/health
# Response: {"status":"healthy",...}
```

### **Test 2: Upload Excel File**
Use the frontend or:
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@data.xlsx"
```

### **Test 3: Chat Query (will now use real AI)**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "question": "What is the total quantity?",
    "sheet_name": "SalesData"
  }'
```

**Before Ollama (Demo Mode):**
```json
{
  "answer": "Based on the data analysis, the total value is approximately 45,000 units...",
  "sql_query": null,
  "chart_config": null
}
```

**After Ollama (Full AI):**
```json
{
  "answer": "The total quantity across all products is 15,847 units...",
  "sql_query": "SELECT SUM(quantity) FROM session_0cb2ca52_SalesData",
  "chart_config": {"type": "bar", "x": "category", "y": "quantity"},
  "sources": ["SalesData"]
}
```

---

## 📊 Demo Mode vs Full AI Mode

| Feature | Demo Mode | Full AI Mode |
|---------|-----------|-------------|
| Chat responses | Generic/pattern-matched | AI-generated, accurate |
| SQL generation | ❌ None | ✅ Dynamic SQL queries |
| Chart suggestions | ❌ None | ✅ Smart recommendations |
| Data analysis | ❌ Limited | ✅ Deep analysis |
| Performance | ⚡ Instant | 🤔 2-5 seconds |
| Requirements | None | Ollama + models |

---

## 🔧 Troubleshooting

### **Problem: "Ollama service not available"**

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
# Should return list of models
```

If error, start Ollama:
```bash
ollama serve
```

### **Problem: Model not found (404)**

**Check installed models:**
```bash
ollama list
```

**Install missing models:**
```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### **Problem: High memory/CPU usage**

Ollama uses significant resources:
- `qwen2.5:7b`: ~8 GB RAM
- Embeddings: ~2 GB RAM
- Total: 10+ GB recommended

If system is slow, reduce model size:
```bash
ollama pull qwen2.5:1.5b  # Smaller, faster model
```

Update `app/core/config.py`:
```python
llm_model: str = Field(default="qwen2.5:1.5b")
```

### **Problem: Port 11434 already in use**

Another instance of Ollama might be running:

**Windows:**
```bash
netstat -ano | findstr :11434
taskkill /PID <PID> /F
```

**Linux/macOS:**
```bash
lsof -i :11434
kill -9 <PID>
```

### **Problem: API response takes too long**

**First request after restart is slow** (model loads into memory): Normal
**Subsequent requests**: Should be 1-5 seconds

If consistently slow:
- Check system RAM (need 10+ GB)
- Use smaller model: `qwen2.5:1.5b`
- Check CPU is not maxed out

---

## 📈 Performance Tips

### **For Development (Demo Mode)**
- API responds instantly
- No AI features, but good for testing UI
- **Best for:** Frontend development, file upload testing

### **For Production (Full AI Mode)**
- Enable GPU acceleration if available:
  ```bash
  # NVIDIA GPU
  ollama serve --gpu=1
  ```
- Use smaller, faster models:
  - `qwen2.5:1.5b` (fast, 4 GB RAM)
  - `mistral:latest` (quality alternative)
- Add request caching (future enhancement)

### **Recommended Setup**

**Minimum (Development):**
- Skip Ollama, use demo mode
- 8 GB RAM
- SSD for database

**Recommended (Production):**
- Ollama with `qwen2.5:7b`
- 16+ GB RAM
- NVIDIA GPU (optional but recommended)
- SSD for storage

---

## 🚀 Quick Start Checklist

- [ ] Ollama installed and running (`ollama serve`)
- [ ] Models downloaded (`ollama list` shows both models)
- [ ] Backend API running (`python main.py`)
- [ ] Frontend running (`npm run dev`)
- [ ] Health check passing (`curl http://localhost:8000/api/v1/health`)
- [ ] Can upload Excel file
- [ ] Chat returns real AI answers

---

## 📞 Getting Help

### **Check Logs:**
```bash
# In your backend terminal, watch for Ollama connection messages
2026-07-13 15:18:49 | INFO | app.ai.llm | Ollama service available at http://localhost:11434
```

### **Verify Ollama Status:**
```bash
# Terminal where Ollama is running should show:
# "Listening on 127.0.0.1:11434"
```

### **Test Ollama Directly:**
```bash
curl http://localhost:11434/api/tags
# Should return JSON with model list
```

---

## 📚 Additional Resources

- **Ollama Official:** https://ollama.ai
- **Model Details:** https://ollama.ai/library
- **Documentation:** https://github.com/ollama/ollama
- **Community:** https://discord.gg/ollama

---

## ✨ Summary

**Current State:** ✅ API working in DEMO MODE  
**Next Step:** Install Ollama + models for full AI features  
**Time Required:** 20-30 minutes  
**Difficulty:** Easy (just download and run)

Once Ollama is set up, the chat functionality will automatically enable full AI capabilities including:
- ✅ Natural language SQL generation
- ✅ Intelligent chart recommendations
- ✅ Data analysis and insights
- ✅ Context-aware responses

Enjoy! 🎉
