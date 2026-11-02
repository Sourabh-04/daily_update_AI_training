import { useState } from 'react'
import { startBenchmark, type BenchmarkState, type Model } from '../api'

type Props = {
  models: Model[] // the selected models
  document: string | null
  state: BenchmarkState
  onStarted: () => void
}

export function BenchmarkPanel({ models, document, state, onStarted }: Props) {
  const [error, setError] = useState('')
  const running = state.status === 'running'

  const run = async () => {
    setError('')
    try {
      await startBenchmark(document, models.map((m) => m.id))
      onStarted()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    }
  }

  const progress = running ? state.progress : null
  const percent = progress?.total ? Math.round((progress.done / progress.total) * 100) : 0

  return (
    <div className="space-y-3">
      <p className="text-slate-600">
        Every selected model answers each test question for <b>{document ?? 'all documents'}</b>, one call at a time.
        Answers are scored by keyword match (accuracy) and embedding similarity (relevance, groundedness).
      </p>
      <p className="text-sm text-slate-500">Free models are rate-limited, so a full run can take a few minutes.</p>

      <button
        onClick={run}
        disabled={running || models.length === 0}
        className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {running ? 'Running…' : '▶ Run Benchmark'}
      </button>
      {models.length === 0 && <p className="text-sm text-slate-500">Select at least one model.</p>}

      {running && (
        <div>
          <div className="mb-1 flex justify-between text-sm text-slate-500">
            <span>Progress</span>
            <span>{progress?.total ? `${progress.done} / ${progress.total} calls` : 'Starting…'}</span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100">
            <div className="h-full rounded-full bg-indigo-600 transition-all" style={{ width: `${percent}%` }} />
          </div>
        </div>
      )}

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-red-700">{error}</div>}
    </div>
  )
}
