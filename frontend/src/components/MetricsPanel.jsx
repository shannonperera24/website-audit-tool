import {
  FileText,
  Heading1,
  Heading2,
  Heading3,
  MousePointerClick,
  Link,
  ExternalLink,
  Image,
  AlertTriangle,
} from 'lucide-react'

const METRICS = [
  { key: 'word_count',           label: 'Word Count',           icon: FileText },
  { key: 'h1_count',             label: 'H1 Tags',              icon: Heading1 },
  { key: 'h2_count',             label: 'H2 Tags',              icon: Heading2 },
  { key: 'h3_count',             label: 'H3 Tags',              icon: Heading3 },
  { key: 'cta_count',            label: 'CTAs',                 icon: MousePointerClick },
  { key: 'internal_links',       label: 'Internal Links',       icon: Link },
  { key: 'external_links',       label: 'External Links',       icon: ExternalLink },
  { key: 'image_count',          label: 'Images',               icon: Image },
  { key: 'images_missing_alt',   label: 'Missing Alt Text',     icon: AlertTriangle, suffix: (a) => ` (${a.images_missing_alt_pct ?? 0}%)` },
]

export default function MetricsPanel({ audit }) {
  return (
    <div className="panel metrics-panel">
      <h2 className="panel-title">Page Metrics</h2>

      <div className="meta-block">
        <div className="meta-row">
          <span className="meta-label">Meta Title</span>
          <span className="meta-value">{audit.meta_title || '—'}</span>
        </div>
        <div className="meta-row">
          <span className="meta-label">Meta Description</span>
          <span className="meta-value">{audit.meta_description || '—'}</span>
        </div>
      </div>

      <div className="metrics-grid">
        {METRICS.map(({ key, label, icon: Icon, suffix }) => (
          <div key={key} className="metric-card">
            <div className="metric-icon">
              <Icon size={18} strokeWidth={2} />
            </div>
            <span className="metric-value">
              {audit[key]}
              {suffix ? suffix(audit) : ''}
            </span>
            <span className="metric-label">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
