# Document Authenticity Verification System

A full-stack application for verifying document authenticity using SHA256 file hashing and secure storage.

## 🚀 Quick Start

```bash
# Start the application
./start.sh

# Run comprehensive tests
./test_complete_flow.sh

# Stop the application
./stop.sh
```

Then open http://localhost:5173 in your browser.

## ✅ Current Status

**FULLY FUNCTIONAL - ALL TESTS PASSING**

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ MongoDB local instance configured and running
- ✅ All dependencies installed
- ✅ End-to-end tests passing
- ✅ No known blockers

## 🎯 Features

### Authentication
- User registration with email validation
- Secure login with JWT tokens
- Password hashing with bcrypt
- Protected routes and API endpoints

### Document Management
- Upload documents (any file type)
- Automatic SHA256 hash generation
- Document listing (user-scoped)
- Document verification by hash comparison
- Document deletion with file cleanup
- Status tracking (pending, verified, rejected)

### Security
- JWT-based authentication
- Bcrypt password hashing
- User-scoped document access
- CORS protection
- Environment-based configuration
- No hardcoded secrets

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI 0.104.1
- **Database:** MongoDB 8.0.32
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt
- **Server:** Uvicorn

### Frontend
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite 5
- **Routing:** React Router 6
- **HTTP Client:** Axios
- **Icons:** Lucide React

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB (installed automatically via start script)

## 🛠️ Installation

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work for local development)
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (optional)
cp .env.example .env
```

### 3. MongoDB Setup

MongoDB is automatically installed and started by the start script. If you need to manually install:

```bash
brew tap mongodb/brew
brew install mongodb-community@8.0
brew services start mongodb/brew/mongodb-community@8.0
```

## 🎮 Running the Application

### Option 1: Using Scripts (Recommended)

```bash
# Start everything
./start.sh

# Stop everything
./stop.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 🧪 Testing

### Run Complete Test Suite
```bash
./test_complete_flow.sh
```

This tests:
- ✅ Backend health check
- ✅ User registration
- ✅ User authentication
- ✅ Document upload
- ✅ Document listing
- ✅ Document verification (hash comparison)
- ✅ Document deletion
- ✅ Cleanup verification

### Manual API Testing

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📁 Project Structure

```
Kiro-Devesh_Singh/
├── backend/
│   ├── app/
│   │   ├── config/          # Settings & configuration
│   │   ├── database/        # MongoDB connection
│   │   ├── models/          # Pydantic models
│   │   ├── routers/         # API endpoints
│   │   └── utils/           # JWT, security utilities
│   ├── uploads/             # Uploaded documents
│   ├── main.py              # Application entry point
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── contexts/        # React contexts
│   │   ├── pages/           # Page components
│   │   ├── services/        # API client
│   │   └── App.tsx          # Main application
│   └── package.json         # Node dependencies
│
├── start.sh                 # Start script
├── stop.sh                  # Stop script
├── test_complete_flow.sh    # Test script
└── README.md                # This file
```

## 🔐 Environment Variables

### Backend (.env)
```env
MONGODB_URI=mongodb://localhost:27017/authenticity_verification
JWT_SECRET=dev-secret-key-change-in-production-32chars-minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:5173
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🎯 How It Works

1. **User Registration/Login:** Users create accounts with hashed passwords
2. **Document Upload:** Files are uploaded and SHA256 hash is calculated
3. **Storage:** Document metadata and hash stored in MongoDB, file saved locally
4. **Verification:** System recalculates hash and compares with stored hash
   - **Verified:** Hashes match (file unchanged)
   - **Rejected:** Hashes don't match (file modified)
5. **Management:** Users can view, verify, and delete their documents

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check MongoDB is running
mongosh --eval "db.version()"

# If not, start it
brew services start mongodb/brew/mongodb-community@8.0

# Check virtual environment
cd backend && source venv/bin/activate
python -c "import fastapi; print('OK')"
```

### Frontend won't start
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port already in use
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9  # Backend
lsof -ti:5173 | xargs kill -9  # Frontend
```

## 📊 Test Results

Last test run: **October 3, 2026**

```
✅ Backend health check
✅ User registration
✅ User authentication  
✅ Document upload
✅ Document listing
✅ Document verification (hash comparison)
✅ Document deletion
✅ Cleanup verification

