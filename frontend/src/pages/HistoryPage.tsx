import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { analysisAPI, AnalysisSummary } from '../utils/api'
import ScoreGauge from '../components/ScoreGauge'
import { ChevronRight, Search, Plus } from 'lucide-react'
import toast from 'react-hot-toast'

export default function HistoryPage() {
  const [analyses, setAnalyses] = useState<AnalysisSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')

  useEffect(() => {
    analysisAPI.list()
      .then((r) => setAnalyses(r.data))
      .catch(() => toast.error('Failed to load history'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = analyses.filter((a) => {
    const q = query.toLowerCase()
    return (
      a.job_title.toLowerCase().includes(q) ||
      (a.company ?? '').toLowerCase().includes(q) ||
      a.grade.toLowerCase().includes(q)
    )
  })

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">History</h1>
          <p className="text-slate-400 mt-1 text-sm">{analyses.length} analyses total</p>
        </div>
        <Link to="/analyze" className="btn-primary flex items-center gap-2 text-sm">
          <Plus className="w-4 h-4" />
          New Analysis
        </Link>
      </div>

      {analyses.length === 0 ? (
        <div className="card flex flex-col items-center text-center py-16 gap-4">
          <div className="w-14 h-14 rounded-2xl bg-slate-800 flex items-center justify-center">
            <Search className="w-7 h-7 text-slate-500" />
          </div>
          <div>
            <p className="text-white font-semibold text-lg">No analyses yet</p>
            <p className="text-slate-400 text-sm mt-1">
              Run your first analysis to see it here.
            </p>
          </div>
          <Link to="/analyze" className="btn-primary mt-2">
            Get started
          </Link>
        </div>
      ) : (
        <>
          {/* Search */}
          <div className="relative mb-5">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              className="input pl-9"
              placeholder="Search by job title, company, or grade…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          {filtered.length === 0 ? (
            <div className="card text-center py-10">
              <p className="text-slate-400 text-sm">No results for "{query}"</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filtered.map((a) => (
                <Link
                  key={a.id}
                  to={`/analysis/${a.id}`}
                  className="card flex items-center gap-4 hover:border-slate-700 hover:bg-slate-800/60 transition-colors cursor-pointer"
                >
                  <ScoreGauge score={a.overall_score} grade={a.grade} size="sm" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-slate-100 truncate">{a.job_title}</p>
                    {a.company && (
                      <p className="text-slate-400 text-sm truncate">{a.company}</p>
                    )}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-xs text-slate-500">
                      {new Date(a.created_at).toLocaleDateString('en-US', {
                        year: 'numeric', month: 'short', day: 'numeric'
                      })}
                    </p>
                    <p className="text-xs text-slate-600 mt-0.5">
                      {new Date(a.created_at).toLocaleTimeString('en-US', {
                        hour: '2-digit', minute: '2-digit'
                      })}
                    </p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
                </Link>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
