// Types and calls for the FastAPI backend (backend/api.py).

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type Model = {
  id: string
  display_name: string
  provider: string
  tagline: string
  is_open: boolean
  color: string
}

export type Source = { id: string; text: string; source: string; distance: number }

export type Answer = { model_id: string; answer: string; latency_s: number | null; error: string }

export type AskResponse = { sources: Source[]; answers: Answer[] }

export type SummaryRow = {
  model_id: string
  correct: number
  total: number
  accuracy: number | null
  failed: number
  avg_relevance: number | null
  avg_groundedness: number | null
  avg_latency_s: number | null
}

export type BenchmarkState =
  | { status: 'none' }
  | { status: 'running'; document: string | null; model_ids: string[]; progress: { done: number; total: number | null } }
  | { status: 'failed'; error: string }
  | {
      status: 'completed'
      document: string | null
      model_ids: string[]
      finished_at: string
      total_questions: number
      summary: SummaryRow[]
    }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(API_URL + path, {
    ...init,
    headers: { 'Content-Type': 'application/json' },
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(typeof body?.detail === 'string' ? body.detail : `Request failed (${res.status})`)
  }
  return res.json()
}

export const getDocuments = () => request<string[]>('/documents')

export const getModels = () => request<Model[]>('/models')

export const ask = (question: string, document: string | null, model_ids: string[]) =>
  request<AskResponse>('/ask', { method: 'POST', body: JSON.stringify({ question, document, model_ids }) })

export const startBenchmark = (document: string | null, model_ids: string[]) =>
  request<{ status: string }>('/benchmark', { method: 'POST', body: JSON.stringify({ document, model_ids }) })

export const getLatestBenchmark = () => request<BenchmarkState>('/benchmark/latest')
