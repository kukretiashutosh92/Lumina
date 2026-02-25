'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { useAuth } from '../lib/auth-context'
import { api } from '../lib/api'
import {
  IconSparkles,
  IconChevronRight,
  IconLoader2,
  IconBook2,
} from '@tabler/icons-react'

export default function RecommendationsPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  const [items, setItems] = useState([])
  const [err, setErr] = useState('')
  const [prefGenre, setPrefGenre] = useState('')
  const [prefWeight, setPrefWeight] = useState(1)
  const [prefMsg, setPrefMsg] = useState('')
  const [genrePrefs, setGenrePrefs] = useState([])
  const [aiSuggestions, setAiSuggestions] = useState([])
  const [loadingRecs, setLoadingRecs] = useState(true)

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  function loadRecommendations() {
    if (!user) return

    setLoadingRecs(true)
    setErr('')

    Promise.all([
      api.recommendations
        .list()
        .then(setItems)
        .catch((e) => setErr(e?.message || 'Failed')),

      api.preferences
        .list()
        .then(setGenrePrefs)
        .catch(() => setGenrePrefs([])),

      api.recommendations
        .suggestions(10)
        .then((r) => setAiSuggestions(r?.suggestions || []))
        .catch(() => setAiSuggestions([])),
    ]).finally(() => setLoadingRecs(false))
  }

  useEffect(() => {
    if (!user) return
    loadRecommendations()
  }, [user])

  async function addPreference(e) {
    e.preventDefault()
    if (!prefGenre.trim()) return

    setPrefMsg('')

    try {
      await api.preferences.add(prefGenre.trim(), prefWeight)
      toast.success('Genre preference added')
      loadRecommendations()
    } catch (e) {
      const msg = e?.message || 'Failed'
      setPrefMsg(msg)
      toast.error(msg)
    }
  }

  if (loading || !user) {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <span className="flex items-center gap-2 text-muted">
          <IconLoader2 className="h-5 w-5 animate-spin" />
          Loading...
        </span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="page-title flex items-center gap-2">
        <IconSparkles className="h-8 w-8 text-primary-600" />
        Recommendations
      </h1>

      <p className="text-muted">
        Add a genre below to see two kinds of recommendations:
        books in your library and AI suggestions.
      </p>

      {/* Genre Preferences */}
      <div className="card">
        <h2 className="mb-3 font-semibold text-slate-900">
          Genre preferences
        </h2>

        {genrePrefs.length > 0 && (
          <div className="mb-4 flex flex-wrap gap-2">
            {genrePrefs.map((p) => (
              <span
                key={p.genre}
                className="inline-flex items-center rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-800"
              >
                {p.genre} (weight {p.weight})
              </span>
            ))}
          </div>
        )}

        <form
          onSubmit={addPreference}
          className="flex flex-wrap items-end gap-4"
        >
          <div className="min-w-[140px] flex-1">
            <label className="label">Genre</label>
            <input
              type="text"
              value={prefGenre}
              onChange={(e) => setPrefGenre(e.target.value)}
              className="input-field"
              placeholder="e.g. Fiction, Sci-Fi"
            />
          </div>

          <div className="w-24">
            <label className="label">Weight</label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={prefWeight}
              onChange={(e) => setPrefWeight(Number(e.target.value))}
              className="input-field"
            />
          </div>

          <button type="submit" className="btn-primary">
            Add
          </button>
        </form>

        {prefMsg && (
          <p className="mt-3 text-sm text-error">{prefMsg}</p>
        )}
      </div>

      {/* Error */}
      {err && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-error">
          {err}
        </div>
      )}

      {/* Loading */}
      {loadingRecs && (
        <div className="card flex min-h-[200px] items-center justify-center py-12">
          <span className="flex items-center gap-2 text-muted">
            <IconLoader2 className="h-6 w-6 animate-spin" />
            Loading recommendations...
          </span>
        </div>
      )}

      {/* Empty */}
      {!loadingRecs && items.length === 0 && !err && (
        <div className="card py-12 text-center">
          <IconBook2 className="mx-auto mb-4 h-12 w-12 text-slate-300" />
          <p className="mb-2 text-muted">No recommendations yet.</p>
        </div>
      )}

      {/* AI Suggestions */}
      {!loadingRecs && aiSuggestions.length > 0 && (
        <div className="space-y-3">
          <h2 className="flex items-center gap-2 font-semibold text-slate-900">
            <IconSparkles className="h-5 w-5 text-primary-600" />
            AI Suggestions
          </h2>

          <ul className="grid gap-3">
            {aiSuggestions.map((s, i) => (
              <li
                key={`${s.title}-${i}`}
                className="card flex items-center gap-4"
              >
                <IconBook2 className="h-5 w-5 text-primary-600" />
                <div className="min-w-0 flex-1">
                  <h3 className="truncate font-semibold text-slate-900">
                    {s.title}
                  </h3>
                  <p className="text-sm text-muted">{s.author}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Library Matches */}
      {!loadingRecs && items.length > 0 && (
        <div className="space-y-3">
          <h2 className="font-semibold text-slate-900">
            In your library
          </h2>

          <ul className="grid gap-4">
            {items.map((b) => (
              <li key={b.id}>
                <Link
                  href={`/books/${b.id}`}
                  className="card-hover flex items-center justify-between gap-4"
                >
                  <div className="min-w-0 flex-1">
                    <h3 className="truncate font-semibold text-slate-900">
                      {b.title}
                    </h3>
                    {b.author && (
                      <p className="mt-0.5 text-sm text-muted">
                        {b.author}
                      </p>
                    )}
                  </div>
                  <IconChevronRight className="h-5 w-5 shrink-0 text-slate-400" />
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}