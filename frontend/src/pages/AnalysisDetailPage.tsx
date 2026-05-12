import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { analysisAPI, Analysis } from '../utils/api'
import ScoreGauge from '../components/ScoreGauge'
import {
  ChevronLeft, Download, CheckCircle2, AlertCircle,
  Lightbulb, Map, MessageSquare, Clock, BookOpen, Zap
} from 'lucide-react'
import toast from 'react-hot-toast'

export default function AnalysisDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [exporting, setExporting] = useState(false)
  const [tab, setTab] = useState<'overview' | 'roadmap' | 'interview'>('overview')

  useEffect(() => {
    if (!id) return
    analysisAPI.get(Number(id))
      .then((r) => setAnalysis(r.data))
      .catch(() => toast.error('Failed to load analysis'))
      .finally(() => setLoading(false))
  }, [id])

  const handleExport = async () => {
    if (!id) return
    setExporting(true)
    try {
      const { data } = await analysisAPI.exportMarkdown(Number(id))
      const url = URL.createObjectURL(new Blob([data]))
      const a = document.createElement('a')
      a.href = url
      a.download = `analysis-${id}.md`
      a.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error('Export failed')
    } finally {
      setExporting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!analysis) return null

  const { score, skill_overlap, suggestions, roadmap, interview_pack } = analysis

  return (
    <div className="max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Link to="/history" className="btn-ghost">
            <ChevronLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-white">Analysis Report</h1>
            <p className="text-slate-500 text-xs mt-0.5">
              {new Date(analysis.created_at).toLocaleString()}
            </p>
          </div>
        </div>
        <button
          className="btn-secondary flex items-center gap-2 text-sm"
          onClick={handleExport}
          disabled={exporting}
        >
          <Download className="w-4 h-4" />
          {exporting ? 'Exporting…' : 'Export MD'}
        </button>
      </div>

      {/* Score hero */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row items-center gap-8">
          <ScoreGauge score={score.overall_score} grade={score.grade} size="lg" />
          <div className="flex-1 grid grid-cols-3 gap-4 w-full">
            {[
              { label: 'Semantic Match', value: score.semantic_score },
              { label: 'Keyword Match', value: score.keyword_score },
              { label: 'Skill Overlap', value: score.skill_overlap_score },
            ].map(({ label, value }) => (
              <div key={label} className="text-center">
                <p className="text-2xl font-bold text-white">{value.toFixed(0)}</p>
                <p className="text-slate-400 text-xs mt-1">{label}</p>
                <div className="w-full bg-slate-800 rounded-full h-1.5 mt-2">
                  <div
                    className="bg-blue-500 h-1.5 rounded-full transition-all duration-500"
                    style={{ width: `${value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-900 border border-slate-800 rounded-xl p-1 mb-6 w-fit">
        {(['overview', 'roadmap', 'interview'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
              tab === t
                ? 'bg-blue-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {t === 'overview' ? 'Overview' : t === 'roadmap' ? 'Learning Roadmap' : 'Interview Prep'}
          </button>
        ))}
      </div>

      {/* Overview tab */}
      {tab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Matching skills */}
          {skill_overlap.matching_skills.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <h3 className="font-semibold text-white text-sm">
                  Matching Skills ({skill_overlap.matching_skills.length})
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {skill_overlap.matching_skills.map((s) => (
                  <span key={s} className="badge bg-emerald-900/40 text-emerald-300 border border-emerald-800/50">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Missing skills */}
          {skill_overlap.missing_skills.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="w-4 h-4 text-orange-400" />
                <h3 className="font-semibold text-white text-sm">
                  Skill Gaps ({skill_overlap.missing_skills.length})
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {skill_overlap.missing_skills.map((s) => (
                  <span key={s} className="badge bg-orange-900/30 text-orange-300 border border-orange-800/40">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Keyword hits */}
          {analysis.keyword_hits.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <CheckCircle2 className="w-4 h-4 text-blue-400" />
                <h3 className="font-semibold text-white text-sm">
                  Keyword Hits ({analysis.keyword_hits.length})
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {analysis.keyword_hits.map((s) => (
                  <span key={s} className="badge bg-blue-900/30 text-blue-300 border border-blue-800/40">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Keyword gaps */}
          {analysis.keyword_gaps.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <AlertCircle className="w-4 h-4 text-red-400" />
                <h3 className="font-semibold text-white text-sm">
                  Keyword Gaps ({analysis.keyword_gaps.length})
                </h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {analysis.keyword_gaps.map((s) => (
                  <span key={s} className="badge bg-red-900/30 text-red-300 border border-red-800/40">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* AI Suggestions */}
          {suggestions.length > 0 && (
            <div className="card lg:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-4 h-4 text-yellow-400" />
                <h3 className="font-semibold text-white text-sm">AI Suggestions</h3>
              </div>
              <ul className="space-y-3">
                {suggestions.map((s, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                    <span className="w-5 h-5 rounded-full bg-yellow-900/40 text-yellow-400 flex items-center justify-center text-xs flex-shrink-0 mt-0.5 font-bold">
                      {i + 1}
                    </span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Roadmap tab */}
      {tab === 'roadmap' && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="card flex items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-600/20 flex items-center justify-center">
                <Map className="w-5 h-5 text-blue-400" />
              </div>
              <div>
                <p className="font-semibold text-white">{roadmap.role_target}</p>
                <p className="text-slate-400 text-sm">{roadmap.estimated_total_weeks} weeks estimated</p>
              </div>
            </div>
            {roadmap.quick_wins.length > 0 && (
              <div className="flex-1">
                <p className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5 text-yellow-400" /> Quick Wins
                </p>
                <div className="flex flex-wrap gap-2">
                  {roadmap.quick_wins.map((w) => (
                    <span key={w} className="badge bg-yellow-900/30 text-yellow-300 border border-yellow-800/40">
                      {w}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Phases */}
          {roadmap.phases.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4 text-sm">Learning Phases</h3>
              <div className="space-y-4">
                {roadmap.phases.map((phase, i) => (
                  <div key={i} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-7 h-7 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-xs font-bold text-blue-400">
                        {i + 1}
                      </div>
                      {i < roadmap.phases.length - 1 && (
                        <div className="w-px flex-1 bg-slate-800 my-1" />
                      )}
                    </div>
                    <div className="pb-4 flex-1">
                      <p className="font-medium text-slate-200 text-sm">{phase.phase}</p>
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {phase.skills.map((s) => (
                          <span key={s} className="badge bg-slate-800 text-slate-300 border border-slate-700">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Milestones */}
          {roadmap.milestones.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4 text-sm">Milestones & Resources</h3>
              <div className="space-y-4">
                {roadmap.milestones.map((m, i) => (
                  <div key={i} className="border border-slate-800 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <p className="font-medium text-slate-100">{m.skill}</p>
                        <span className="badge bg-slate-800 text-slate-400 border border-slate-700 mt-1">
                          {m.level}
                        </span>
                      </div>
                      <div className="flex items-center gap-1 text-slate-400 text-xs">
                        <Clock className="w-3.5 h-3.5" />
                        {m.estimated_weeks}w
                      </div>
                    </div>
                    {m.resources.length > 0 && (
                      <div className="space-y-1.5">
                        {m.resources.map((r, j) => (
                          <div key={j} className="flex items-center gap-2 text-sm">
                            <BookOpen className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
                            {r.url ? (
                              <a
                                href={r.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-400 hover:text-blue-300"
                              >
                                {r.title}
                              </a>
                            ) : (
                              <span className="text-slate-300">{r.title}</span>
                            )}
                            <span className="text-slate-600 text-xs">({r.type})</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Interview tab */}
      {tab === 'interview' && (
        <div className="space-y-6">
          <div className="card flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-violet-600/20 flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-violet-400" />
            </div>
            <div>
              <p className="font-semibold text-white">{interview_pack.role}</p>
              <p className="text-slate-400 text-sm">{interview_pack.total_count} questions prepared</p>
            </div>
          </div>

          {interview_pack.technical_questions.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4 text-sm">
                Technical Questions ({interview_pack.technical_questions.length})
              </h3>
              <div className="space-y-4">
                {interview_pack.technical_questions.map((q, i) => (
                  <div key={i} className="border border-slate-800 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      <span className="w-6 h-6 rounded-full bg-violet-900/40 text-violet-400 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                        {i + 1}
                      </span>
                      <div className="flex-1">
                        <p className="text-slate-100 text-sm">{q.question}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className="badge bg-slate-800 text-slate-400 border border-slate-700">{q.skill}</span>
                          <span className="badge bg-slate-800 text-slate-400 border border-slate-700">{q.type}</span>
                        </div>
                        {q.note && (
                          <p className="text-slate-500 text-xs mt-2 italic">{q.note}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {interview_pack.behavioral_questions.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4 text-sm">
                Behavioral Questions ({interview_pack.behavioral_questions.length})
              </h3>
              <ol className="space-y-3">
                {interview_pack.behavioral_questions.map((q, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                    <span className="w-5 h-5 rounded-full bg-blue-900/40 text-blue-400 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    {q}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {interview_pack.system_design_questions.length > 0 && (
            <div className="card">
              <h3 className="font-semibold text-white mb-4 text-sm">
                System Design Questions ({interview_pack.system_design_questions.length})
              </h3>
              <ol className="space-y-3">
                {interview_pack.system_design_questions.map((q, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm text-slate-300">
                    <span className="w-5 h-5 rounded-full bg-emerald-900/40 text-emerald-400 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">
                      {i + 1}
                    </span>
                    {q}
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
