import type { Model } from '../api'

export const MAX_MODELS = 3

export function ModelBadge({ model }: { model: Model }) {
  return (
    <span
      className="flex size-9 shrink-0 items-center justify-center rounded-lg text-sm font-bold text-white"
      style={{ backgroundColor: model.color }}
    >
      {model.provider[0]}
    </span>
  )
}

type Props = {
  models: Model[]
  selected: string[]
  onChange: (selected: string[]) => void
}

export function ModelSelector({ models, selected, onChange }: Props) {
  const toggle = (id: string) =>
    onChange(selected.includes(id) ? selected.filter((s) => s !== id) : [...selected, id])

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4">
      <h2 className="mb-3 font-semibold">Select Models (up to {MAX_MODELS})</h2>
      <div className="grid gap-3 sm:grid-cols-3">
        {models.map((m) => {
          const checked = selected.includes(m.id)
          const disabled = !checked && selected.length >= MAX_MODELS
          return (
            <label
              key={m.id}
              className={`flex cursor-pointer items-center gap-3 rounded-lg border-2 p-3 ${
                checked ? 'border-indigo-500 bg-indigo-50/40' : 'border-slate-200'
              } ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
            >
              <input
                type="checkbox"
                className="size-4 accent-indigo-600"
                checked={checked}
                disabled={disabled}
                onChange={() => toggle(m.id)}
              />
              <ModelBadge model={m} />
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  <span className="truncate font-medium">{m.display_name}</span>
                  {m.is_open && (
                    <span className="rounded bg-indigo-100 px-1.5 text-xs text-indigo-700">Open</span>
                  )}
                </div>
                <div className="truncate text-sm text-slate-500">{m.tagline}</div>
              </div>
            </label>
          )
        })}
      </div>
    </section>
  )
}
