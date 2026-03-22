'use client'

import { useEffect, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://optinpg-evaluator-production.up.railway.app'

interface Project {
  slug: string
  project?: string
  ostrom_overall?: number | null
  governance_maturity?: string | null
  quant_composite?: number | null
  created_at?: string | null
  updated_at?: string | null
  source?: string
  data_files?: string[]
}

const OSTROM_PRINCIPLES = [
  'Clearly Defined Boundaries',
  'Congruence with Local Conditions',
  'Collective-Choice Arrangements',
  'Monitoring',
  'Graduated Sanctions',
  'Conflict-Resolution Mechanisms',
  'Rights to Organize',
  'Nested Enterprises',
]

// Protocol Guild is the only real evaluation — everything else is demo
const REAL_SLUGS = new Set(['protocol-guild', 'l2beat', 'growthepie', 'revoke-cash'])

function maturityColor(m: string | null | undefined): string {
  if (!m) return 'bg-gray-800/30 text-gray-400'
  switch (m) {
    case 'established': return 'bg-green-900/30 text-green-400'
    case 'developing': return 'bg-yellow-900/30 text-yellow-400'
    case 'nascent': return 'bg-orange-900/30 text-orange-400'
    default: return 'bg-red-900/30 text-red-400'
  }
}

function scoreColor(score: number): string {
  if (score >= 70) return 'text-green-400'
  if (score >= 50) return 'text-yellow-400'
  return 'text-orange-400'
}

export default function Home() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch(`${API_URL}/projects`)
      .then((res) => res.json())
      .then((data) => {
        setProjects(data.projects || [])
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const realCount = projects.filter((p) => REAL_SLUGS.has(p.slug)).length
  const demoCount = projects.filter((p) => !REAL_SLUGS.has(p.slug)).length

  return (
    <div>
      {/* Hero */}
      <section className="mb-12">
        <h1 className="text-4xl font-bold mb-4">
          Ostrom-Augmented Public Goods Evaluation
        </h1>
        <p className="text-octant-muted text-lg max-w-3xl mb-6">
          Evaluate Octant ecosystem projects against Elinor Ostrom&apos;s 8 Design
          Principles for commons governance — the Nobel Prize-winning framework from{' '}
          <em>Governing the Commons</em> (1990), translated for digital public goods.
          Every score is evidence-based, independently evaluated, and attestable on-chain via EAS on Base.
        </p>
        <div className="flex gap-3 text-sm">
          <span className="bg-octant-surface px-3 py-1.5 rounded-full text-octant-accent">
            Collection: Octant + Karma + Social
          </span>
          <span className="bg-octant-surface px-3 py-1.5 rounded-full text-octant-accent">
            Analysis: Quant + Qual + Ostrom
          </span>
          <span className="bg-octant-surface px-3 py-1.5 rounded-full text-octant-accent">
            Mechanism: Ostrom Design Principles
          </span>
        </div>
      </section>

      {/* Stats */}
      <section className="mb-10">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-octant-surface rounded-lg p-6">
            <div className="text-3xl font-bold text-octant-primary">{projects.length}</div>
            <div className="text-octant-muted text-sm mt-1">Projects Evaluated</div>
          </div>
          <div className="bg-octant-surface rounded-lg p-6">
            <div className="text-3xl font-bold text-octant-secondary">8</div>
            <div className="text-octant-muted text-sm mt-1">Ostrom Principles Scored</div>
          </div>
          <div className="bg-octant-surface rounded-lg p-6">
            <div className="text-3xl font-bold text-octant-accent">3</div>
            <div className="text-octant-muted text-sm mt-1">Independent Evaluators</div>
          </div>
          <div className="bg-octant-surface rounded-lg p-6">
            <div className="text-3xl font-bold text-indigo-400">Base</div>
            <div className="text-octant-muted text-sm mt-1">EAS Attestation Chain</div>
          </div>
        </div>
      </section>

      {/* Ostrom Principles Overview */}
      <section className="mb-10">
        <h2 className="text-xl font-bold mb-4">The 8 Design Principles</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {OSTROM_PRINCIPLES.map((p, i) => (
            <div key={i} className="bg-octant-surface rounded-lg px-4 py-3 text-sm">
              <span className="text-octant-primary font-mono mr-2">{i + 1}</span>
              <span className="text-octant-text">{p}</span>
            </div>
          ))}
        </div>
        <p className="text-octant-muted text-xs mt-3">
          From Elinor Ostrom, <em>Governing the Commons</em> (Cambridge University Press, 1990), pp. 90-102.
          Adapted for digital public goods evaluation.
        </p>
      </section>

      {/* Projects */}
      <section>
        <div className="flex items-center gap-3 mb-4">
          <h2 className="text-2xl font-bold">Evaluated Projects</h2>
          {projects.length > 0 && (
            <div className="flex gap-2 text-xs">
              {realCount > 0 && (
                <span className="bg-green-900/30 text-green-400 px-2 py-0.5 rounded-full">
                  {realCount} real
                </span>
              )}
              {demoCount > 0 && (
                <span className="bg-amber-900/30 text-amber-400 px-2 py-0.5 rounded-full">
                  {demoCount} demo
                </span>
              )}
            </div>
          )}
        </div>
        {loading && <p className="text-octant-muted">Loading projects...</p>}
        {error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4 text-red-300">
            Failed to load projects: {error}
          </div>
        )}
        {!loading && !error && projects.length === 0 && (
          <div className="bg-octant-surface rounded-lg p-8 text-center">
            <p className="text-octant-muted mb-2">No projects evaluated yet.</p>
            <p className="text-sm text-octant-muted">
              Run <code className="bg-octant-bg px-2 py-1 rounded">/council:evaluate [project]</code> to get started.
            </p>
          </div>
        )}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => {
            const isDemo = !REAL_SLUGS.has(project.slug)
            const displayName = project.project || project.slug.replace(/-/g, ' ')

            return (
              <a
                key={project.slug}
                href={`/project/?slug=${project.slug}`}
                className={`bg-octant-surface rounded-lg p-6 border transition group relative ${
                  isDemo
                    ? 'border-amber-500/20 hover:border-amber-500/40'
                    : 'border-transparent hover:border-octant-primary'
                }`}
              >
                {/* Demo / Real badge */}
                <div className="absolute top-3 right-3">
                  {isDemo ? (
                    <span className="bg-amber-900/40 text-amber-400 text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider">
                      Demo
                    </span>
                  ) : (
                    <span className="bg-green-900/40 text-green-400 text-[10px] font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider">
                      Real
                    </span>
                  )}
                </div>

                {/* Project name */}
                <h3 className="text-lg font-semibold mb-2 capitalize group-hover:text-octant-primary transition pr-14">
                  {displayName}
                </h3>

                {/* Scores row */}
                {(project.ostrom_overall != null || project.quant_composite != null) && (
                  <div className="flex items-center gap-3 mb-3">
                    {project.ostrom_overall != null && (
                      <div className="flex items-baseline gap-1">
                        <span className={`text-xl font-bold ${scoreColor(project.ostrom_overall)}`}>
                          {project.ostrom_overall}
                        </span>
                        <span className="text-octant-muted text-xs">/100 Ostrom</span>
                      </div>
                    )}
                    {project.quant_composite != null && (
                      <div className="flex items-baseline gap-1">
                        <span className={`text-lg font-semibold ${scoreColor(project.quant_composite)}`}>
                          {project.quant_composite}
                        </span>
                        <span className="text-octant-muted text-xs">/100 Quant</span>
                      </div>
                    )}
                  </div>
                )}

                {/* Governance maturity badge */}
                {project.governance_maturity && (
                  <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${maturityColor(project.governance_maturity)}`}>
                    {project.governance_maturity.charAt(0).toUpperCase() + project.governance_maturity.slice(1)} Governance
                  </span>
                )}

                {/* Legacy: data_files for filesystem-backed projects */}
                {project.data_files && project.data_files.length > 0 && (
                  <>
                    <div className="text-octant-muted text-sm mt-2">
                      {project.data_files.length} data sources collected
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {project.data_files.map((f) => (
                        <span
                          key={f}
                          className="bg-octant-bg text-octant-accent text-xs px-2 py-0.5 rounded"
                        >
                          {f.replace('.json', '').replace('.md', '')}
                        </span>
                      ))}
                    </div>
                  </>
                )}
              </a>
            )
          })}
        </div>
      </section>

      {/* How it works */}
      <section className="mt-12 border-t border-octant-surface pt-8">
        <h2 className="text-xl font-bold mb-4">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-octant-primary font-bold mb-2">Wave 1 — Collect</div>
            <p className="text-octant-muted text-sm">
              Four data agents gather information in parallel: Octant project data,
              Karma GAP accountability scores, GitHub/Farcaster/X social activity,
              and ecosystem metrics from DefiLlama, OSO, and L2Beat.
            </p>
          </div>
          <div>
            <div className="text-octant-secondary font-bold mb-2">Wave 2 — Evaluate</div>
            <p className="text-octant-muted text-sm">
              Three independent evaluators score the project without seeing each
              other&apos;s work: quantitative metrics (0-100), qualitative narrative
              (150-300 words with evidence), and Ostrom commons governance (8 principles).
            </p>
          </div>
          <div>
            <div className="text-octant-accent font-bold mb-2">Wave 3 — Synthesize</div>
            <p className="text-octant-muted text-sm">
              Synthesis agents combine all evaluations into an Ostrom radar chart
              report and produce EAS attestation JSON ready for on-chain recording on Base.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}
