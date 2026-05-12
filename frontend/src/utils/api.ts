import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Global 401 handler
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ── Types ──────────────────────────────────────────────────────────────────

export interface User {
  id: number
  email: string
  full_name: string | null
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Resume {
  id: number
  filename: string
  skills: string[]
  contact_info: Record<string, string>
  created_at: string
}

export interface JobDescription {
  id: number
  title: string
  company: string | null
  required_skills: string[]
  created_at: string
}

export interface ScoreBreakdown {
  overall_score: number
  semantic_score: number
  keyword_score: number
  skill_overlap_score: number
  confidence: number
  grade: string
}

export interface SkillOverlap {
  matching_skills: string[]
  missing_skills: string[]
  extra_skills: string[]
}

export interface RoadmapMilestone {
  skill: string
  level: string
  estimated_weeks: number
  resources: { type: string; title: string; url?: string }[]
}

export interface Roadmap {
  role_target: string
  estimated_total_weeks: number
  phases: { phase: string; skills: string[] }[]
  milestones: RoadmapMilestone[]
  quick_wins: string[]
}

export interface InterviewQuestion {
  question: string
  skill: string
  type: string
  note: string
}

export interface InterviewPack {
  role: string
  technical_questions: InterviewQuestion[]
  behavioral_questions: string[]
  system_design_questions: string[]
  total_count: number
}

export interface Analysis {
  id: number
  resume_id: number
  job_description_id: number
  score: ScoreBreakdown
  skill_overlap: SkillOverlap
  keyword_gaps: string[]
  keyword_hits: string[]
  suggestions: string[]
  roadmap: Roadmap
  interview_pack: InterviewPack
  created_at: string
}

export interface AnalysisSummary {
  id: number
  job_title: string
  company: string | null
  overall_score: number
  grade: string
  created_at: string
}

export interface Dashboard {
  total_analyses: number
  average_score: number
  best_match: AnalysisSummary | null
  recent_analyses: AnalysisSummary[]
  top_missing_skills: string[]
  top_matching_skills: string[]
}

// ── API calls ──────────────────────────────────────────────────────────────

export const authAPI = {
  register: (email: string, password: string, full_name?: string) =>
    api.post<User>('/auth/register', { email, password, full_name }),
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),
}

export const resumeAPI = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post<Resume>('/resumes/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: () => api.get<Resume[]>('/resumes/'),
  delete: (id: number) => api.delete(`/resumes/${id}`),
}

export const jobsAPI = {
  create: (title: string, raw_text: string, company?: string) =>
    api.post<JobDescription>('/jobs/', { title, raw_text, company }),
  list: () => api.get<JobDescription[]>('/jobs/'),
  get: (id: number) => api.get<JobDescription>(`/jobs/${id}`),
  delete: (id: number) => api.delete(`/jobs/${id}`),
}

export const analysisAPI = {
  run: (resume_id: number, job_description_id: number) =>
    api.post<Analysis>('/analysis/', { resume_id, job_description_id }),
  list: () => api.get<AnalysisSummary[]>('/analysis/'),
  get: (id: number) => api.get<Analysis>(`/analysis/${id}`),
  dashboard: () => api.get<Dashboard>('/analysis/dashboard'),
  exportMarkdown: (id: number) =>
    api.get(`/export/${id}/markdown`, { responseType: 'blob' }),
}
