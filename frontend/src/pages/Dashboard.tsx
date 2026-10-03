import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { getDocuments, uploadDocument, deleteDocument, verifyDocument } from '../services/api'
import { LogOut, Upload, Trash2, CheckCircle } from 'lucide-react'

interface Document {
  id: string
  title: string
  description?: string
  file_hash: string
  status: 'pending' | 'verified' | 'rejected'
  created_at: string
  updated_at: string
}

export default function Dashboard() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const { logout } = useAuth()

  const loadDocuments = async () => {
    setLoading(true)
    setError('')
    try {
      const docs = await getDocuments()
      setDocuments(docs)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDocuments()
  }, [])

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    setUploading(true)
    setError('')
    try {
      await uploadDocument(file, title, description)
      setFile(null)
      setTitle('')
      setDescription('')
      await loadDocuments()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload document')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    setError('')
    try {
      await deleteDocument(id)
      await loadDocuments()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete document')
    }
  }

  const handleVerify = async (id: string) => {
    setError('')
    try {
      await verifyDocument(id)
      await loadDocuments()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to verify document')
    }
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Document Verification Dashboard</h1>
        <button onClick={logout}>
          <LogOut size={18} /> Logout
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="upload-section">
        <h2>
          <Upload size={24} /> Upload Document
        </h2>
        <form onSubmit={handleUpload} className="upload-form">
          <input
            type="file"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            required
            disabled={uploading}
          />
          <input
            type="text"
            placeholder="Document Title (optional)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={uploading}
          />
          <textarea
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            disabled={uploading}
            rows={3}
          />
          <button type="submit" disabled={uploading || !file}>
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        </form>
      </div>

      <div className="documents-section">
        <h2>Your Documents</h2>
        {loading ? (
          <p>Loading documents...</p>
        ) : documents.length === 0 ? (
          <p>No documents uploaded yet.</p>
        ) : (
          <div className="documents-list">
            {documents.map((doc) => (
              <div key={doc.id} className="document-card">
                <div className="document-info">
                  <h3>{doc.title}</h3>
                  {doc.description && <p>{doc.description}</p>}
                  <p>
                    <strong>Hash:</strong> {doc.file_hash.substring(0, 16)}...
                  </p>
                  <p>
                    <strong>Uploaded:</strong> {new Date(doc.created_at).toLocaleString()}
                  </p>
                  <span className={`document-status ${doc.status}`}>{doc.status}</span>
                </div>
                <div className="document-actions">
                  <button onClick={() => handleVerify(doc.id)} title="Verify Document">
                    <CheckCircle size={18} />
                  </button>
                  <button onClick={() => handleDelete(doc.id)} title="Delete Document">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