ALL 8 TESTS PASSED
```

## 🔒 Security Notes

- Passwords hashed with bcrypt
- JWT tokens with 24-hour expiry
- User-scoped document access
- CORS protection enabled
- Environment-based configuration
- No secrets in repository

**For Production:**
- Generate strong JWT secret (32+ chars)
- Use MongoDB Atlas or production cluster
- Enable HTTPS
- Add rate limiting
- Configure proper CORS origins
- Add file size/type validation

## 📝 License

MIT

## 👤 Author

Devesh Singh

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 📞 Support

For issues or questions:
1. Check VERIFICATION_REPORT.md
2. Review API documentation at /docs
3. Run test suite to verify installation

---

**Status:** ✅ Production Ready for Local Development  
**Last Updated:** October 3, 2026

## Features

- User authentication (register/login)
- Document upload with automatic hash generation
- Document verification by comparing stored and current file hashes
- Document management (view, delete)
- Secure JWT-based authentication
- MongoDB Atlas for data persistence

## Tech Stack

### Backend
- FastAPI (Python web framework)
- MongoDB (Atlas cloud database)
- PyMongo (MongoDB driver)
- JWT authentication
- Bcrypt password hashing

### Frontend
- React 18 with TypeScript
- Vite (build tool)
- React Router (navigation)
- Axios (HTTP client)
- Lucide React (icons)

## Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB Atlas account with connection URI

## Setup Instructions

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your MongoDB Atlas URI and JWT secret
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env if needed (default: VITE_API_URL=http://localhost:8000)
```

### 3. MongoDB Atlas Configuration

1. Create a MongoDB Atlas account at https://www.mongodb.com/cloud/atlas
2. Create a new cluster (free tier available)
3. Create a database user with read/write permissions
4. Whitelist your IP address (or allow access from anywhere for development)
5. Get your connection string and update the `MONGODB_URI` in `backend/.env`

Example connection string:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/authenticity_verification?retryWrites=true&w=majority
```

### 4. JWT Secret

Generate a secure JWT secret:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add this to `JWT_SECRET` in `backend/.env`

## Running the Application

### Start Backend

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
python main.py
```

Backend will run at: http://localhost:8000

API documentation available at: http://localhost:8000/docs

### Start Frontend

```bash
cd frontend
npm run dev
```

Frontend will run at: http://localhost:5173

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   └── settings.py          # Configuration management
│   │   ├── database/
│   │   │   └── connection.py        # MongoDB connection
│   │   ├── models/
│   │   │   ├── user.py             # User data models
│   │   │   └── document.py         # Document data models
│   │   ├── routers/
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   └── documents.py        # Document endpoints
│   │   └── utils/
│   │       ├── jwt_handler.py      # JWT token management
│   │       └── security.py         # Password hashing
│   ├── main.py                     # FastAPI application entry
│   └── requirements.txt            # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx     # Authentication state
│   │   ├── pages/
│   │   │   ├── Login.tsx           # Login page
│   │   │   ├── Register.tsx        # Registration page
│   │   │   └── Dashboard.tsx       # Main dashboard
│   │   ├── services/
│   │   │   └── api.ts              # API client
│   │   ├── App.tsx                 # Main application
│   │   └── main.tsx                # Entry point
│   ├── package.json                # Node dependencies
│   └── vite.config.ts              # Vite configuration
│
└── README.md
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token

### Documents
- `GET /documents/` - Get all user documents
- `GET /documents/{id}` - Get specific document
- `POST /documents/upload` - Upload new document
- `PATCH /documents/{id}` - Update document details
- `DELETE /documents/{id}` - Delete document
- `POST /documents/{id}/verify` - Verify document authenticity

## How It Works

1. **Registration/Login**: Users create an account and authenticate
2. **Document Upload**: Users upload documents (any file type)
3. **Hash Generation**: System calculates SHA256 hash of uploaded file
4. **Storage**: Document metadata and hash stored in MongoDB, file saved on server
5. **Verification**: System recalculates hash and compares with stored hash
   - **Verified**: Hashes match (file unchanged)
   - **Rejected**: Hashes don't match (file modified)

## Security Features

- Passwords hashed with bcrypt
- JWT token-based authentication
- HTTP-only token storage
- CORS protection
- File hash verification (SHA256)
- Secure file upload handling

## Development

### Type Checking (Frontend)
```bash
cd frontend
npm run build  # Includes TypeScript type checking
```

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation

## Troubleshooting

### Backend won't start
- Check MongoDB connection URI is correct
- Ensure virtual environment is activated
- Verify all dependencies are installed

### Frontend won't start
- Check Node.js version (requires 18+)
- Run `npm install` again
- Clear `node_modules` and reinstall if needed

### Cannot upload files
- Check `uploads/` directory exists and is writable
- Verify backend is running
- Check CORS settings if frontend on different port

## License

MIT
