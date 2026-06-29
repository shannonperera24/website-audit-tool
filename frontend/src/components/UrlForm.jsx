import { useState } from 'react'
import { runAudit } from '../api/auditApi'

export default function UrlForm({ onResult, onLoading, onError }) {
  const [url, setUrl] = useState('')

  const handleSubmit = async () => {
    const trimmed = url.trim()
    if (!trimmed) return

    onLoading(true)
    onError(null)
    onResult(null)

    try {
      const data = await runAudit(trimmed)
      onResult(data)
    } catch (err) {
      const message =
        err.response?.data?.error ||
        err.response?.data?.url?.[0] ||
        'Something went wrong. Check the URL and try again.'
      onError(message)
    } finally {
      onLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleSubmit()
  }

  return (
    <div className="url-form">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="https://example.com"
        className="url-input"
      />
      <button onClick={handleSubmit} className="submit-btn">
        Run Audit
      </button>
    </div>
  )
}
