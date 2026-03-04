import { useState } from 'react'
import './App.css'

const API_BASE = ''

function formatHikeStartForApi(dateStr: string, timeStr: string): string {
  if (!dateStr || !timeStr) return ''
  const d = new Date(dateStr + 'T' + timeStr)
  const options: Intl.DateTimeFormatOptions = {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
  }
  return d.toLocaleDateString('en-US', options)
}

function parsePlanOutput(output: string): { tripSummary: string; socialPost: string } {
  const tripMatch = output.match(/(?:1\)\s*)?TRIP SUMMARY:?\s*([\s\S]*?)(?=2\)\s*SOCIAL POST:|SOCIAL POST:|\z)/i)
  const socialMatch = output.match(/(?:2\)\s*)?SOCIAL POST:?\s*([\s\S]*?)$/im)
  const tripSummary = tripMatch ? tripMatch[1].trim() : ''
  const socialPost = socialMatch ? socialMatch[1].trim() : output
  return { tripSummary, socialPost }
}

export default function App() {
  const [homeAddress, setHomeAddress] = useState('')
  const [hikeDate, setHikeDate] = useState('')
  const [hikeTime, setHikeTime] = useState('09:00')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setResult(null)
    if (!homeAddress.trim()) {
      setError('Please enter your home address.')
      return
    }
    setLoading(true)
    try {
      const hikeStart = formatHikeStartForApi(hikeDate, hikeTime)
      const res = await fetch(`${API_BASE}/api/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          home_address: homeAddress.trim(),
          hike_start: hikeStart,
        }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        setError(data.detail || res.statusText || 'Request failed')
        return
      }
      setResult(data.output ?? '')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Network error')
    } finally {
      setLoading(false)
    }
  }

  const parsed = result ? parsePlanOutput(result) : null

  return (
    <div className="app">
      <header className="hero">
        <h1 className="title">Trail Plan</h1>
        <p className="tagline">Plan your hike. Get trails, weather, and a post to invite friends.</p>
      </header>

      <main className="main">
        <form className="card form-card" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="address">Home address</label>
            <input
              id="address"
              type="text"
              placeholder="e.g. 123 Main St, Vancouver, BC"
              value={homeAddress}
              onChange={(e) => setHomeAddress(e.target.value)}
              disabled={loading}
              autoComplete="street-address"
            />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="date">Hike start — day</label>
              <input
                id="date"
                type="date"
                value={hikeDate}
                onChange={(e) => setHikeDate(e.target.value)}
                disabled={loading}
              />
            </div>
            <div className="form-group">
              <label htmlFor="time">Time</label>
              <input
                id="time"
                type="time"
                value={hikeTime}
                onChange={(e) => setHikeTime(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn" disabled={loading}>
            {loading ? 'Planning…' : 'Plan my hike'}
          </button>
        </form>

        {parsed && (
          <div className="results">
            {parsed.tripSummary && (
              <section className="card result-card">
                <h2>Trip summary</h2>
                <div className="content prose">{parsed.tripSummary}</div>
              </section>
            )}
            {parsed.socialPost && (
              <section className="card result-card social">
                <h2>Invite friends</h2>
                <div className="content social-content">{parsed.socialPost}</div>
                <button
                  type="button"
                  className="btn secondary"
                  onClick={() => navigator.clipboard.writeText(parsed.socialPost)}
                >
                  Copy post
                </button>
              </section>
            )}
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Trails & weather near you · ETA from home · One tap to share</p>
      </footer>
    </div>
  )
}
