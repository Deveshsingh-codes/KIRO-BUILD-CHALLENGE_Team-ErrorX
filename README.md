# 🔐 Document Authenticity Verification System

A full-stack web application for verifying the integrity of digital documents using secure authentication, SHA-256 file hashing, controlled document storage, and automated verification.

---

## 📑 Table of Contents

~ Problem Statement
~ Our Solution
~ Project Objectives
~ Key Features
~ How the System Works
~ Verification Methodology
~ System Architecture
~ Technology Stack
~ Project Structure
~ Prerequisites
~ Installation & Setup
~ Running the Application
~ Application Workflow
~ API Endpoints
~ Testing
~ Security
~ Environment Variables
~ Troubleshooting
~ Current Limitations
~ Future Scope
~ Project Status
~ License
~ Author

---

# 🎯 Problem Statement

## PROBLEM STATEMENT

With the rapid growth of **AI-generated images, videos, and digitally manipulated documents**, it is becoming increasingly difficult to distinguish authentic content from fake or altered content. Such content can be used to spread **misinformation, create false claims, impersonate people or organizations, and reduce trust in digital information**.

The problem becomes more serious when **fake government documents, identity-related documents, certificates, screenshots, or edited media** are shared online and users have no reliable way to verify their authenticity. Manual verification is often time-consuming, difficult, and dependent on expertise.

**Our project addresses this gap by providing a unified platform for analyzing, verifying, and managing digital content through automated verification and document integrity checks, helping users make more informed decisions about the authenticity of the files they receive.**

---

# 💡 Our Solution

We developed a **Document Authenticity Verification System** that allows authenticated users to upload and manage documents and verify their digital integrity.

When a document is uploaded, the system generates a **SHA-256 cryptographic hash** and stores it with the document metadata.

During verification, the system generates the hash again and compares it with the previously stored hash.

```text
Original Document
       │
       ▼
 SHA-256 Hash
       │
       ▼
Store Hash + Metadata
       │
       ▼
Document Verification
       │
       ▼
Calculate SHA-256 Again
       │
       ▼
Compare Hashes
       │
       ├── Match ──────► VERIFIED
       │
       └── Different ──► REJECTED / MODIFIED
```

This provides a reliable way to detect whether the digital contents of a registered file have changed.

---

# 🎯 Project Objectives

* Provide secure user registration and authentication.
* Allow users to upload and manage documents.
* Generate a unique SHA-256 fingerprint for uploaded files.
* Store document metadata securely.
* Verify documents through hash comparison.
* Detect modifications to registered files.
* Restrict document access to the respective user.
* Provide a simple web-based verification workflow.
* Provide automated testing for the complete application flow.
* Maintain an architecture that can be extended with advanced verification methods.

---

# ✨ Key Features

### 👤 Authentication

* User registration
* Email validation
* Secure password hashing using bcrypt
* JWT-based authentication
* Protected API endpoints
* User-specific document access

### 📄 Document Management

* Document upload
* Automatic SHA-256 hash generation
* Document listing
* Document details
* Document verification
* Verification status tracking
* Document deletion

### 🔐 Security

* JWT authentication
* Bcrypt password hashing
* SHA-256 file fingerprinting
* User-scoped document access
* CORS protection
* Environment-based configuration
* No secrets required in source code

### 🖥️ Web Application

* React-based frontend
* Authentication screens
* Dashboard
* Document management interface
* Verification workflow
* REST API integration

---

# ⚙️ How the System Works

The system follows a simple document verification lifecycle.

### 1. User Registration

The user creates an account using their name, email, and password.

```text
User Details
     │
     ▼
Validation
     │
     ▼
Password Hashing
     │
     ▼
User Stored in Database
```

### 2. User Login

The user authenticates using their credentials.

```text
Email + Password
       │
       ▼
Credential Validation
       │
       ▼
JWT Token
       │
       ▼
Authenticated User
```

### 3. Document Upload

The authenticated user uploads a document.

```text
Upload File
    │
    ▼
Calculate SHA-256
    │
    ▼
Store File
    │
    ▼
Store Metadata + Hash
```

### 4. Document Verification

The system calculates the current hash and compares it with the stored hash.

```text
Stored Hash
     │
     │
     ▼
Current File ──► SHA-256
                    │
                    ▼
              Compare Hashes
                    │
              ┌─────┴─────┐
              ▼           ▼
           MATCH       DIFFERENT
              │           │
              ▼           ▼
          VERIFIED     REJECTED
```

### 5. Document Management

Users can view, verify, and delete their registered documents.

