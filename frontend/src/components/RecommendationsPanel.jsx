export default function RecommendationsPanel({ recommendations }) {
  return (
    <div className="panel recommendations-panel">
      <h2 className="panel-title">Recommendations</h2>
      <p className="panel-subtitle">Prioritized actions based on audit findings</p>
      <ol className="recommendations-list">
        {recommendations.map((rec) => (
          <li key={rec.priority} className={`rec-item priority-${rec.priority}`}>
            <div className="rec-header">
              <span className="rec-priority">#{rec.priority}</span>
              <h3 className="rec-title">{rec.title}</h3>
            </div>
            <p className="rec-reasoning">{rec.reasoning}</p>
          </li>
        ))}
      </ol>
    </div>
  )
}
