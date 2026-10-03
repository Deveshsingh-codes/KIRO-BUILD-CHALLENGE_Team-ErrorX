import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { getDocuments, uploadDocument, deleteDocument, verifyDocument } from '../services/api'
import { LogOut, Upload, Trash2, CheckCircle, XCircle, AlertCircle, Clock, Shield, FileText } from 'lucide-react'
import './Dashboard.css'

interface DetectionResult {
  name: string
  detected: boolean
  confidence?: number
  details?: string
  severity?: string
}

interface VerificationResult {
  overall_status: string
  authenticity_score?: number
  fake_probability?: number
  detections: DetectionResult[]
  metadata: Record<string, any>
  analyzed_at: string
}

interface Document {
  id: string
  title: string
  description?: string
  file_hash: string
  file_path: string
  status: 'pending' | 'verified' | 'rejected' | 'suspicious' | 'manual_review'
  created_at: string
  updated_at: string
  verification_result?: VerificationResult
}

export default function Dashboard() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [verifying, setVerifying] = useState<string | null>(null)
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null)
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
      let errorMessage = 'Failed to load documents'
      const detail = err.response?.data?.detail
      
      if (detail) {
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || JSON.stringify(detail)
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      if (typeof errorMessage !== 'string') {
        errorMessage = JSON.stringify(errorMessage)
      }
      
      setError(errorMessage)
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
      let errorMessage = 'Failed to upload document'
      const detail = err.response?.data?.detail
      
      if (detail) {
        if (typeof detail === 'string') {
          errorMessage = detail
        } else if (Array.isArray(detail)) {
          errorMessage = detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ')
        } else if (typeof detail === 'object') {
          errorMessage = detail.msg || JSON.stringify(detail)
        }
      } else if (err.message) {
        errorMessage = err.message
      }
      
      if (typeof errorMessage !== 'string') {
        errorMessage = JSON.stringify(errorMessage)
      }
      
      setError(errorMessage)
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    setError('')
    try {
      await deleteDocument(id)
      if (selectedDoc?.id === id) {
        setSelectedDoc(null)
      }
      await loadDocuments()
    } catch (err: any) {
      let errorMessage = 'Failed to delete document'
      if (err.response?.data?.detail && typeof err.response.data.detail === 'string') {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      }
      if (typeof errorMessage !== 'string') {
        errorMessage = JSON.stringify(errorMessage)
      }
      setError(errorMessage)
    }
  }

  const handleVerify = async (id: string) => {
    setError('')
    setVerifying(id)
    try {
      const result = await verifyDocument(id)
      await loadDocuments()
      setSelectedDoc(result)
    } catch (err: any) {
      let errorMessage = 'Failed to verify document'
      if (err.response?.data?.detail && typeof err.response.data.detail === 'string') {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      }
      if (typeof errorMessage !== 'string') {
        errorMessage = JSON.stringify(errorMessage)
      }
      setError(errorMessage)
    } finally {
      setVerifying(null)
    }
  }

  const getStatusInfo = (status: string) => {
    switch (status) {
      case 'verified':
        return { icon: CheckCircle, text: 'Verified', className: 'status-verified' }
      case 'rejected':
        return { icon: XCircle, text: 'Rejected', className: 'status-rejected' }
      case 'suspicious':
        return { icon: AlertCircle, text: 'Suspicious', className: 'status-suspicious' }
      case 'manual_review':
        return { icon: Shield, text: 'Manual Review', className: 'status-review' }
      default:
        return { icon: Clock, text: 'Pending', className: 'status-pending' }
    }
  }

  const getOverallStatusLabel = (status: string) => {
    switch (status) {
      case 'verified':
        return 'VERIFIED'
      case 'rejected':
        return 'LIKELY FAKE / MANIPULATED'
      case 'suspicious':
        return 'SUSPICIOUS'
      case 'manual_review':
        return 'MANUAL REVIEW REQUIRED'
      default:
        return 'PENDING ANALYSIS'
    }
  }

  const renderVerificationDetails = (doc: Document) => {
    const result = doc.verification_result
    if (!result) return null

    return (
      <div className="verification-details">
        <div className="verification-header">
          <div className={`overall-status ${doc.status}`}>
            <h2>{getOverallStatusLabel(doc.status)}</h2>
          </div>

          {(result.authenticity_score !== undefined || result.fake_probability !== undefined) && (
            <div className="confidence-scores">
              {result.authenticity_score !== undefined && (
                <div className="score-card authenticity">
                  <div className="score-label">Estimated Authenticity</div>
                  <div className="score-value">{result.authenticity_score.toFixed(1)}%</div>
                  <div className="score-note">AI confidence estimate</div>
                </div>
              )}
              {result.fake_probability !== undefined && (
                <div className="score-card fake-prob">
                  <div className="score-label">Estimated Fake Probability</div>
                  <div className="score-value">{result.fake_probability.toFixed(1)}%</div>
                  <div className="score-note">AI confidence estimate</div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="detections-section">
          <h3>Detection Summary</h3>
          <div className="detections-grid">
            {result.detections.map((detection, idx) => (
              <div key={idx} className={`detection-card ${detection.detected ? 'detected' : 'not-detected'} ${detection.severity || ''}`}>
                <div className="detection-header">
                  <div className="detection-name">{detection.name}</div>
                  <div className={`detection-status ${detection.detected ? 'detected' : ''}`}>
                    {detection.confidence !== null && detection.confidence !== undefined
                      ? detection.detected ? 'Detected' : 'Not Detected'
                      : 'Not Available'}
                  </div>
                </div>
                {detection.confidence !== null && detection.confidence !== undefined && (
                  <div className="detection-confidence">
                    Confidence: {detection.confidence.toFixed(1)}%
                  </div>
                )}
                {detection.details && (
                  <div className="detection-details">{detection.details}</div>
                )}
                {detection.severity && (
                  <div className={`detection-severity severity-${detection.severity}`}>
                    Severity: {detection.severity}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {result.metadata && Object.keys(result.metadata).length > 0 && (
          <div className="metadata-section">
            <h3>File Metadata</h3>
            <div className="metadata-grid">
              {Object.entries(result.metadata).map(([key, value]) => (
                <div key={key} className="metadata-item">
                  <span className="metadata-key">{key.replace(/_/g, ' ')}:</span>
                  <span className="metadata-value">{String(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="analysis-timestamp">
          Analyzed at: {new Date(result.analyzed_at).toLocaleString()}
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="header-content">
          <Shield size={32} className="app-icon" />
          <h1>Document Authenticity Verification</h1>
        </div>
        <button onClick={logout} className="logout-btn">
          <LogOut size={18} /> Logout
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="dashboard-layout">
        <div className="sidebar">
          <div className="upload-section">
            <h2><Upload size={20} /> Upload Document</h2>
            <form onSubmit={handleUpload} className="upload-form">
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                disabled={uploading}
                required
              />
              <input
                type="text"
                placeholder="Title (optional)"
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
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
            </form>
          </div>

          <div className="documents-list">
            <h2><FileText size={20} /> Your Documents</h2>
            {loading ? (
              <div className="loading-state">Loading documents...</div>
            ) : documents.length === 0 ? (
              <div className="empty-state">No documents uploaded yet</div>
            ) : (
              <div className="documents-items">
                {documents.map((doc) => {
                  const statusInfo = getStatusInfo(doc.status)
                  const StatusIcon = statusInfo.icon
                  return (
                    <div
                      key={doc.id}
                      className={`document-item ${selectedDoc?.id === doc.id ? 'selected' : ''}`}
                      onClick={() => setSelectedDoc(doc)}
                    >
                      <div className="document-info">
                        <div className="document-title">{doc.title}</div>
                        <div className={`document-status ${statusInfo.className}`}>
                          <StatusIcon size={14} />
                          <span>{statusInfo.text}</span>
                        </div>
                      </div>
                      <div className="document-actions">
                        {doc.status === 'pending' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleVerify(doc.id)
                            }}
                            disabled={verifying === doc.id}
                            className="verify-btn"
                          >
                            {verifying === doc.id ? 'Verifying...' : 'Verify'}
                          </button>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(doc.id)
                          }}
                          className="delete-btn"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>

        <div className="main-content">
          {selectedDoc ? (
            <div className="document-details">
              <div className="document-details-header">
                <h2>{selectedDoc.title}</h2>
                {selectedDoc.description && (
                  <p className="document-description">{selectedDoc.description}</p>
                )}
                <div className="document-meta">
                  <span>Uploaded: {new Date(selectedDoc.created_at).toLocaleDateString()}</span>
                  <span>Hash: {selectedDoc.file_hash.substring(0, 16)}...</span>
                </div>
              </div>

              {selectedDoc.verification_result ? (
                renderVerificationDetails(selectedDoc)
              ) : (
                <div className="no-verification">
                  <Shield size={48} />
                  <p>No verification results yet</p>
                  <button
                    onClick={() => handleVerify(selectedDoc.id)}
                    disabled={verifying === selectedDoc.id}
                    className="verify-btn-large"
                  >
                    {verifying === selectedDoc.id ? 'Analyzing...' : 'Run Verification'}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="no-selection">
              <FileText size={64} />
              <p>Select a document to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
