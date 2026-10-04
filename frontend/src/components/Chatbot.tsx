import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X, Send } from 'lucide-react'
import './Chatbot.css'

interface Message {
  id: string
  text: string
  sender: 'user' | 'assistant'
  timestamp: Date
}

const FAQ_RESPONSES: Record<string, string> = {
  'image_verification': `Image verification analyzes multiple signals:

• **File Integrity**: SHA256 hash verification
• **AI Detection**: Statistical analysis of color smoothness, texture patterns, noise levels, and dimensions
• **Metadata Analysis**: EXIF data presence and camera information
• **Format Analysis**: Image format and structure

The system provides:
- **Verified**: Passes available checks, no suspicious indicators
- **Suspicious**: AI generation or manipulation detected
- **Manual Review**: Insufficient data or weak signals

Note: Missing EXIF metadata or PNG format alone do NOT make an image suspicious.`,

  'suspicious': `"Suspicious" means the analysis detected risk indicators such as:

• AI generation signals (smooth textures, repetitive patterns, specific dimensions)
• Manipulation artifacts
• Synthetic EXIF metadata
• Multiple risk factors

**Important**: The result is based on available technical signals, not absolute proof. Some legitimate images may be flagged if they have unusual characteristics.`,

  'document_verification': `Document verification analyzes ID documents using:

• **OCR**: Extracts text from Aadhaar, PAN, Driving Licence, Ration Card, Death Certificate
• **Field Extraction**: Identifies document numbers, names, dates, addresses
• **Structure Check**: Validates document aspect ratio and layout
• **Manipulation Detection**: Checks for editing artifacts
• **Consistency**: Validates field formats and internal consistency

**Limitations**:
- No official government database verification
- OCR accuracy depends on image quality
- Cannot guarantee authenticity - visual checks only`,

  'authenticity_score': `The authenticity score is calculated from real analysis signals:

**75-95%**: Normal image characteristics, integrity verified, no suspicious indicators

**40-70%**: Weak AI signals detected, some risk factors, requires manual review

**0-40%**: Strong AI generation or manipulation detected

**null/Inconclusive**: Insufficient data for reliable scoring

Scores are estimates based on available checks, not guarantees. A high score means "passed available checks" - not proof of absolute authenticity.`,

  'ai_detection': `AI-generated image detection uses statistical analysis:

**What we check**:
• Color smoothness (AI images are often unnaturally smooth)
• Texture repetition patterns
• Noise levels (AI images are too clean)
• Dimensions (512x512, 768x768, divisible by 64)
• EXIF software tags (Stable Diffusion, Midjourney markers)

**Limitations**:
- No trained ML model - statistical analysis only
- Cannot detect all AI-generated images
- Sophisticated AI with added noise may evade detection
- Some heavily edited real photos may trigger false positives

Results labeled as "Possible AI" or "Detected with X% confidence" reflect analysis uncertainty.`,

  'documents': `You can verify these document types:

• **Aadhaar Card**: Extracts number, name, DOB, gender, address
• **PAN Card**: Extracts PAN number, name, DOB
• **Ration Card**: Extracts card number, names, address
• **Driving Licence**: Extracts DL number, DOB, validity dates
• **Death Certificate**: Extracts registration number, date of death

Sensitive numbers are masked by default (shows ****1234). Use the toggle to reveal.`
}

const QUICK_QUESTIONS = [
  { id: 'image_verification', label: 'How does image verification work?' },
  { id: 'suspicious', label: 'What does Suspicious mean?' },
  { id: 'document_verification', label: 'How are documents verified?' },
  { id: 'authenticity_score', label: 'What does the authenticity score mean?' },
  { id: 'ai_detection', label: 'How can I identify AI-generated images?' },
  { id: 'documents', label: 'What documents can I verify?' }
]

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hi! I\'m your Verification Assistant. I can help you understand how image and document verification works. Choose a question below or ask me anything!',
      sender: 'assistant',
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const findBestResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase()
    
    // Direct matches
    if (lowerQuery.includes('image') && (lowerQuery.includes('verification') || lowerQuery.includes('verify') || lowerQuery.includes('work'))) {
      return FAQ_RESPONSES.image_verification
    }
    if (lowerQuery.includes('suspicious') || lowerQuery.includes('suspect')) {
      return FAQ_RESPONSES.suspicious
    }
    if (lowerQuery.includes('document') && (lowerQuery.includes('verification') || lowerQuery.includes('verify'))) {
      return FAQ_RESPONSES.document_verification
    }
    if (lowerQuery.includes('authenticity') || lowerQuery.includes('score') || lowerQuery.includes('percentage')) {
      return FAQ_RESPONSES.authenticity_score
    }
    if (lowerQuery.includes('ai') && (lowerQuery.includes('detect') || lowerQuery.includes('identify') || lowerQuery.includes('generated'))) {
      return FAQ_RESPONSES.ai_detection
    }
    if (lowerQuery.includes('aadhaar') || lowerQuery.includes('pan') || lowerQuery.includes('ration') || lowerQuery.includes('driving') || lowerQuery.includes('death')) {
      return FAQ_RESPONSES.documents
    }
    
    // Partial matches
    if (lowerQuery.includes('how') && lowerQuery.includes('work')) {
      return FAQ_RESPONSES.image_verification
    }
    if (lowerQuery.includes('what') && lowerQuery.includes('mean')) {
      return FAQ_RESPONSES.authenticity_score
    }
    if (lowerQuery.includes('can') && lowerQuery.includes('verify')) {
      return FAQ_RESPONSES.documents
    }
    
    return `I can help you with:

• Image verification process
• Document verification (Aadhaar, PAN, etc.)
• Understanding verification results
• AI-generated image detection
• Authenticity scores

Please choose from the quick questions above or ask about a specific topic.`
  }

  const handleSendMessage = (text?: string) => {
    const messageText = text || inputText.trim()
    if (!messageText) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputText('')
    setIsTyping(true)

    setTimeout(() => {
      const response = findBestResponse(messageText)
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        sender: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, assistantMessage])
      setIsTyping(false)
    }, 800)
  }

  const handleQuickQuestion = (questionId: string) => {
    const question = QUICK_QUESTIONS.find(q => q.id === questionId)
    if (question) {
      handleSendMessage(question.label)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <>
      {!isOpen && (
        <button className="chatbot-trigger" onClick={() => setIsOpen(true)} aria-label="Open chat">
          <MessageCircle size={24} />
        </button>
      )}

      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <div>
              <h3>Verification Assistant</h3>
              <p>Ask me about document & media verification</p>
            </div>
            <button onClick={() => setIsOpen(false)} aria-label="Close chat">
              <X size={20} />
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.map(message => (
              <div key={message.id} className={`message ${message.sender}`}>
                <div className="message-bubble">
                  {message.text.split('\n').map((line, idx) => (
                    <p key={idx}>{line}</p>
                  ))}
                </div>
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            ))}
            {isTyping && (
              <div className="message assistant">
                <div className="message-bubble typing">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="quick-questions">
            {QUICK_QUESTIONS.map(q => (
              <button key={q.id} onClick={() => handleQuickQuestion(q.id)} className="quick-question-btn">
                {q.label}
              </button>
            ))}
          </div>

          <div className="chatbot-input">
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question..."
              disabled={isTyping}
            />
            <button onClick={() => handleSendMessage()} disabled={!inputText.trim() || isTyping} aria-label="Send message">
              <Send size={20} />
            </button>
          </div>
        </div>
      )}
    </>
  )
}
