# Quick Setup Guide

## Prerequisites Check

Before starting, verify you have:
- Python 3.8+ installed: `python3 --version`
- Node.js 18+ installed: `node --version`
- MongoDB Atlas account (free tier available)

## Backend Setup (5 minutes)

### 1. Install Backend Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Activates virtual environment
pip install -r requirements.txt
```

**Note:** If pip install takes too long or fails, try installing packages individually:
```bash
pip install --no-cache-dir fastapi uvicorn pymongo python-jose passlib python-dotenv python-multipart pydantic pydantic-settings
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `backend/.env` and update these values:

**MONGODB_URI:**
1. Go to https://www.mongodb.com/cloud/atlas
2. Create free cluster (if you don't have one)
3. Create database user (Database Access > Add New Database User)
4. Whitelist IP (Network Access > Add IP Address > Allow Access from Anywhere for dev)
5. Get connection string (Clusters > Connect > Connect your application)
6. Replace `<username>`, `<password>`, and database name in connection URI

**JWT_SECRET:**
Generate a secure secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example `.env` file:
```
MONGODB_URI=mongodb+srv://myuser:mypassword@cluster0.xxxxx.mongodb.net/authenticity_verification?retryWrites=true&w=majority
JWT_SECRET=your-generated-secret-here-32-chars-minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:5173
```

### 3. Test Backend

```bash
# Make sure virtual environment is activated
cd backend
source venv/bin/activate

# Start backend
python main.py
```

Backend should start at http://localhost:8000
API docs at http://localhost:8000/docs

## Frontend Setup (2 minutes)

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment (Optional)

```bash
cp .env.example .env
```

Default configuration works for local development. Only change if backend runs on different port.

### 3. Start Frontend

```bash
npm run dev
```

Frontend runs at http://localhost:5173

## Verify Installation

1. Open http://localhost:5173 in browser
2. Register a new account
3. Upload a test document
4. Click verify button to check authenticity

## Troubleshooting

### Backend Issues

**"No module named 'app'"**
- Make sure you're in the `backend` directory
- Activate virtual environment: `source venv/bin/activate`

**"Failed to connect to MongoDB"**
- Verify MongoDB URI is correct in `.env`
- Check IP is whitelisted in MongoDB Atlas
- Verify database user credentials

**"JWT secret required"**
- Ensure `JWT_SECRET` is set in `backend/.env`

### Frontend Issues

**"Cannot connect to backend"**
- Verify backend is running on http://localhost:8000
- Check console for CORS errors
- Verify `VITE_API_URL` in `frontend/.env` matches backend URL

**Build errors**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again
- Clear npm cache: `npm cache clean --force`

## Project Structure

```
.
├── backend/
│   ├── app/                    # Application code
│   │   ├── config/            # Settings
│   │   ├── database/          # MongoDB connection
│   │   ├── models/            # Data models
│   │   ├── routers/           # API endpoints
│   │   └── utils/             # JWT, security
│   ├── main.py                # Application entry
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Configuration (create from .env.example)
│
└── frontend/
    ├── src/
    │   ├── contexts/          # Auth state
    │   ├── pages/             # Login, Register, Dashboard
    │   ├── services/          # API client
    │   └── App.tsx            # Main app
    ├── package.json           # Node dependencies
    └── .env                   # Configuration (create from .env.example)
```

## Next Steps

1. **Production Deployment:** Update `FRONTEND_URL` in backend `.env` to your production domain
2. **Security:** Use environment-specific `.env` files, never commit secrets
3. **Database:** Create indexes on frequently queried fields (user_id, file_hash)
4. **Storage:** Consider cloud storage (S3, GCS) instead of local file storage for production

## Quick Commands Reference

**Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Build Frontend for Production:**
```bash
cd frontend
npm run build
npm run preview  # Test production build
```
