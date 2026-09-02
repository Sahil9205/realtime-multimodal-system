import { useEffect, useRef } from 'react'
import { Mic, MicOff, Radio, RotateCcw, ShieldCheck, Wifi } from 'lucide-react'
import { useVoiceSession } from './useVoiceSession'

const statusCopy = {
  idle: 'Standby',
  connecting: 'Opening channel',
  ready: 'Ready to listen',
  recording: 'Listening live',
  thinking: 'Thinking',
  speaking: 'Alisha is speaking',
  error: 'Connection issue',
} as const

export default function App() {
  const { state, error, timeline, connect, disconnect, toggleRecording } = useVoiceSession()
  const transcriptRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    transcriptRef.current?.scrollTo({ top: transcriptRef.current.scrollHeight, behavior: 'smooth' })
  }, [timeline])

  return (
    <main className="voice-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark"><Radio size={18} strokeWidth={2.5} /></div>
          <div>
            <p className="eyebrow">Pipecat voice interface</p>
            <h1>Alisha<span>/</span>live</h1>
          </div>
        </div>
        <div className={`status-pill ${state}`}><span className="status-dot" />{statusCopy[state]}</div>
      </header>

      <section className="hero-grid">
        <section className="control-panel">
          <div className="panel-kicker"><Wifi size={14} /> REALTIME CHANNEL</div>
          <h2>Talk naturally.<br /><em>Stay present.</em></h2>
          <p className="lead">A direct voice line to your assistant, with live transcription and instant spoken replies.</p>

          <div className={`orb ${state}`}>
            <div className="orb-ring ring-one" />
            <div className="orb-ring ring-two" />
            <div className="orb-core"><span /></div>
            {(state === 'recording' || state === 'speaking') && <div className="sound-bars"><i /><i /><i /><i /><i /></div>}
          </div>

          <button className={`talk-button ${state}`} onClick={() => void toggleRecording()} disabled={state === 'connecting'}>
            {state === 'recording' ? <MicOff size={21} /> : <Mic size={21} />}
            <span>{state === 'recording' ? 'Stop listening' : state === 'speaking' ? 'Interrupt & speak' : 'Start speaking'}</span>
          </button>
          <p className="hint"><ShieldCheck size={14} /> Microphone audio is streamed securely to your local session.</p>
        </section>

        <section className="conversation-panel">
          <div className="conversation-head">
            <div><p className="eyebrow">Conversation stream</p><h3>Live transcript</h3></div>
            <button className="icon-button" onClick={() => disconnect()} title="Reset connection"><RotateCcw size={17} /></button>
          </div>
          <div className="timeline" ref={transcriptRef}>
            {timeline.length === 0 ? (
              <div className="empty-state"><div className="empty-icon"><Mic size={20} /></div><p>Your conversation will appear here.</p><span>Press start and say hello.</span></div>
            ) : timeline.map((item) => (
              <article className={`message ${item.role}`} key={item.id}>
                <span className="message-label">{item.role === 'user' ? 'YOU' : item.role === 'assistant' ? 'ALISHA' : 'SYSTEM'}</span>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
          <div className="connection-footer"><span><span className="mini-dot" /> {state === 'recording' ? 'Listening to you' : state === 'thinking' ? 'Preparing response' : state === 'speaking' ? 'Alisha is speaking' : 'Session ready'}</span><code>PCM · 16kHz</code></div>
        </section>
      </section>

      {(error || state === 'error') && <div className="error-toast">{error ?? 'Voice channel unavailable.'}</div>}
    </main>
  )
}
