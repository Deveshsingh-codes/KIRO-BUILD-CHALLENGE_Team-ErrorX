# Document Authenticity Verification System

A full-stack application for verifying document authenticity using file hashing and secure storage.

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
