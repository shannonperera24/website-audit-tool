export default function SkeletonLoader() {
  return (
    <div className="skeleton-wrap">
      {/* Metrics skeleton */}
      <div className="panel skeleton-panel">
        <div className="sk sk-title" />
        <div className="sk sk-meta" />
        <div className="sk sk-meta short" />
        <div className="skeleton-grid">
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className="sk sk-card" />
          ))}
        </div>
      </div>

      {/* Insights skeleton */}
      <div className="panel skeleton-panel">
        <div className="sk sk-title" />
        <div className="sk sk-line" />
        <div className="sk sk-line" />
        <div className="sk sk-line short" />
        <div className="sk sk-line" />
        <div className="sk sk-line short" />
      </div>

      {/* Recommendations skeleton */}
      <div className="panel skeleton-panel">
        <div className="sk sk-title" />
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="sk sk-rec" />
        ))}
      </div>
    </div>
  )
}
