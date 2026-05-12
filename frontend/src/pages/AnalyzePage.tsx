import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { resumeAPI, jobsAPI, analysisAPI, Resume, JobDescription } from '../utils/api'
import { Upload, FileText, Loader2, ChevronRight, X } from 'lucide-react'
import toast from 'react-hot-toast'

type Step = 'resume' | 'job' | 'run'

export default function AnalyzePage() {
  const navigate = useNavigate()

  // Step state
  const [step, setStep] = useState<Step>('resume')

  // Resume
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [uploadingResume, setUploadingResume] = useState(false)
  const [resume, setResume] = useState<Resume | null>(null)

  // Job
  const [jobTitle, setJobTitle] = useState('')
  const [company, setCompany] = useState('')
  const [jobText, setJobText] = useState('')
  const [savingJob, setSavingJob] = useState(false)
  const [job, setJob] = useState<JobDescription | null>(null)

  // Analysis
  const [running, setRunning] = useState(false)

  // ── Resume step ──────────────────────────────────────────────────────────

  const handleResumeUpload = async () => {
    if (!resumeFile) return
    setUploadingResume(true)
    try {
      const { data } = await resumeAPI.upload(resumeFile)
      setResume(data)
      toast.success('Resume parsed!')
      setStep('job')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to upload resume')
    } finally {
      setUploadingResume(false)
    }
  }

  // ── Job step ─────────────────────────────────────────────────────────────

  const handleJobSave = async () => {
    if (!jobTitle.trim() || !jobText.trim()) {
      toast.error('Title and description are required')
      return
    }
    setSavingJob(true)
    try {
      const { data } = await jobsAPI.create(jobTitle.trim(), jobText.trim(), company.trim() || undefined)
      setJob(data)
      toast.success('Job description saved!')
      setStep('run')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to save job description')
    } finally {
      setSavingJob(false)
    }
  }

  // ── Run step ─────────────────────────────────────────────────────────────

  const handleRun = async () => {
    if (!resume || !job) return
    setRunning(true)
    try {
      const { data } = await analysisAPI.run(resume.id, job.id)
      toast.success('Analysis complete!')
      navigate(`/analysis/${data.id}`)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Analysis failed')
      setRunning(false)
    }
  }

  // ── Step indicator ───────────────────────────────────────────────────────

  const steps: { key: Step; label: string }[] = [
    { key: 'resume', label: 'Upload Resume' },
    { key: 'job',    label: 'Job Description' },
    { key: 'run',    label: 'Run Analysis' },
  ]

  const stepIndex = steps.findIndex((s) => s.key === step)

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">New Analysis</h1>
        <p className="text-slate-400 mt-1 text-sm">Match your resume against a job description</p>
      </div>

      {/* Stepper */}
      <div className="flex items-center gap-2 mb-8">
        {steps.map((s, i) => (
          <div key={s.key} className="flex items-center gap-2">
            <div
              className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-colors ${
                i < stepIndex
                  ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-700/40'
                  : i === stepIndex
                  ? 'bg-blue-600/20 text-blue-300 border border-blue-500/40'
                  : 'bg-slate-800 text-slate-500 border border-slate-700'
              }`}
            >
              <span className={`w-4 h-4 rounded-full text-[10px] flex items-center justify-center font-bold ${
                i < stepIndex ? 'bg-emerald-500 text-white' :
                i === stepIndex ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-400'
              }`}>{i < stepIndex ? '✓' : i + 1}</span>
              {s.label}
            </div>
            {i < steps.length - 1 && <ChevronRight className="w-3.5 h-3.5 text-slate-700" />}
          </div>
        ))}
      </div>

      {/* Step 1: Resume */}
      {step === 'resume' && (
        <div className="card space-y-5">
          <div>
            <h2 className="font-semibold text-white mb-1">Upload your resume</h2>
            <p className="text-slate-400 text-sm">Supports PDF, DOCX, and TXT files</p>
          </div>

          <label className="block">
            <div className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
              resumeFile ? 'border-blue-500/50 bg-blue-500/5' : 'border-slate-700 hover:border-slate-600'
            }`}>
              {resumeFile ? (
                <div className="flex items-center justify-center gap-3">
                  <FileText className="w-5 h-5 text-blue-400" />
                  <span className="text-slate-200 text-sm font-medium">{resumeFile.name}</span>
                  <button
                    type="button"
                    onClick={(e) => { e.preventDefault(); setResumeFile(null) }}
                    className="text-slate-500 hover:text-slate-300"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <>
                  <Upload className="w-8 h-8 text-slate-500 mx-auto mb-3" />
                  <p className="text-slate-300 text-sm font-medium">Click to browse or drag & drop</p>
                  <p className="text-slate-600 text-xs mt-1">PDF, DOCX, TXT — max 10 MB</p>
                </>
              )}
            </div>
            <input
              type="file"
              className="hidden"
              accept=".pdf,.docx,.txt"
              onChange={(e) => setResumeFile(e.target.files?.[0] ?? null)}
            />
          </label>

          <button
            className="btn-primary w-full"
            disabled={!resumeFile || uploadingResume}
            onClick={handleResumeUpload}
          >
            {uploadingResume ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> Parsing resume…
              </span>
            ) : 'Upload & Continue'}
          </button>
        </div>
      )}

      {/* Step 2: Job */}
      {step === 'job' && (
        <div className="card space-y-4">
          <div>
            <h2 className="font-semibold text-white mb-1">Job description</h2>
            <p className="text-slate-400 text-sm">Paste the full job posting for best results</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Job title <span className="text-red-500">*</span></label>
              <input
                className="input"
                placeholder="Senior Software Engineer"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
                autoFocus
              />
            </div>
            <div>
              <label className="label">Company <span className="text-slate-600">(optional)</span></label>
              <input
                className="input"
                placeholder="Acme Corp"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="label">Job description <span className="text-red-500">*</span></label>
            <textarea
              className="input min-h-[200px] resize-none"
              placeholder="Paste the full job description here…"
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
            />
          </div>

          <button
            className="btn-primary w-full"
            disabled={!jobTitle.trim() || !jobText.trim() || savingJob}
            onClick={handleJobSave}
          >
            {savingJob ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" /> Saving…
              </span>
            ) : 'Save & Continue'}
          </button>
        </div>
      )}

      {/* Step 3: Run */}
      {step === 'run' && resume && job && (
        <div className="card space-y-6">
          <div>
            <h2 className="font-semibold text-white mb-1">Ready to analyze</h2>
            <p className="text-slate-400 text-sm">
              AI will score your resume, identify skill gaps, generate a roadmap, and create interview questions.
            </p>
          </div>

          <div className="space-y-3">
            <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/60">
              <FileText className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-slate-400">Resume</p>
                <p className="text-sm text-slate-100 font-medium">{resume.filename}</p>
                {resume.skills.length > 0 && (
                  <p className="text-xs text-slate-500 mt-0.5">
                    {resume.skills.length} skills detected
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-start gap-3 p-3 rounded-lg bg-slate-800/60">
              <FileText className="w-4 h-4 text-violet-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-xs text-slate-400">Job</p>
                <p className="text-sm text-slate-100 font-medium">{job.title}</p>
                {job.company && <p className="text-xs text-slate-500">{job.company}</p>}
              </div>
            </div>
          </div>

          <button
            className="btn-primary w-full py-3 text-base"
            disabled={running}
            onClick={handleRun}
          >
            {running ? (
              <span className="flex items-center justify-center gap-2">
                <Loader2 className="w-5 h-5 animate-spin" /> Analyzing with AI…
              </span>
            ) : '⚡ Run Analysis'}
          </button>
          {running && (
            <p className="text-center text-xs text-slate-500">
              This may take 15–30 seconds while the AI processes everything…
            </p>
          )}
        </div>
      )}
    </div>
  )
}
