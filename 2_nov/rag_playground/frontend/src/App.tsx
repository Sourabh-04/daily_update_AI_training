import { useEffect, useState } from 'react'
import { getDocuments, getLatestBenchmark, getModels, type BenchmarkState, type Model } from './api'
import { AskPanel } from './components/AskPanel'
import { BenchmarkPanel } from './components/BenchmarkPanel'
import { BenchmarkResults } from './components/BenchmarkResults'
import { MAX_MODELS, ModelSelector } from './components/ModelSelector'

type Tab = 'ask' | 'benchmark'

export default function App() {
  const [documents, setDocuments] = useState<string[]>([])
  const [models, setModels] = useState<Model[]>([])
  const [document, setDocument] = useState<string | null>(null) // null = all documents
  const [selected, setSelected] = useState<string[]>([])
  const [tab, setTab] = useState<Tab>('ask')
  const [error, setError] = useState('')
  const [benchmark, setBenchmark] = useState<BenchmarkState>({ status: 'none' })

  useEffect(() => {
    Promise.all([getDocuments(), getModels(), getLatestBenchmark()])
      .then(([docs, mods, latest]) => {
        setDocuments(docs)
        setModels(mods)
        setSelected(mods.slice(0, MAX_MODELS).map((m) => m.id))
        setBenchmark(latest)
      })
      .catch(() => setError('Cannot reach the backend. Is it running on http://localhost:8000?'))
  }, [])

  // While a benchmark runs, poll for progress every 2 s.
  useEffect(() => {
    if (benchmark.status !== 'running') return
    const timer = setInterval(() => getLatestBenchmark().then(setBenchmark).catch(() => {}), 2000)
    return () => clearInterval(timer)
  }, [benchmark.status])

  const selectedModels = models.filter((m) => selected.includes(m.id))

  return (
    <div className="mx-auto max-w-7xl space-y-4 p-4 sm:p-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">RAG Playground &amp; Model Benchmark</h1>
          <p className="text-slate-500">Ask questions on your documents and compare performance across models.</p>
        </div>
        <label className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm">
          <span className="text-slate-500">Document:</span>
          <select
            className="bg-transparent font-medium outline-none"
            value={document ?? ''}
            onChange={(e) => setDocument(e.target.value || null)}
          >
            <option value="">All documents</option>
            {documents.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </label>
      </header>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-red-700">{error}</div>}

      <ModelSelector models={models} selected={selected} onChange={setSelected} />

      <div className="grid gap-4 lg:grid-cols-[2fr_3fr]">
        <section className="rounded-xl border border-slate-200 bg-white">
          <div className="flex border-b border-slate-200">
            {(['ask', 'benchmark'] as const).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`flex-1 px-4 py-3 font-medium ${
                  tab === t ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-slate-500'
                }`}
              >
                {t === 'ask' ? 'Ask a Question' : 'Run Benchmark'}
              </button>
            ))}
          </div>
          {/* Both panels stay mounted so switching tabs keeps their state. */}
          <div className={`p-4 ${tab === 'ask' ? '' : 'hidden'}`}>
            <AskPanel models={selectedModels} document={document} />
          </div>
          <div className={`p-4 ${tab === 'benchmark' ? '' : 'hidden'}`}>
            <BenchmarkPanel
              models={selectedModels}
              document={document}
              state={benchmark}
              onStarted={() =>
                setBenchmark({ status: 'running', document, model_ids: selected, progress: { done: 0, total: null } })
              }
            />
          </div>
        </section>

        <section className="min-w-0 rounded-xl border border-slate-200 bg-white p-4">
          <h2 className="mb-1 text-lg font-semibold">Benchmark Results</h2>
          <BenchmarkResults state={benchmark} models={models} />
        </section>
      </div>
    </div>
  )
}
