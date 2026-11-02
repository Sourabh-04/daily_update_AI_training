import { Bar, BarChart, CartesianGrid, Cell, LabelList, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { BenchmarkState, Model, SummaryRow } from '../api'
import { ModelBadge } from './ModelSelector'

type Props = { state: BenchmarkState; models: Model[] }

const pct = (v: number | null) => (v == null ? '—' : `${Math.round(v * 100)}%`)
const num = (v: number | null) => (v == null ? '—' : v.toFixed(2))
const secs = (v: number | null) => (v == null ? '—' : `${v.toFixed(2)} s`)

export function BenchmarkResults({ state, models }: Props) {
  const modelFor = (id: string): Model =>
    models.find((m) => m.id === id) ?? { id, display_name: id, provider: '?', tagline: '', is_open: false, color: '#94a3b8' }

  if (state.status === 'none') return <Empty text="No benchmark yet. Start one from the Run Benchmark tab." />
  if (state.status === 'running') return <Empty text="Benchmark running… results appear here when it finishes." />
  if (state.status === 'failed') return <Empty text={`Benchmark failed: ${state.error}`} />

  const { summary, total_questions } = state
  const bestAccuracy = Math.max(...summary.map((s) => s.accuracy ?? 0))
  const best = summary.filter((s) => s.accuracy === bestAccuracy)
  const latencies = summary.map((s) => s.avg_latency_s).filter((v): v is number => v != null)
  const avgLatency = latencies.length ? latencies.reduce((a, b) => a + b, 0) / latencies.length : null
  const byAccuracy = [...summary].sort((a, b) => (b.accuracy ?? 0) - (a.accuracy ?? 0))

  return (
    <div className="space-y-4">
      <p className="text-sm text-slate-500">
        {state.document ?? 'All documents'} · {total_questions} test questions · finished{' '}
        {new Date(state.finished_at).toLocaleString()}
      </p>

      <div className="grid gap-3 sm:grid-cols-3">
        <StatCard
          label="Best Accuracy"
          value={pct(bestAccuracy)}
          sub={best.map((s) => modelFor(s.model_id).display_name).join(', ')}
          className="bg-emerald-50"
        />
        <StatCard label="Avg. Latency" value={secs(avgLatency)} sub="across models" className="bg-sky-50" />
        <StatCard label="Total Questions" value={String(total_questions)} sub="per model" className="bg-violet-50" />
      </div>

      <div className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              {['Model', 'Accuracy ↓', 'Relevance', 'Groundedness', 'Avg. Latency', 'Failed'].map((h) => (
                <th key={h} className="px-3 py-2 font-medium whitespace-nowrap">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {byAccuracy.map((s) => (
              <tr key={s.model_id} className="border-t border-slate-200">
                <td className="px-3 py-2">
                  <div className="flex items-center gap-2 whitespace-nowrap">
                    <ModelBadge model={modelFor(s.model_id)} />
                    {modelFor(s.model_id).display_name}
                  </div>
                </td>
                <td className={`px-3 py-2 whitespace-nowrap ${s.accuracy === bestAccuracy ? 'bg-emerald-50 font-semibold' : ''}`}>
                  {pct(s.accuracy)} ({s.correct}/{s.total})
                </td>
                <td className="px-3 py-2">{num(s.avg_relevance)}</td>
                <td className="px-3 py-2">{num(s.avg_groundedness)}</td>
                <td className="px-3 py-2 whitespace-nowrap">{secs(s.avg_latency_s)}</td>
                <td className={`px-3 py-2 ${s.failed ? 'text-red-600' : ''}`}>{s.failed}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <ModelBarChart
          title="Accuracy Comparison"
          rows={summary}
          value={(s) => s.accuracy}
          format={pct}
          domain={[0, 1]}
          modelFor={modelFor}
        />
        <ModelBarChart
          title="Avg. Response Time (seconds)"
          rows={summary}
          value={(s) => s.avg_latency_s}
          format={secs}
          domain={[0, 'auto']}
          modelFor={modelFor}
        />
      </div>
    </div>
  )
}

function Empty({ text }: { text: string }) {
  return <p className="py-8 text-center text-slate-400">{text}</p>
}

function StatCard({ label, value, sub, className }: { label: string; value: string; sub: string; className: string }) {
  return (
    <div className={`rounded-lg p-3 ${className}`}>
      <div className="text-sm text-slate-600">{label}</div>
      <div className="text-2xl font-bold">{value}</div>
      <div className="truncate text-sm text-slate-500">{sub}</div>
    </div>
  )
}

type ChartProps = {
  title: string
  rows: SummaryRow[]
  value: (s: SummaryRow) => number | null
  format: (v: number | null) => string
  domain: [number, number | 'auto']
  modelFor: (id: string) => Model
}

// Bars keep the model's own color (same as its card and badge); every bar is labelled with its value.
function ModelBarChart({ title, rows, value, format, domain, modelFor }: ChartProps) {
  const data = rows.map((s) => {
    const model = modelFor(s.model_id)
    return { name: model.display_name, value: value(s), color: model.color }
  })

  return (
    <div className="rounded-lg border border-slate-200 p-3">
      <h3 className="mb-2 font-medium">{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 20, right: 8, left: -8, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="#e2e8f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#475569' }} tickLine={false} axisLine={{ stroke: '#cbd5e1' }} />
          <YAxis
            domain={domain}
            tickFormatter={(v: number) => format(v)}
            tick={{ fontSize: 12, fill: '#64748b' }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip formatter={(v) => [format(Number(v)), title]} cursor={{ fill: '#f1f5f9' }} />
          <Bar dataKey="value" radius={[4, 4, 0, 0]} maxBarSize={56}>
            {data.map((d) => (
              <Cell key={d.name} fill={d.color} />
            ))}
            <LabelList dataKey="value" position="top" formatter={(v) => format(v == null ? null : Number(v))} fill="#334155" fontSize={12} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
