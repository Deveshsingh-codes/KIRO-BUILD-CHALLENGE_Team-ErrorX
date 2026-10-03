# Quick Start Guide

## Services Running

- ✅ **MongoDB:** Port 27017 (running)
- ✅ **Backend:** Port 8000 (running)
- ✅ **Frontend:** Port 5174 (running)

## URLs

- **Frontend:** http://localhost:5174
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## Quick Commands

```bash
# Health check
curl http://localhost:8000/health

# Run all tests
./test_complete_flow.sh

# Verify browser flow
./verify_browser_flow.sh

# Check services
ps aux | grep -E "(mongod|uvicorn|vite)"

# Restart backend
cd backend && source venv/bin/activate && python main.py

# Restart frontend
cd frontend && npm run dev
```

## Test Flow in Browser

1. Open: http://localhost:5174
2. Register: Any email + password
3. Login: Use registered credentials
4. Upload: Select file + add title + description
5. ✅ Verify: No black screen, document appears in list

## What Was Fixed

1. **401 Errors** → Removed Content-Type override in api.ts
2. **Black Screen** → Safe error normalization in Dashboard.tsx
3. **422 Errors** → Added Form() parameters in documents.py
4. **Bcrypt Issue** → Replaced passlib with direct bcrypt

## Files Changed

- `frontend/src/services/api.ts`
- `frontend/src/pages/Dashboard.tsx`
- `backend/app/routers/documents.py`
- `backend/app/utils/security.py`

## Status

✅ **ALL SYSTEMS OPERATIONAL**

Full details: See VERIFICATION_REPORT.md
