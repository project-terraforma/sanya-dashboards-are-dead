import { useState, useEffect, useRef } from 'react'
import {
  Database, AlertCircle, HelpCircle, Layers, BarChart2,
  Send, Globe, Loader2, ChevronRight
} from 'lucide-react'

const SUGGESTIONS = [
  { label: "Total record count?",       icon: Database   },
  { label: "Which columns have nulls?", icon: AlertCircle },
  { label: "Why is data missing?",      icon: HelpCircle  },
  { label: "List all schema columns",   icon: Layers      },
  { label: "Geometry metrics status?",  icon: BarChart2   },
]

const BotAvatar = () => (
  <div style={{
    width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
    background: 'linear-gradient(135deg, #00D9A3 0%, #0062FF 100%)',
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    boxShadow: '0 0 12px rgba(0,217,163,0.4)',
    marginTop: 2,
  }}>
    <Globe size={13} color="#fff" strokeWidth={2} />
  </div>
)

export default function App() {
  const [query, setQuery]       = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading]   = useState(false)
  const chatEndRef              = useRef(null)
  const inputRef                = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (userQuery) => {
    const active = (userQuery ?? query).trim()
    if (!active) return
    if (!userQuery) setQuery('')
    inputRef.current?.focus()

    setMessages(prev => [...prev, { role: 'user', text: active }])
    setLoading(true)

    try {
      const res  = await fetch('http://localhost:8000/api/chat', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ query: active }),
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'bot', text: data.reply }])
    } catch {
      setMessages(prev => [...prev, {
        role: 'bot', text: '⚠️ Connection error — is the backend running on :8000?'
      }])
    }
    setLoading(false)
  }

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit() }
  }

  return (
    <div style={styles.root}>
      {/* ── subtle grid overlay ── */}
      <div style={styles.grid} aria-hidden="true" />

      <div style={styles.layout}>

        {/* ── HEADER ── */}
        <header style={styles.header}>
          <div style={styles.badge}>
            <span style={styles.dot} />
            Overture Maps · Metrics Snapshot
          </div>
          <h1 style={styles.h1}>
            Dashboards are{' '}
            <span style={styles.accent}>Dead</span>
          </h1>
          <p style={styles.sub}>
            Natural-language access to your Overture dataset — no SQL required.
          </p>
        </header>

        {/* ── CHAT PANEL ── */}
        <div style={styles.panel}>

          {/* messages */}
          <div style={styles.feed}>
            {messages.length === 0 && (
              <div style={styles.empty}>
                <Globe size={28} color="rgba(0,217,163,0.5)" strokeWidth={1.5} />
                <p style={styles.emptyText}>
                  Ask anything about the Overture dataset statistics below.
                </p>
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i} style={{
                display: 'flex',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                alignItems: 'flex-start',
                gap: 10,
              }}>
                {msg.role === 'bot' && <BotAvatar />}
                <div style={msg.role === 'user' ? styles.bubbleUser : styles.bubbleBot}>
                  {msg.text}
                </div>
              </div>
            ))}

            {loading && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <BotAvatar />
                <div style={styles.thinking}>
                  <Loader2 size={13} color="#00D9A3"
                    style={{ animation: 'spin 1s linear infinite' }} />
                  <span>Thinking&hellip;</span>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* suggestion chips */}
          <div style={styles.chips}>
            {SUGGESTIONS.map(({ label, icon: Icon }, i) => (
              <button
                key={i}
                onClick={() => handleSubmit(label)}
                style={styles.chip}
                onMouseEnter={e => {
                  e.currentTarget.style.borderColor = 'rgba(0,217,163,0.6)'
                  e.currentTarget.style.color       = '#00D9A3'
                  e.currentTarget.style.background  = 'rgba(0,217,163,0.06)'
                }}
                onMouseLeave={e => {
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
                  e.currentTarget.style.color       = 'rgba(255,255,255,0.55)'
                  e.currentTarget.style.background  = 'transparent'
                }}
              >
                <Icon size={11} strokeWidth={2} style={{ flexShrink: 0 }} />
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* ── INPUT ROW ── */}
        <div style={styles.inputRow}>
          <div style={styles.inputWrap}>
            <input
              ref={inputRef}
              style={styles.input}
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={onKey}
              placeholder="Ask a question about the dataset…"
              autoComplete="off"
              spellCheck={false}
            />
          </div>
          <button
            onClick={() => handleSubmit()}
            disabled={loading || !query.trim()}
            style={{
              ...styles.sendBtn,
              opacity: (loading || !query.trim()) ? 0.4 : 1,
              cursor:  (loading || !query.trim()) ? 'not-allowed' : 'pointer',
            }}
            aria-label="Send"
          >
            {loading
              ? <Loader2 size={18} strokeWidth={2}
                  style={{ animation: 'spin 1s linear infinite' }} />
              : <><Send size={15} strokeWidth={2} /><ChevronRight size={13} strokeWidth={2} /></>
            }
          </button>
        </div>

        <footer style={styles.footer}>
          573,795 rows · 23 columns · Overture Maps Metrics Snapshot
        </footer>
      </div>

      {/* keyframe for spinner */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');
        @keyframes spin { to { transform: rotate(360deg) } }
        * { box-sizing: border-box; margin: 0; padding: 0 }
        body { background: #07090F; }
        ::-webkit-scrollbar { width: 4px }
        ::-webkit-scrollbar-track { background: transparent }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px }
      `}</style>
    </div>
  )
}

/* ────────────────────────────── styles ────────────────────────────── */
const styles = {
  root: {
    minHeight: '100vh',
    background: '#07090F',
    display: 'flex',
    justifyContent: 'center',
    padding: '2rem 1rem',
    fontFamily: "'DM Sans', system-ui, sans-serif",
    position: 'relative',
    overflow: 'hidden',
  },
  grid: {
    position: 'absolute', inset: 0, pointerEvents: 'none',
    backgroundImage: `
      linear-gradient(rgba(0,217,163,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,217,163,0.03) 1px, transparent 1px)
    `,
    backgroundSize: '48px 48px',
    maskImage: 'radial-gradient(ellipse 80% 80% at 50% 0%, black 30%, transparent 100%)',
  },
  layout: {
    width: '100%', maxWidth: 720,
    display: 'flex', flexDirection: 'column', gap: '1.5rem',
    position: 'relative', zIndex: 1,
  },
  header: {
    textAlign: 'center', paddingTop: '0.5rem',
  },
  badge: {
    display: 'inline-flex', alignItems: 'center', gap: 6,
    background: 'rgba(0,217,163,0.08)',
    border: '1px solid rgba(0,217,163,0.2)',
    borderRadius: 100,
    padding: '4px 12px',
    fontSize: 11,
    fontFamily: "'Space Mono', monospace",
    color: '#00D9A3',
    letterSpacing: '0.04em',
    marginBottom: '1rem',
  },
  dot: {
    width: 6, height: 6, borderRadius: '50%',
    background: '#00D9A3',
    boxShadow: '0 0 6px #00D9A3',
    display: 'inline-block',
  },
  h1: {
    fontSize: 'clamp(2rem, 5vw, 3rem)',
    fontWeight: 300,
    color: 'rgba(255,255,255,0.92)',
    letterSpacing: '-0.02em',
    lineHeight: 1.1,
    marginBottom: '0.75rem',
    fontFamily: "'DM Sans', system-ui, sans-serif",
  },
  accent: {
    fontWeight: 700,
    background: 'linear-gradient(90deg, #00D9A3 0%, #4F9DFF 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
  },
  sub: {
    fontSize: 14, color: 'rgba(255,255,255,0.4)',
    fontWeight: 300, letterSpacing: '0.01em',
  },
  panel: {
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.07)',
    borderRadius: 20,
    overflow: 'hidden',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    boxShadow: '0 0 0 1px rgba(0,217,163,0.05), 0 24px 64px rgba(0,0,0,0.6)',
  },
  feed: {
    minHeight: 320, maxHeight: 480,
    overflowY: 'auto',
    padding: '1.5rem',
    display: 'flex', flexDirection: 'column', gap: 16,
  },
  empty: {
    flex: 1, display: 'flex', flexDirection: 'column',
    alignItems: 'center', justifyContent: 'center',
    gap: 12, opacity: 0.6, paddingTop: 80, paddingBottom: 80,
  },
  emptyText: {
    fontSize: 13, color: 'rgba(255,255,255,0.4)',
    textAlign: 'center', maxWidth: 280, lineHeight: 1.6,
  },
  bubbleUser: {
    maxWidth: '80%',
    background: 'linear-gradient(135deg, rgba(0,217,163,0.2) 0%, rgba(79,157,255,0.2) 100%)',
    border: '1px solid rgba(0,217,163,0.25)',
    borderRadius: '16px 16px 4px 16px',
    padding: '10px 14px',
    fontSize: 14,
    lineHeight: 1.6,
    color: 'rgba(255,255,255,0.9)',
    fontFamily: "'DM Sans', system-ui, sans-serif",
  },
  bubbleBot: {
    maxWidth: '82%',
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '16px 16px 16px 4px',
    padding: '10px 14px',
    fontSize: 14,
    lineHeight: 1.7,
    color: 'rgba(255,255,255,0.8)',
    fontFamily: "'Space Mono', monospace",
    letterSpacing: '-0.01em',
    whiteSpace: 'pre-wrap',
    textAlign: 'left',
  },
  thinking: {
    display: 'flex', alignItems: 'center', gap: 8,
    fontSize: 12, color: 'rgba(0,217,163,0.7)',
    fontFamily: "'Space Mono', monospace",
    padding: '8px 12px',
    background: 'rgba(0,217,163,0.05)',
    border: '1px solid rgba(0,217,163,0.12)',
    borderRadius: '12px 12px 12px 4px',
  },
  chips: {
    display: 'flex', flexWrap: 'wrap', gap: 8,
    padding: '12px 16px',
    borderTop: '1px solid rgba(255,255,255,0.05)',
    background: 'rgba(0,0,0,0.2)',
  },
  chip: {
    display: 'inline-flex', alignItems: 'center', gap: 5,
    padding: '5px 12px',
    fontSize: 11,
    fontFamily: "'Space Mono', monospace",
    letterSpacing: '0.01em',
    color: 'rgba(255,255,255,0.55)',
    background: 'transparent',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: 100,
    cursor: 'pointer',
    transition: 'border-color 0.15s, color 0.15s, background 0.15s',
    whiteSpace: 'nowrap',
  },
  inputRow: {
    display: 'flex', gap: 10,
  },
  inputWrap: {
    flex: 1,
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: 14,
    overflow: 'hidden',
    transition: 'border-color 0.15s',
  },
  input: {
    width: '100%',
    background: 'transparent',
    border: 'none',
    outline: 'none',
    padding: '14px 16px',
    fontSize: 14,
    color: 'rgba(255,255,255,0.85)',
    fontFamily: "'DM Sans', system-ui, sans-serif",
    caretColor: '#00D9A3',
  },
  sendBtn: {
    display: 'flex', alignItems: 'center', gap: 2,
    padding: '0 20px',
    background: 'linear-gradient(135deg, #00D9A3 0%, #0062FF 100%)',
    border: 'none',
    borderRadius: 14,
    color: '#fff',
    fontWeight: 600,
    fontSize: 14,
    boxShadow: '0 0 20px rgba(0,217,163,0.3)',
    transition: 'opacity 0.15s, transform 0.1s',
    flexShrink: 0,
  },
  footer: {
    textAlign: 'center',
    fontSize: 11,
    fontFamily: "'Space Mono', monospace",
    color: 'rgba(255,255,255,0.2)',
    letterSpacing: '0.04em',
    paddingBottom: '0.5rem',
  },
}