---

# 🔎 Verification Methodology

The current verification mechanism is based on **SHA-256 file integrity verification**.

For every uploaded file:

```text
SHA256(file_contents) → Unique File Hash
```

The resulting hash is stored with the document metadata.

During verification:

```text
Current File Hash == Stored Hash
             │
        ┌────┴────┐
        ▼         ▼
       YES        NO
        │         │
        ▼         ▼
    VERIFIED   REJECTED
```

### What This Verification Means

A matching hash means the current file contents are identical to the contents used when the original hash was generated.

A different hash indicates that the file contents have changed.

> **Note:** SHA-256 verifies digital file integrity. A matching hash alone does not prove that a document was originally issued by a particular institution or that the information inside it is factually genuine.

---

# 🏗️ System Architecture

The application follows a client-server architecture.

```text
┌─────────────────────────────┐
│       React Frontend        │
│                             │
│  Login / Register           │
│  Dashboard                  │
│  Upload                     │
│  Verification               │
│  Document Management        │
└──────────────┬──────────────┘
               │
               │ HTTP / REST API
               ▼
┌─────────────────────────────┐
│       FastAPI Backend       │
│                             │
│ Authentication              │
│ Document APIs               │
│ Validation                  │
│ SHA-256 Hashing             │
│ Security                    │
└──────────────┬──────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌──────────────┐ ┌──────────────┐
│   MongoDB    │ │ File Storage │
│              │ │              │
│ Users        │ │ Uploaded     │
│ Documents    │ │ Documents    │
│ Metadata     │ │              │
└──────────────┘ └──────────────┘
```

---

# 🧰 Technology Stack

## Frontend

* **React 18** — UI development
* **TypeScript** — Type-safe development
* **Vite 5** — Build and development tooling
* **React Router 6** — Application routing
* **Axios** — API communication
* **Lucide React** — Icons

## Backend

* **Python** — Backend development
* **FastAPI** — REST API framework
* **Uvicorn** — Application server
* **Pydantic** — Data validation
* **PyMongo** — MongoDB integration
* **python-jose** — JWT handling
* **bcrypt** — Password hashing

## Database

* **MongoDB / MongoDB Atlas**

## Security & Verification

* **SHA-256**
* **JWT**
* **bcrypt**
* **CORS**

---

# 📁 Project Structure

```text
Kiro-Devesh_Singh/
│
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   └── settings.py
│   │   │       # Application configuration
│   │   │
│   │   ├── database/
│   │   │   └── connection.py
│   │   │       # MongoDB connection
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── document.py
│   │   │       # User and document models
│   │   │
│   │   ├── routers/
│   │   │   ├── auth.py
│   │   │   └── documents.py
│   │   │       # Authentication and document APIs
│   │   │
│   │   └── utils/
│   │       ├── jwt_handler.py
│   │       └── security.py
│   │           # Authentication and security utilities
│   │
│   ├── uploads/
│   │   └── ...
│   │       # Uploaded documents
│   │
│   ├── main.py
│   │   # FastAPI entry point
│   │
│   └── requirements.txt
│       # Backend dependencies
│
├── frontend/
│   ├── src/
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx
│   │   │       # Authentication state
│   │   │
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── Dashboard.tsx
│   │   │       # Main application pages
│   │   │
│   │   ├── services/
│   │   │   └── api.ts
│   │   │       # API client
│   │   │
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── start.sh
│   # Start application
│
├── stop.sh
│   # Stop application
│
├── test_complete_flow.sh
│   # Automated end-to-end tests
│
└── README.md
```

---

# 📋 Prerequisites

Before running the project, install:

* Python 3.8+
* Node.js 18+
* npm
* MongoDB or MongoDB Atlas
* Git

---

# 🛠️ Installation & Setup

### Backend

```bash
cd backend

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
```

Configure the MongoDB connection and JWT secret in `.env`.

### Frontend

```bash
cd frontend

npm install

cp .env.example .env
```

Set:

```env
VITE_API_URL=http://localhost:8000
```

---

# ▶️ Running the Application

## Recommended

From the project root:

```bash
./start.sh
```

Application:

```text
Frontend → http://localhost:5173
Backend  → http://localhost:8000
```

Stop the application:

```bash
./stop.sh
```

## Manual Start

Backend:

```bash
cd backend
source venv/bin/activate
python main.py
```

Frontend:

```bash
cd frontend
npm run dev
```

---

# 🔄 Application Workflow

