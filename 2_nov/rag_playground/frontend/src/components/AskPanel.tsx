import { useState, type FormEvent } from 'react'
import { ask, type AskResponse, type Model } from '../api'
import { ModelBadge } from './ModelSelector'

type Props = {
  models: Model[] // the selected models
  document: string | null
}

export function AskPanel({ models, document }: Props) {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<AskResponse | null>(null)
  const [error, setError] = useState('')

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)
    try {
      setResult(await ask(question.trim(), document, models.map((m) => m.id)))
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  // While loading, show a placeholder card per selected model; afterwards, the models that were asked.
  const cardModels = result ? result.answers.map((a) => a.model_id) : loading ? models.map((m) => m.id) : []
  const modelById = (id: string) => models.find((m) => m.id === id)

  return (
    <div className="space-y-3">
      <form onSubmit={submit} className="space-y-3">
        <label className="block">
          <span className="mb-1 block font-medium">Your Question</span>
          <textarea
            className="w-full rounded-lg border border-slate-300 p-3 outline-none focus:border-indigo-500"
            rows={3}
            placeholder="How many days of annual leave do full-time employees receive?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
        </label>
        <button
          type="submit"
          disabled={loading || !question.trim() || models.length === 0}
          className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Asking…' : '▶ Ask Selected Models'}
        </button>
        {models.length === 0 && <p className="text-sm text-slate-500">Select at least one model.</p>}
      </form>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-red-700">{error}</div>}

      {cardModels.map((id) => {
        const model = modelById(id)
        const answer = result?.answers.find((a) => a.model_id === id)
        return (
          <div key={id} className="rounded-lg border border-slate-200 p-3">
            <div className="mb-2 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                {model && <ModelBadge model={model} />}
                <span className="font-medium">{model?.display_name ?? id}</span>
              </div>
              {answer?.latency_s != null && (
                <span className="rounded bg-slate-100 px-2 py-0.5 text-sm text-slate-600">
                  ⏱ {answer.latency_s.toFixed(2)} s
                </span>
              )}
            </div>
            {!answer ? (
              <p className="animate-pulse text-slate-400">Waiting for answer…</p>
            ) : answer.error ? (
              <p className="text-sm text-red-600">Failed: {answer.error}</p>
            ) : (
              <p className="whitespace-pre-wrap text-slate-700">{answer.answer}</p>
            )}
          </div>
        )
      })}

      {result && (
        <details className="rounded-lg border border-slate-200 p-3">
          <summary className="cursor-pointer font-medium">Sources (Top Chunks)</summary>
          <ol className="mt-3 space-y-3">
            {result.sources.map((s) => (
              <li key={s.id} className="rounded bg-slate-50 p-3 text-sm">
                <div className="mb-1 flex justify-between gap-2 text-slate-500">
                  <span className="font-medium">{s.id}</span>
                  <span>similarity {(1 - s.distance).toFixed(2)}</span>
                </div>
                <p className="whitespace-pre-wrap text-slate-700">{s.text}</p>
              </li>
            ))}
          </ol>
        </details>
      )}
    </div>
  )
}
