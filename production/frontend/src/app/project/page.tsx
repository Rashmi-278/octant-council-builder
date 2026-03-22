'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import ReactMarkdown from 'react-markdown'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://optinpg-evaluator-production.up.railway.app'

interface OstromRule {
  label: string
  full_text?: string
  value: number
  confidence: string
}

interface RadarData {
  project: string
  overall_score: number
  governance_maturity?: string
  axes: OstromRule[]
}

function OstromRadar({ data }: { data: RadarData }) {
  const cx = 250, cy = 250, r = 180
  const n = data.axes.length
  if (n === 0) return null

  const angleStep = (2 * Math.PI) / n
  const startAngle = -Math.PI / 2 // Start from top

  const getPoint = (index: number, value: number) => {
    const angle = startAngle + index * angleStep
    const dist = (value / 100) * r
    return {
      x: cx + dist * Math.cos(angle),
      y: cy + dist * Math.sin(angle),
    }
  }

  const rings = [25, 50, 75, 100]

  return (
    <svg viewBox="0 0 500 500" className="w-full max-w-lg mx-auto">
      {/* Background rings */}
      {rings.map((pct) => {
        const ringR = (pct / 100) * r
        const points = Array.from({ length: n }, (_, i) => {
          const angle = startAngle + i * angleStep
          return `${cx + ringR * Math.cos(angle)},${cy + ringR * Math.sin(angle)}`
        }).join(' ')
        return (
          <polygon
            key={pct}
            points={points}
            fill="none"
            stroke="#334155"
            strokeWidth="1"
          />
        )
      })}

      {/* Axis lines */}
      {data.axes.map((_, i) => {
        const end = getPoint(i, 100)
        return (
          <line
            key={i}
            x1={cx} y1={cy}
            x2={end.x} y2={end.y}
            stroke="#334155"
            strokeWidth="1"
          />
        )
      })}

      {/* Data polygon */}
      <polygon
        points={data.axes.map((ax, i) => {
          const p = getPoint(i, ax.value)
          return `${p.x},${p.y}`
        }).join(' ')}
        fill="rgba(99, 102, 241, 0.2)"
        stroke="#6366f1"
        strokeWidth="2"
      />

      {/* Data points */}
      {data.axes.map((ax, i) => {
        const p = getPoint(i, ax.value)
        return (
          <circle
            key={i}
            cx={p.x} cy={p.y}
            r="4"
            fill="#6366f1"
          />
        )
      })}

      {/* Labels */}
      {data.axes.map((ax, i) => {
        const labelPoint = getPoint(i, 120)
        const angle = startAngle + i * angleStep
        const textAnchor = Math.abs(Math.cos(angle)) < 0.1
          ? 'middle'
          : Math.cos(angle) > 0 ? 'start' : 'end'
        return (
          <g key={i}>
            <text
              x={labelPoint.x}
              y={labelPoint.y}
              textAnchor={textAnchor}
              dominantBaseline="middle"
              className="text-xs"
              fill="#94a3b8"
              fontSize="10"
            >
              {ax.label.length > 20 ? ax.label.substring(0, 20) + '...' : ax.label}
            </text>
            <text
              x={getPoint(i, ax.value + 12).x}
              y={getPoint(i, ax.value + 12).y}
              textAnchor="middle"
              dominantBaseline="middle"
              fill="#6366f1"
              fontSize="11"
              fontWeight="bold"
            >
              {ax.value}
            </text>
          </g>
        )
      })}

      {/* Center score */}
      <text x={cx} y={cy - 10} textAnchor="middle" fill="#f8fafc" fontSize="28" fontWeight="bold">
        {data.overall_score}
      </text>
      <text x={cx} y={cy + 12} textAnchor="middle" fill="#94a3b8" fontSize="11">
        Overall Ostrom Score
      </text>
    </svg>
  )
}

