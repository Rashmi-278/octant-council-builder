import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'OptInPG — Ostrom Public Goods Evaluator',
  description: 'Evaluate Octant public goods projects using Elinor Ostrom\'s 8 Rules for Managing a Commons',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-octant-bg text-octant-text">
        <nav className="border-b border-octant-surface px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-octant-primary">
              OptInPG
            </a>
            <div className="flex items-center gap-4 text-sm text-octant-muted">
              <span>Ostrom-Augmented Scoring</span>
              <a
                href="https://octant.app"
                target="_blank"
                rel="noopener noreferrer"
                className="text-octant-accent hover:text-octant-primary transition"
              >
                Octant
              </a>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
        <footer className="border-t border-octant-surface px-6 py-4 mt-12">
          <div className="max-w-7xl mx-auto text-center text-sm text-octant-muted">
            Powered by{' '}
            <a href="https://github.com/golemfoundation/octant-council-builder" className="text-octant-accent hover:text-octant-primary">
              Council Builder
            </a>{' '}
            · Scoring by Elinor Ostrom&apos;s 8 Rules · Attestations on{' '}
            <a href="https://base.easscan.org" className="text-octant-accent hover:text-octant-primary">
              Base EAS
            </a>
          </div>
        </footer>
      </body>
    </html>
  )
}
