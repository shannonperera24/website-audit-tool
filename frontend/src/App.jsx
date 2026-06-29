import { useState } from 'react'
import UrlForm from './components/UrlForm'
import MetricsPanel from './components/MetricsPanel'
import InsightsPanel from './components/InsightsPanel'
import RecommendationsPanel from './components/RecommendationsPanel'
import SkeletonLoader from './components/SkeletonLoader'

export default function App() {
  const [audit, setAudit] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-inner">
          <div className="header-eyebrow">EIGHT25MEDIA</div>
          <h1 className="app-title">Website Audit Tool</h1>
          <p className="app-subtitle">
            Paste any URL to extract page metrics and generate AI-powered SEO &amp; UX insights.
          </p>
          <UrlForm onResult={setAudit} onLoading={setLoading} onError={setError} />
          {error && <div className="error-banner">{error}</div>}
        </div>
      </header>

      <main className="app-main">
        {loading && <SkeletonLoader />}

        {audit && !loading && (
          <div className="results">
            <div className="results-url">
              Audit for{' '}
              <a href={audit.url} target="_blank" rel="noreferrer">
                {audit.url}
              </a>
            </div>
            <MetricsPanel audit={audit} />
            <InsightsPanel insights={audit.ai_insights} />
            <RecommendationsPanel recommendations={audit.recommendations} />
          </div>
        )}
      </main>
    </div>
  )
}
