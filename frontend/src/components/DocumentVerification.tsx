import { useState } from 'react'
import { uploadDocument, verifyIdDocument } from '../services/api'
import { Upload, FileText, Shield, Eye, EyeOff } from 'lucide-react'
import './DocumentVerification.css'

const DOCUMENT_TYPES = [
  { id: 'aadhaar', name: 'Aadhaar Card', icon: '🆔' },
  { id: 'pan', name: 'PAN Card', icon: '💳' },
  { id: 'ration_card', name: 'Ration Card', icon: '📋' },
  { id: 'driving_licence', name: 'Driving Licence', icon: '🚗' },
  { id: 'death_certificate', name: 'Death Certificate', icon: '📜' }
]

interface DocumentVerificationProps {
  onVerificationComplete?: () => void
}

export default function DocumentVerification({ onVerificationComplete }: DocumentVerificationProps) {
  const [selectedType, setSelectedType] = useState<string>('')
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [verifying, setVerifying] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')
  const [showSensitive, setShowSensitive] = useState(false)

  const handleUploadAndVerify = async () => {
    if (!file || !selectedType) return

    setError('')
    setUploading(true)
    
    try {
      const uploaded = await uploadDocument(file, file.name, `${DOCUMENT_TYPES.find(t => t.id === selectedType)?.name} verification`, selectedType)
      
      setUploading(false)
      setVerifying(true)
      
      const verified = await verifyIdDocument(uploaded.id)
      setResult(verified)
      
      if (onVerificationComplete) {
        onVerificationComplete()
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Verification failed')
    } finally {
      setUploading(false)
      setVerifying(false)
    }
  }

  const maskSensitiveValue = (value: string, fieldName: string): string => {
    if (showSensitive) return value

    if (fieldName.includes('aadhaar') || fieldName.includes('pan') || fieldName.includes('number')) {
      const len = value.length
      if (len <= 4) return '****'
      return '****' + value.slice(-4)
    }
    return value
  }

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { label: string; className: string }> = {
      verified: { label: 'Verified by Available Checks', className: 'status-verified' },
      suspicious: { label: 'Suspicious', className: 'status-suspicious' },
      manual_review: { label: 'Requires Manual Review', className: 'status-review' },
      rejected: { label: 'Possible Manipulation', className: 'status-rejected' }
    }
    return badges[status] || { label: 'Pending', className: 'status-pending' }
  }

  return (
    <div className="doc-verification-container">
      {!result ? (
        <>
          <div className="doc-type-selector">
            <h3>Select Document Type</h3>
            <div className="doc-types-grid">
              {DOCUMENT_TYPES.map(docType => (
                <div
                  key={docType.id}
                  className={`doc-type-card ${selectedType === docType.id ? 'selected' : ''}`}
                  onClick={() => setSelectedType(docType.id)}
                >
                  <span className="doc-icon">{docType.icon}</span>
                  <span className="doc-name">{docType.name}</span>
                </div>
              ))}
            </div>
          </div>

          {selectedType && (
            <div className="doc-upload-area">
              <h3><Upload size={20} /> Upload {DOCUMENT_TYPES.find(t => t.id === selectedType)?.name}</h3>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                disabled={uploading || verifying}
              />
              {file && (
                <div className="file-preview">
                  <FileText size={16} />
                  <span>{file.name}</span>
                </div>
              )}
              <button
                onClick={handleUploadAndVerify}
                disabled={!file || uploading || verifying}
                className="verify-btn"
              >
                {uploading ? 'Uploading...' : verifying ? 'Analyzing Document...' : 'Upload & Verify'}
              </button>
              {error && <div className="error-msg">{error}</div>}
            </div>
          )}

          {verifying && (
            <div className="processing-steps">
              <div className="step">📤 Uploading document...</div>
              <div className="step active">🔍 Extracting text (OCR)...</div>
              <div className="step">📋 Detecting document type...</div>
              <div className="step">🔬 Checking structure...</div>
              <div className="step">🛡️ Analyzing authenticity...</div>
              <div className="step">✅ Generating report...</div>
            </div>
          )}
        </>
      ) : (
        <div className="doc-result">
          <div className="result-header">
            <h2>Verification Report</h2>
            <button onClick={() => { setResult(null); setFile(null); setSelectedType('') }} className="new-verification-btn">
              New Verification
            </button>
          </div>

          <div className={`overall-status ${result.status}`}>
            <Shield size={32} />
            <h3>{getStatusBadge(result.status).label}</h3>
            {result.document_verification_result?.confidence_score && (
              <div className="confidence">
                Confidence: {result.document_verification_result.confidence_score.toFixed(0)}%
              </div>
            )}
          </div>

          {result.document_verification_result && (
            <>
              <div className="doc-info-section">
                <h4>Document Information</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">Selected Type:</span>
                    <span className="value">{result.document_type || 'Not specified'}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Detected Type:</span>
                    <span className="value">
                      {result.document_verification_result.document_type_detected || 'Not detected'}
                      {result.document_verification_result.document_type_match ? ' ✓' : 
                       result.document_verification_result.document_type_detected ? ' ⚠️ Mismatch' : ''}
                    </span>
                  </div>
                </div>
              </div>

              {Object.keys(result.document_verification_result.extracted_fields || {}).length > 0 && (
                <div className="extracted-fields-section">
                  <div className="section-header">
                    <h4>Extracted Information</h4>
                    <button onClick={() => setShowSensitive(!showSensitive)} className="toggle-btn">
                      {showSensitive ? <EyeOff size={16} /> : <Eye size={16} />}
                      {showSensitive ? 'Hide' : 'Show'} Sensitive Data
                    </button>
                  </div>
                  <div className="fields-grid">
                    {Object.entries(result.document_verification_result.extracted_fields).map(([key, value]: [string, any]) => (
                      <div key={key} className="field-item">
                        <span className="field-label">{key.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())}:</span>
                        <span className="field-value">
                          {value ? maskSensitiveValue(String(value), key) : 'Not detected'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="checks-section">
                <h4>Verification Checks</h4>
                <div className="checks-list">
                  <div className={`check-item ${result.document_verification_result.structure_check.detected ? 'pass' : 'fail'}`}>
                    <div className="check-name">{result.document_verification_result.structure_check.name}</div>
                    <div className="check-status">{result.document_verification_result.structure_check.detected ? '✓' : '✗'}</div>
                    <div className="check-details">{result.document_verification_result.structure_check.details}</div>
                  </div>
                  
                  <div className={`check-item ${result.document_verification_result.manipulation_check.detected ? 'fail' : 'pass'}`}>
                    <div className="check-name">{result.document_verification_result.manipulation_check.name}</div>
                    <div className="check-status">{result.document_verification_result.manipulation_check.detected ? '⚠️' : '✓'}</div>
                    <div className="check-details">{result.document_verification_result.manipulation_check.details}</div>
                  </div>
                  
                  <div className={`check-item ${result.document_verification_result.text_consistency.detected ? 'pass' : 'fail'}`}>
                    <div className="check-name">{result.document_verification_result.text_consistency.name}</div>
                    <div className="check-status">{result.document_verification_result.text_consistency.detected ? '✓' : '⚠️'}</div>
                    <div className="check-details">{result.document_verification_result.text_consistency.details}</div>
                  </div>
                </div>
              </div>

              {result.document_verification_result.limitations && result.document_verification_result.limitations.length > 0 && (
                <div className="limitations-section">
                  <h4>Limitations</h4>
                  <ul>
                    {result.document_verification_result.limitations.map((limitation: string, idx: number) => (
                      <li key={idx}>{limitation}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  )
}