function ProjectPageContent() {
  const searchParams = useSearchParams()
  const slug = searchParams.get('slug') || ''
  const [dashboard, setDashboard] = useState<Record<string, unknown> | null>(null)
  const [radarData, setRadarData] = useState<RadarData | null>(null)
  const [report, setReport] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!slug) return

    Promise.all([
      fetch(`${API_URL}/dashboard/${slug}`).then((r) => r.json()).catch(() => null),
      fetch(`${API_URL}/evaluate/${slug}/ostrom-radar`).then((r) => r.json()).catch(() => null),
      fetch(`${API_URL}/evaluate/${slug}/report`).then((r) => r.json()).catch(() => null),
    ]).then(([dash, radar, rep]) => {
      setDashboard(dash)
      setRadarData(radar)
      setReport(rep?.report || null)
      setLoading(false)
    })
  }, [slug])

  if (!slug) {
    return <p className="text-octant-muted">No project slug provided.</p>
  }

  if (loading) {
    return <p className="text-octant-muted">Loading project data...</p>
  }

  return (
    <div>
      <a href="/" className="text-octant-accent hover:text-octant-primary text-sm mb-4 inline-block">
        ← Back to all projects
      </a>

      <div className="flex items-center gap-3 mb-2">
        <h1 className="text-3xl font-bold capitalize">{slug.replace(/-/g, ' ')}</h1>
        {['protocol-guild', 'l2beat', 'growthepie', 'revoke-cash'].includes(slug) ? (
          <span className="bg-green-900/40 text-green-400 text-xs font-semibold px-2.5 py-1 rounded-full uppercase tracking-wider">
            Real Evaluation
          </span>
        ) : (
          <span className="bg-amber-900/40 text-amber-400 text-xs font-semibold px-2.5 py-1 rounded-full uppercase tracking-wider">
            Demo Data
          </span>
        )}
      </div>

      {/* Summary bar */}
      {radarData && (
        <div className="flex items-center gap-4 mt-2 mb-4">
          <span className="text-2xl font-bold text-octant-primary">{radarData.overall_score}/100</span>
          {radarData.governance_maturity && (
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              radarData.governance_maturity === 'established' ? 'bg-green-900/30 text-green-400' :
              radarData.governance_maturity === 'developing' ? 'bg-yellow-900/30 text-yellow-400' :
              radarData.governance_maturity === 'nascent' ? 'bg-orange-900/30 text-orange-400' :
              'bg-red-900/30 text-red-400'
            }`}>
              {radarData.governance_maturity.charAt(0).toUpperCase() + radarData.governance_maturity.slice(1)} Governance
            </span>
          )}
          <span className="text-octant-muted text-sm">
            Ostrom Design Principles Assessment
          </span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-4">
        {/* Ostrom Radar */}
        <div className="bg-octant-surface rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Ostrom Commons Governance</h2>
          {radarData ? (
            <OstromRadar data={radarData} />
          ) : (
            <p className="text-octant-muted">No Ostrom scores available.</p>
          )}
        </div>

        {/* Score Breakdown */}
        <div className="bg-octant-surface rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Score Breakdown</h2>
          {radarData?.axes ? (
            <div className="space-y-3">
              {radarData.axes.map((ax, i) => (
                <div key={i} title={ax.full_text || ax.label}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-octant-muted">
                      <span className="text-octant-primary font-mono mr-1.5">{i + 1}</span>
                      {ax.label}
                    </span>
                    <span className="flex items-center gap-2">
                      <span className={`text-xs px-1.5 py-0.5 rounded ${
                        ax.confidence === 'high' ? 'bg-green-900/30 text-green-400' :
                        ax.confidence === 'medium' ? 'bg-yellow-900/30 text-yellow-400' :
                        'bg-red-900/30 text-red-400'
                      }`}>
                        {ax.confidence}
                      </span>
                      <span className="text-octant-primary font-mono">{ax.value}</span>
                    </span>
                  </div>
                  <div className="h-2 bg-octant-bg rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${
                        ax.value >= 70 ? 'bg-green-500' :
                        ax.value >= 40 ? 'bg-octant-primary' :
                        'bg-orange-500'
                      }`}
                      style={{ width: `${ax.value}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-octant-muted">No scores available.</p>
          )}
        </div>
      </div>

      {/* EAS Attestation */}
      <div className="bg-octant-surface rounded-lg p-6 mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">EAS Attestation</h2>
          {dashboard && (dashboard as Record<string, unknown>).has_eas ? (
            <button className="bg-octant-primary hover:bg-octant-secondary text-white px-4 py-2 rounded-lg transition font-medium">
              Attest on Base
            </button>
          ) : (
            <span className="text-octant-muted text-sm">No attestation data yet</span>
          )}
        </div>
        <p className="text-octant-muted text-sm">
          On-chain attestation via the Ethereum Attestation Service on Base.
          Scores are permanently recorded and publicly verifiable.
        </p>
      </div>

      {/* Report */}
      {report && (
        <div className="bg-octant-surface rounded-lg p-6 mt-8">
          <h2 className="text-xl font-semibold mb-4">Full Report</h2>
          <div className="markdown-report">
            <ReactMarkdown
              components={{
                h1: ({ children }) => <h1 className="text-2xl font-bold mt-6 mb-3 text-octant-text">{children}</h1>,
                h2: ({ children }) => <h2 className="text-xl font-semibold mt-5 mb-2 text-octant-text border-b border-octant-bg pb-2">{children}</h2>,
                h3: ({ children }) => <h3 className="text-lg font-semibold mt-4 mb-2 text-octant-accent">{children}</h3>,
                p: ({ children }) => <p className="text-sm text-octant-muted leading-relaxed mb-3">{children}</p>,
                strong: ({ children }) => <strong className="text-octant-text font-semibold">{children}</strong>,
                em: ({ children }) => <em className="text-octant-muted italic">{children}</em>,
                ul: ({ children }) => <ul className="list-disc list-inside text-sm text-octant-muted mb-3 space-y-1">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside text-sm text-octant-muted mb-3 space-y-1">{children}</ol>,
                li: ({ children }) => <li className="text-sm text-octant-muted leading-relaxed">{children}</li>,
                blockquote: ({ children }) => (
                  <blockquote className="border-l-2 border-octant-primary pl-4 my-3 text-sm text-octant-muted italic">
                    {children}
                  </blockquote>
                ),
                code: ({ children, className }) => {
                  const isBlock = className?.includes('language-')
                  if (isBlock) {
                    return (
                      <pre className="bg-octant-bg rounded-lg p-4 my-3 overflow-x-auto">
                        <code className="text-xs text-octant-muted">{children}</code>
                      </pre>
                    )
                  }
                  return <code className="bg-octant-bg text-octant-accent text-xs px-1.5 py-0.5 rounded">{children}</code>
                },
                pre: ({ children }) => <>{children}</>,
                table: ({ children }) => (
                  <div className="overflow-x-auto my-4">
                    <table className="w-full text-sm border-collapse">{children}</table>
                  </div>
                ),
                thead: ({ children }) => <thead className="border-b border-octant-bg">{children}</thead>,
                th: ({ children }) => <th className="text-left text-xs font-semibold text-octant-muted uppercase tracking-wider py-2 px-3">{children}</th>,
                td: ({ children }) => <td className="text-sm text-octant-muted py-2 px-3 border-b border-octant-bg/50">{children}</td>,
                tr: ({ children }) => <tr className="hover:bg-octant-bg/30">{children}</tr>,
                hr: () => <hr className="border-octant-bg my-4" />,
                a: ({ href, children }) => (
                  <a href={href} className="text-octant-accent hover:text-octant-primary underline" target="_blank" rel="noopener noreferrer">
                    {children}
                  </a>
                ),
              }}
            >
              {report}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}

export default function ProjectPage() {
  return (
    <Suspense fallback={<p className="text-octant-muted">Loading...</p>}>
      <ProjectPageContent />
    </Suspense>
  )
}
