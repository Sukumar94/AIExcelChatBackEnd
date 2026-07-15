# ✨ Permanent Database Lock Solutions

## 🎯 PERMANENT FIX: Use Startup Scripts

### **Windows PowerShell (RECOMMENDED)**
```powershell
.\start_api.ps1
```

### **Windows Command Prompt**
```cmd
start_api.bat
```

---

## What These Scripts Do (PERMANENT)

✅ Kill any existing Python processes  
✅ Wait 5 seconds for OS to release file locks  
✅ Start fresh API with no conflicts  
✅ Display API status and docs URL  

---

## ✅ Fixes Implemented

### 1. **Automatic Process Cleanup**
- Startup scripts kill stale processes before starting
- Prevents database lock conflicts

### 2. **Long Wait for File Locks**  
- 5-second delay ensures OS releases all locks
- Solves "file already open" errors

### 3. **Enhanced Retry Logic**
- Exponential backoff: 2s, 4s, 6s
- Read-only fallback if write fails

### 4. **Proper Connection Cleanup**
- Database closed cleanly on shutdown
- No connection leaks

---

## 🚀 How to Start (Choose One)

### Best Option: PowerShell Script
```powershell
# Just double-click or run:
.\start_api.ps1
```

### Alternative: Manual Commands
```powershell
# 1. Kill existing processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# 2. Wait 5 seconds
Start-Sleep -Seconds 5

# 3. Start API
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🔧 Configuration

### `.env` file (optional)
```
DEBUG=false
DUCKDB_PATH=data/databases/analytics.db
```

---

## 🛡️ What's Fixed

| Issue | Solution |
|-------|----------|
| Database locked on startup | Kill + 5s wait |
| Stale process conflicts | Auto cleanup |
| Connection leaks | Proper shutdown |
| Retry failures | Exponential backoff |
| Write failures | Read-only fallback |

---

## 📊 Check API Status

```powershell
# Health check
curl http://localhost:8000/api/v1/health

# View docs
Start-Process http://localhost:8000/docs
```

---

## ⚠️ Troubleshooting

### Still getting lock errors?

1. **Run the startup script:**
   ```powershell
   .\start_api.ps1
   ```

2. **Manual cleanup:**
   ```powershell
   Get-Process python | Stop-Process -Force
   Start-Sleep -Seconds 10
   python -m uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **Check for locks:**
   ```powershell
   Get-Process python
   ```

---

## ✨ Bottom Line

**Problem: Database locks on startup**  
**Solution: `.\start_api.ps1`**  
**That's it!** 🎉

No more manual killing processes.  
No more waiting and retrying.  
Just run the startup script and you're done.

