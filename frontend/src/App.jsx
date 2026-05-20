import { useState, useEffect, useRef } from 'react'
import {
  Database, AlertCircle, HelpCircle, Layers, BarChart2,
  Send, Globe, Loader2, ChevronRight, Activity, Clock, Hash,
  CheckCircle2, XCircle, ShieldAlert,
} from 'lucide-react'

import scoresJson from '@root/viz/scores.json'
import {
  classifyQuestion, scoreResponse, peerStatusForSection, SECTION_LABELS,
} from './metrics.js'

const API_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api/chat'

const SUGGESTIONS = [
  { label: 'Total record count?',       icon: Database    },
  { label: 'Which columns have nulls?', icon: AlertCircle },
  { label: 'Why is data missing?',      icon: HelpCircle  },
  { label: 'List all schema columns',   icon: Layers      },
  { label: 'Geometry metrics status?',  icon: BarChart2   },
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
  const [metrics, setMetrics]   = useState(null)
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

    const classification = classifyQuestion(active)
    const peer = peerStatusForSection(scoresJson, classification.section)
    setMetrics({ stage: 'pending', classification, peer })
    setMessages((prev) => [...prev, { role: 'user', text: active }])
    setLoading(true)

    try {
      const res  = await fetch(API_URL, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ query: active }),
      })
      const data = await res.json()
      const reply = data.reply ?? data.error ?? '(empty response)'
      const grounding = scoreResponse(reply)
      setMessages((prev) => [...prev, { role: 'bot', text: reply }])
      setMetrics({
        stage: 'done',
        classification, peer, grounding,
        latencyMs: data.latency_ms,
        tokens:    data.tokens,
        model:     data.model,
      })
    } catch {
      setMessages((prev) => [...prev, {
        role: 'bot',
        text: `⚠️ Connection error — backend at ${API_URL} unreachable.`,
      }])
      setMetrics({ stage: 'error', classification, peer })
    }
    setLoading(false)
  }

  const onKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit() }
  }

  return (
    <div style={styles.root}>
      <div style={styles.grid} aria-hidden="true" />

      <div style={styles.layout}>

        <header style={styles.header}>
          <div style={styles.badge}>
            <span style={styles.dot} />
            Overture Maps · Metrics Snapshot
          </div>
          <h1 style={styles.h1}>
            Dashboards are <span style={styles.accent}>Dead</span>
          </h1>
          <p style={styles.sub}>
            Natural-language access to your Overture dataset — no SQL required.
          </p>
        </header>

        <div style={styles.split}>
          {/* ── CHAT COLUMN ── */}
          <div style={styles.chatCol}>
            <div style={styles.panel}>
              <div style={styles.feed}>
                {messages.length === 0 && (
                  <div style={styles.empty}>
                    <Globe size={28} color="rgba(0,217,163,0.5)" strokeWidth={1.5} />
                    <p style={styles.emptyText}>
                      Ask anything about the Overture dataset.
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

              <div style={styles.chips}>
                {SUGGESTIONS.map(({ label, icon: Icon }, i) => (
                  <button
                    key={i}
                    onClick={() => handleSubmit(label)}
                    style={styles.chip}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'rgba(0,217,163,0.6)'
                      e.currentTarget.style.color       = '#00D9A3'
                      e.currentTarget.style.background  = 'rgba(0,217,163,0.06)'
                    }}
                    onMouseLeave={(e) => {
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

            <div style={styles.inputRow}>
              <div style={styles.inputWrap}>
                <input
                  ref={inputRef}
                  style={styles.input}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
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
          </div>

          {/* ── METRICS SIDEBAR ── */}
          <aside style={styles.sidebar}>
            <MetricsPanel metrics={metrics} loading={loading} />
          </aside>
        </div>

        <footer style={styles.footer}>
          573,795 rows · 23 columns · Overture Maps Metrics Snapshot
        </footer>
      </div>

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

/* ────────────────────────────── metrics panel ───────────────────────────── */

function MetricsPanel({ metrics, loading }) {
  if (!metrics) {
    return (
      <div style={styles.sidebarCard}>
        <div style={styles.sidebarHeading}>
          <Activity size={13} strokeWidth={2} />
          <span>Response metrics</span>
        </div>
        <p style={styles.sidebarMuted}>
          Send a question to see how the rubric classifies it and how
          context_perfect compares to peer files.
        </p>
      </div>
    )
  }

  const { classification, peer, grounding, latencyMs, tokens, model, stage } = metrics
  const sectionLabel = SECTION_LABELS[classification.section]
  const peerRisky = (peer.RISKY || 0) + (peer.UNKNOWN || 0)

  return (
    <div style={styles.sidebarCard}>
      <div style={styles.sidebarHeading}>
        <Activity size={13} strokeWidth={2} />
        <span>Response metrics</span>
      </div>

      <Row label="Rubric section" value={sectionLabel} />
      <Row
        label="context_perfect"
        value={<Pill text="SUPPORTED" tone="good" />}
      />
      <Row
        label="Peer files"
        value={
          peerRisky > 0
            ? <Pill text={`RISKY on ${peerRisky}/${peer.peers}`} tone="warn" />
            : <Pill text={`SUPPORTED on ${peer.SUPPORTED}/${peer.peers}`} tone="good" />
        }
      />

      {classification.hits.length > 0 && (
        <div style={styles.hitsBox}>
          <span style={styles.hitsLabel}>Keyword hits</span>
          <div style={styles.hitChips}>
            {classification.hits.slice(0, 6).map((h) => (
              <span key={h} style={styles.hitChip}>{h}</span>
            ))}
          </div>
        </div>
      )}

      <div style={styles.divider} />

      {stage === 'pending' || loading ? (
        <div style={styles.sidebarMuted}>Waiting for response…</div>
      ) : stage === 'error' ? (
        <div style={{ ...styles.sidebarMuted, color: '#F2545B' }}>
          Backend unreachable.
        </div>
      ) : (
        <>
          <Row
            label={<><Clock size={11} style={{ marginRight: 4 }} />Latency</>}
            value={latencyMs != null ? `${latencyMs} ms` : '—'}
          />
          <Row
            label={<><Hash size={11} style={{ marginRight: 4 }} />Tokens</>}
            value={tokens?.total != null
              ? `${tokens.total} (${tokens.prompt}+${tokens.completion})`
              : '—'}
          />
          <Row label="Model" value={model || '—'} />

          <div style={styles.divider} />

          <div style={styles.sidebarHeading}>
            <ShieldAlert size={13} strokeWidth={2} />
            <span>Grounding</span>
          </div>
          <Row
            label="Numbers cited"
            value={
              <Pill
                text={String(grounding?.numbersCited ?? 0)}
                tone={(grounding?.numbersCited ?? 0) > 0 ? 'good' : 'muted'}
              />
            }
          />
          <Row
            label="Properly refused"
            value={
              grounding?.refused
                ? <Pill text="yes" tone="good" icon={CheckCircle2} />
                : <Pill text="no" tone="muted" icon={XCircle} />
            }
          />
          <Row
            label="Speculation"
            value={
              grounding?.speculationHits?.length
                ? <Pill text={grounding.speculationHits.length + ' flags'} tone="warn" />
                : <Pill text="clean" tone="good" />
            }
          />
        </>
      )}
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div style={styles.row}>
      <span style={styles.rowLabel}>{label}</span>
      <span style={styles.rowValue}>{value}</span>
    </div>
  )
}

function Pill({ text, tone = 'muted', icon: Icon }) {
  const palette = {
    good:  { bg: 'rgba(0,217,163,0.12)', bd: 'rgba(0,217,163,0.4)', fg: '#00D9A3' },
    warn:  { bg: 'rgba(242,166,90,0.12)', bd: 'rgba(242,166,90,0.4)', fg: '#F2A65A' },
    bad:   { bg: 'rgba(242,84,91,0.12)',  bd: 'rgba(242,84,91,0.4)',  fg: '#F2545B' },
    muted: { bg: 'rgba(255,255,255,0.05)', bd: 'rgba(255,255,255,0.1)', fg: 'rgba(255,255,255,0.7)' },
  }[tone]
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      padding: '2px 8px',
      borderRadius: 100,
      fontSize: 10,
      fontFamily: "'Space Mono', monospace",
      letterSpacing: '0.04em',
      textTransform: 'uppercase',
      background: palette.bg,
      border: `1px solid ${palette.bd}`,
      color: palette.fg,
    }}>
      {Icon && <Icon size={10} strokeWidth={2} />}
      {text}
    </span>
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
    width: '100%', maxWidth: 1120,
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
  split: {
    display: 'grid',
    gridTemplateColumns: 'minmax(0, 1fr) 320px',
    gap: '1.25rem',
    alignItems: 'stretch',
  },
  chatCol: {
    display: 'flex', flexDirection: 'column', gap: '1rem',
    minWidth: 0,
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
  sidebar: {
    minWidth: 0,
  },
  sidebarCard: {
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.07)',
    borderRadius: 20,
    padding: '1.25rem',
    display: 'flex', flexDirection: 'column', gap: 10,
    height: '100%',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    boxShadow: '0 0 0 1px rgba(0,217,163,0.05), 0 24px 64px rgba(0,0,0,0.6)',
  },
  sidebarHeading: {
    display: 'flex', alignItems: 'center', gap: 6,
    fontSize: 11,
    fontFamily: "'Space Mono', monospace",
    color: '#00D9A3',
    letterSpacing: '0.06em',
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  sidebarMuted: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.4)',
    lineHeight: 1.6,
  },
  row: {
    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    gap: 8,
    fontSize: 12,
    padding: '4px 0',
  },
  rowLabel: {
    color: 'rgba(255,255,255,0.5)',
    fontFamily: "'Space Mono', monospace",
    fontSize: 11,
    letterSpacing: '0.02em',
    display: 'inline-flex', alignItems: 'center',
  },
  rowValue: {
    color: 'rgba(255,255,255,0.9)',
    fontFamily: "'DM Sans', system-ui, sans-serif",
    fontSize: 12,
    fontWeight: 500,
    textAlign: 'right',
  },
  hitsBox: {
    paddingTop: 6,
  },
  hitsLabel: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.4)',
    fontFamily: "'Space Mono', monospace",
    letterSpacing: '0.04em',
    textTransform: 'uppercase',
  },
  hitChips: {
    display: 'flex', flexWrap: 'wrap', gap: 4,
    marginTop: 6,
  },
  hitChip: {
    fontSize: 10,
    fontFamily: "'Space Mono', monospace",
    padding: '2px 6px',
    borderRadius: 4,
    background: 'rgba(79,157,255,0.08)',
    color: 'rgba(79,157,255,0.85)',
    border: '1px solid rgba(79,157,255,0.2)',
  },
  divider: {
    height: 1,
    background: 'rgba(255,255,255,0.06)',
    margin: '6px 0',
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
