import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { analysisAPI, Dashboard } from '../utils/api'
import ScoreGauge from '../components/ScoreGauge'
import {
  TrendingUp, Briefcase, Search, ChevronRight,
  Sparkles, AlertCircle, CheckCircle2
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    analysisAPI.dashboard()
      .then((r) => setData(r.data))
      .catch(() => toast.error('Failed to load dashboard'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!data) return null

  const hasData = data.total_analyses > 0

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 mt-1 text-sm">Your career intelligence at a glance</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-blue-600/20 flex items-center justify-center flex-shrink-0">
            <TrendingUp className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">{data.total_analyses}</p>
            <p className="text-slate-400 text-xs">Total Analyses</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-emerald-600/20 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <p className="text-2xl font-bold text-white">
              {hasData ? data.average_score.toFixed(0) : '—'}
            </p>
            <p className="text-slate-400 text-xs">Average Score</p>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-violet-600/20 flex items-center justify-center flex-shrink-0">
            <Briefcase className="w-5 h-5 text-violet-400" />
          </div>
          <div>
            <p className="text-sm font-semibold text-white truncate max-w-[140px]">
              {data.best_match ? data.best_match.job_title : '—'}
            </p>
            <p className="text-slate-400 text-xs">Best Match</p>
          </div>
        </div>
      </div>

      {!hasData ? (
        /* Empty state */
        <div className="card flex flex-col items-center text-center py-16 gap-4">
          <div className="w-14 h-14 rounded-2xl bg-blue-600/20 flex items-center justify-center">
            <Search className="w-7 h-7 text-blue-400" />
          </div>
          <div>
            <p className="text-white font-semibold text-lg">No analyses yet</p>
            <p className="text-slate-400 text-sm mt-1 max-w-xs">
              Upload your resume and a job description to get your first AI-powered match score.
            </p>
          </div>
          <Link to="/analyze" className="btn-primary mt-2">
            Run first analysis
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Best match card */}
          {data.best_match && (
            <div className="card lg:col-span-1 flex flex-col items-center gap-4">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider self-start">
                Best Match
              </p>
              <ScoreGauge score={data.best_match.overall_score} grade={data.best_match.grade} size="lg" />
              <div className="text-center">
                <p className="font-semibold text-white">{data.best_match.job_title}</p>
                {data.best_match.company && (
                  <p className="text-slate-400 text-sm">{data.best_match.company}</p>
                )}
              </div>
              <Link
                to={`/analysis/${data.best_match.id}`}
                className="text-blue-400 hover:text-blue-300 text-sm flex items-center gap-1"
              >
                View details <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          )}

          {/* Skills */}
          <div className="card lg:col-span-2 space-y-5">
            {data.top_matching_skills.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  <p className="text-sm font-semibold text-slate-200">Top Matching Skills</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {data.top_matching_skills.map((s) => (
                    <span key={s} className="badge bg-emerald-900/40 text-emerald-300 border border-emerald-800/50">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {data.top_missing_skills.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <AlertCircle className="w-4 h-4 text-orange-400" />
                  <p className="text-sm font-semibold text-slate-200">Top Skill Gaps</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {data.top_missing_skills.map((s) => (
                    <span key={s} className="badge bg-orange-900/30 text-orange-300 border border-orange-800/40">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Recent analyses */}
          <div className="card lg:col-span-3">
            <div className="flex items-center justify-between mb-4">
              <p className="text-sm font-semibold text-slate-200">Recent Analyses</p>
              <Link to="/history" className="text-blue-400 hover:text-blue-300 text-sm">
                View all
              </Link>
            </div>
            <div className="space-y-2">
              {data.recent_analyses.map((a) => (
                <Link
                  key={a.id}
                  to={`/analysis/${a.id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <ScoreGauge score={a.overall_score} grade={a.grade} size="sm" />
                    <div>
                      <p className="text-sm font-medium text-slate-100">{a.job_title}</p>
                      {a.company && <p className="text-xs text-slate-400">{a.company}</p>}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-500">
                      {new Date(a.created_at).toLocaleDateString()}
                    </span>
                    <ChevronRight className="w-4 h-4 text-slate-600" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
