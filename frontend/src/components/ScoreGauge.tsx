interface ScoreGaugeProps {
  score: number   // 0–100
  grade: string
  size?: 'sm' | 'lg'
}

const gradeColor: Record<string, string> = {
  Excellent:   'text-emerald-400',
  Strong:      'text-blue-400',
  Good:        'text-yellow-400',
  Fair:        'text-orange-400',
  'Needs Work':'text-red-400',
}

const gradeRing: Record<string, string> = {
  Excellent:   'stroke-emerald-400',
  Strong:      'stroke-blue-400',
  Good:        'stroke-yellow-400',
  Fair:        'stroke-orange-400',
  'Needs Work':'stroke-red-400',
}

export default function ScoreGauge({ score, grade, size = 'lg' }: ScoreGaugeProps) {
  const r = size === 'lg' ? 54 : 38
  const cx = size === 'lg' ? 64 : 46
  const dim = size === 'lg' ? 128 : 92
  const strokeWidth = size === 'lg' ? 9 : 7
  const circumference = 2 * Math.PI * r
  const offset = circumference - (score / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: dim, height: dim }}>
        <svg width={dim} height={dim} className="-rotate-90">
          {/* Track */}
          <circle
            cx={cx} cy={cx} r={r}
            fill="none"
            stroke="#1e293b"
            strokeWidth={strokeWidth}
          />
          {/* Progress */}
          <circle
            cx={cx} cy={cx} r={r}
            fill="none"
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className={`transition-all duration-700 ${gradeRing[grade] ?? 'stroke-blue-400'}`}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`font-bold leading-none ${size === 'lg' ? 'text-3xl' : 'text-xl'}`}>
            {score.toFixed(0)}
          </span>
          <span className="text-slate-500 text-xs mt-0.5">/ 100</span>
        </div>
      </div>
      <span className={`text-sm font-semibold ${gradeColor[grade] ?? 'text-slate-400'}`}>
        {grade}
      </span>
    </div>
  )
}
