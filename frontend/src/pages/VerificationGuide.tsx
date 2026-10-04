import { Shield, Camera, FileText, Zap, Eye, Globe, CheckCircle, AlertTriangle, Info } from 'lucide-react'
import './VerificationGuide.css'

export default function VerificationGuide() {
  return (
    <div className="guide-container">
      <div className="guide-header">
        <Shield size={48} className="guide-icon" />
        <h1>Image Verification Guide</h1>
        <p className="guide-subtitle">Understanding digital image authenticity verification</p>
      </div>

      <div className="guide-content">
        <section className="guide-section">
          <div className="section-header">
            <Info size={24} />
            <h2>What is Image Verification?</h2>
          </div>
          <p>
            Image verification analyzes multiple technical and contextual signals to assess authenticity.
            It examines metadata, file structure, compression patterns, and visual indicators rather than
            relying on a single factor. Results are analytical assessments, not absolute guarantees.
          </p>
        </section>

        <section className="guide-section">
          <div className="section-header">
            <Camera size={24} />
            <h2>Metadata Analysis</h2>
          </div>
          <div className="info-box">
            <h3>What We Check:</h3>
            <ul>
              <li><strong>EXIF metadata:</strong> Camera make/model, lens, settings</li>
              <li><strong>Timestamps:</strong> Creation and modification dates</li>
              <li><strong>Software tags:</strong> Editing software indicators</li>
              <li><strong>GPS data:</strong> Location information if present</li>
            </ul>
          </div>
          <div className="warning-box">
            <AlertTriangle size={18} />
            <p><strong>Important:</strong> Missing metadata alone does NOT prove an image is fake. 
            Screenshots, social media uploads, and privacy-conscious tools often strip metadata.</p>
          </div>
        </section>

        <section className="guide-section">
          <div className="section-header">
            <FileText size={24} />
            <h2>File Structure & Integrity</h2>
          </div>
          <p>We analyze:</p>
          <ul>
            <li>File format and encoding properties</li>
            <li>Internal structure consistency</li>
            <li>File hash for integrity verification</li>
            <li>Corruption or unusual properties</li>
          </ul>
          <p className="note">
            A modified hash indicates the file changed after initial upload or capture.
          </p>
        </section>

        <section className="guide-section">
          <div className="section-header">
            <Zap size={24} />
            <h2>Compression Analysis</h2>
          </div>
          <p>Compression patterns can reveal editing:</p>
          <ul>
            <li><strong>JPEG compression:</strong> Natural photos typically show uniform compression</li>
            <li><strong>Recompression:</strong> Multiple save cycles create characteristic artifacts</li>
            <li><strong>Block inconsistencies:</strong> Edited regions may show different compression levels</li>
          </ul>
          <div className="warning-box">
            <AlertTriangle size={18} />
            <p><strong>Note:</strong> Compression artifacts alone do NOT prove manipulation. Social media
            platforms routinely recompress images.</p>
          </div>
        </section>

        <section className="guide-section">
          <div className="section-header">
            <Eye size={24} />
            <h2>Visual Manipulation Indicators</h2>
          </div>
          <p>Common visual indicators include:</p>
          <div className="indicators-grid">
            <div className="indicator-card">
              <h4>Lighting & Shadows</h4>
              <p>Inconsistent light direction or shadow angles</p>
            </div>
            <div className="indicator-card">
              <h4>Edge Artifacts</h4>
              <p>Unnatural or blurred edges around objects</p>
            </div>
            <div className="indicator-card">
              <h4>Clone Detection</h4>
              <p>Repeated or duplicated image regions</p>
            </div>
            <div className="indicator-card">
              <h4>Texture Patterns</h4>
              <p>Unnatural or repetitive textures</p>
            </div>
          </div>
        </section>

        <section className="guide-section highlight">
          <div className="section-header">
            <Shield size={24} />
            <h2>AI-Generated Image Indicators</h2>
          </div>
          <p>Synthetic images may exhibit:</p>
          <ul>
            <li>Unnatural fine details or blur in unexpected areas</li>
            <li>Inconsistent or nonsensical text</li>
            <li>Strange object geometry or proportions</li>
            <li>Unusual facial features or hand anatomy</li>
            <li>Inconsistent reflections or lighting</li>
            <li>Repetitive texture patterns</li>
            <li>Generation artifacts or "AI fingerprints"</li>
          </ul>
          <div className="warning-box critical">
            <AlertTriangle size={18} />
            <p><strong>Critical Note:</strong> Visual inspection alone cannot reliably prove AI generation.
            Modern AI models produce highly realistic images. Definitive detection requires specialized
            machine learning models trained on synthetic image datasets.</p>
          </div>
        </section>

        <section className="guide-section">
          <div className="section-header">
            <Globe size={24} />
            <h2>Source & Cross-Validation</h2>
          </div>
          <p>
            Comparing images against trusted sources (official websites, verified accounts, news agencies)
            increases confidence in authenticity. Reverse image search can reveal earlier versions,
            modifications, or original sources.
          </p>
        </section>

        <section className="guide-section">
          <div className="section-header">
            <CheckCircle size={24} />
            <h2>Understanding Results</h2>
          </div>
          <div className="results-explanation">
            <div className="result-item verified">
              <h3>✓ Verified</h3>
              <p>Passed available authenticity checks. No suspicious indicators detected in analyzed signals.</p>
            </div>
            <div className="result-item suspicious">
              <h3>⚠ Suspicious</h3>
              <p>Risk indicators detected. Requires further review or additional verification methods.</p>
            </div>
            <div className="result-item manipulated">
              <h3>✗ Likely Manipulated</h3>
              <p>Strong evidence of modification or manipulation detected.</p>
            </div>
            <div className="result-item inconclusive">
              <h3>? Inconclusive</h3>
              <p>Insufficient data for automated classification. Manual review recommended.</p>
            </div>
          </div>
          <p className="disclaimer">
            <strong>Remember:</strong> These results are analytical assessments based on available signals,
            not absolute guarantees. Verification is one tool in determining authenticity.
          </p>
        </section>

        <section className="guide-section">
          <div className="section-header">
            <Info size={24} />
            <h2>Best Practices for Users</h2>
          </div>
          <ul className="best-practices">
            <li>Upload the <strong>original file</strong> when possible, not screenshots or re-encoded copies</li>
            <li>Preserve original metadata - avoid unnecessary editing or format conversion</li>
            <li>Compare suspicious images with trusted sources when available</li>
            <li>Treat "Suspicious" results as requiring further investigation, not as final proof</li>
            <li>Consider the context: Who shared it? What's the claimed source? Does it seem plausible?</li>
            <li>For critical decisions, seek expert human verification</li>
          </ul>
        </section>

        <section className="guide-section">
          <div className="section-header">
            <Shield size={24} />
            <h2>Privacy & Security</h2>
          </div>
          <p>
            <strong>File Storage:</strong> Uploaded files are stored on the server for verification purposes.
            Files are associated with your account and accessible only to you.
          </p>
          <p>
            <strong>Metadata:</strong> Analysis examines file metadata but does not share it externally.
          </p>
          <p>
            <strong>Data Retention:</strong> You can delete uploaded files at any time from your dashboard.
          </p>
        </section>
      </div>
    </div>
  )
}