```text
┌───────────────┐
│    Register   │
└───────┬───────┘
        ↓
┌───────────────┐
│     Login     │
└───────┬───────┘
        ↓
┌───────────────┐
│   Dashboard   │
└───────┬───────┘
        ↓
┌───────────────┐
│ Upload File   │
└───────┬───────┘
        ↓
┌───────────────┐
│ SHA-256 Hash  │
└───────┬───────┘
        ↓
┌───────────────┐
│ Store Record  │
└───────┬───────┘
        ↓
┌───────────────┐
│ Verify File   │
└───────┬───────┘
        ↓
 ┌──────┴──────┐
 ↓             ↓
MATCH       DIFFERENT
 ↓             ↓
VERIFIED     REJECTED
```

---

# 🔌 API Endpoints

## Authentication

| Method | Endpoint         | Purpose           |
| ------ | ---------------- | ----------------- |
| POST   | `/auth/register` | Register user     |
| POST   | `/auth/login`    | Authenticate user |

## Documents

| Method | Endpoint                 | Purpose             |
| ------ | ------------------------ | ------------------- |
| GET    | `/documents/`            | List user documents |
| GET    | `/documents/{id}`        | Get document        |
| POST   | `/documents/upload`      | Upload document     |
| PATCH  | `/documents/{id}`        | Update document     |
| DELETE | `/documents/{id}`        | Delete document     |
| POST   | `/documents/{id}/verify` | Verify document     |

## Health

```text
GET /health
```

---

# 📚 API Documentation

FastAPI provides interactive API documentation:

**Swagger UI**

```text
http://localhost:8000/docs
```

**ReDoc**

```text
http://localhost:8000/redoc
```

---

# 🧪 Testing

The project includes an automated end-to-end test script:

```bash
./test_complete_flow.sh
```

The test suite covers the main application lifecycle:

```text
✓ Backend health check
✓ User registration
✓ User authentication
✓ Document upload
✓ Document listing
✓ Document verification
✓ Document deletion
✓ Cleanup verification

ALL 8 TESTS PASSED
```

Frontend build/type validation:

```bash
cd frontend
npm run build
```

---

# 🔒 Security

The application uses:

* bcrypt** for password hashing
* JWT** for authentication
* SHA-256** for document integrity verification
* User-scoped document access**
* CORS protection**
* Environment variables for sensitive configuration**

Sensitive credentials and secrets should never be committed to the repository.

---

# 🌐 Environment Variables

## Backend

```env
MONGODB_URI=
JWT_SECRET=
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
FRONTEND_URL=http://localhost:5173
```

## Frontend

```env
VITE_API_URL=http://localhost:8000
```

---

# 🚨 Troubleshooting

### Backend does not start

Check Python, activate the virtual environment, and reinstall dependencies if required.

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### MongoDB connection fails

Verify:

* MongoDB is running or Atlas is accessible.
* `MONGODB_URI` is correct.
* Database credentials are valid.

### Frontend does not start

```bash
cd frontend
npm install
npm run dev
```

### Port already in use

```bash
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

---

# ⚠️ Current Limitations

The current system primarily verifies **digital file integrity**.

SHA-256 can determine whether the registered file contents have changed, but a hash match alone does not prove:

* Who originally issued the document.
* Whether the information inside the document is factually correct.
* Whether a scanned document is genuine.
* Whether an image was AI-generated.
* Whether a document visually matches an official template.

These capabilities can be added through additional verification techniques.

---

# 🚀 Future Scope

The system can be extended with:

* AI-generated image detection
* Image/document tampering detection
* OCR-based document analysis
* Document metadata analysis
* QR-code verification
* Digital signatures
* Issuer/institution verification
* Cloud storage
* Audit logs
* Verification history
* Advanced analytics
* CI/CD and cloud deployment

---

# 📊 Project Status

**Current Status: Functional Development Version**

The current implementation includes:

* User authentication
* JWT authorization
* Document upload
* SHA-256 hashing
* Document storage
* Document metadata
* Hash-based verification
* Document management
* REST APIs
* React frontend
* MongoDB persistence
* Automated end-to-end testing

### Latest Documented Test Run

**October 3, 2026**

```text
✓ Backend health check
✓ User registration
✓ User authentication
✓ Document upload
✓ Document listing
✓ Document verification
✓ Document deletion
✓ Cleanup verification

ALL 8 TESTS PASSED
```

---

# 📄 License

This project is licensed under the MIT License.

---

# 👤 Author
 Devesh Singh | Aryan Singh

### Document Authenticity Verification System

Built with:

**React + TypeScript + FastAPI + MongoDB + SHA-256**
