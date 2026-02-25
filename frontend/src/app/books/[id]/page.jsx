'use client'

import { useState, useEffect } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { useAuth } from '../lib/auth-context'
import { api } from '../lib/api'
import { BookViewModal } from '../components/BookViewModal'
import {
  IconArrowLeft,
  IconBook2,
  IconEye,
  IconLoader2,
  IconSparkles,
  IconStar
} from '@tabler/icons-react'

export default function BookDetailPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const params = useParams()
  const id = Number(params.id)

  const [book, setBook] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [aiSimilar, setAiSimilar] = useState([])
  const [loadingAiSimilar, setLoadingAiSimilar] = useState(false)
  const [err, setErr] = useState('')
  const [action, setAction] = useState('')
  const [rating, setRating] = useState(3)
  const [reviewText, setReviewText] = useState('')
  const [viewModalOpen, setViewModalOpen] = useState(false)

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  useEffect(() => {
    if (!user || !id) return

    api.books
      .get(id)
      .then(setBook)
      .catch((e) => setErr(e?.message || 'Failed'))

    api.books
      .analysis(id)
      .then(setAnalysis)
      .catch(() => setAnalysis(null))

    setLoadingAiSimilar(true)

    api.recommendations
      .suggestionsSimilar(id, 3)
      .then((r) => setAiSimilar(r?.suggestions || []))
      .catch(() => setAiSimilar([]))
      .finally(() => setLoadingAiSimilar(false))
  }, [user, id])

  async function doBorrow() {
    setAction('borrowing')
    setErr('')
    try {
      await api.books.borrow(id)
      const updated = await api.books.get(id)
      setBook(updated)
      toast.success('Book borrowed successfully')
    } catch (e) {
      const msg = e?.message || 'Failed'
      setErr(msg)
      toast.error(msg)
    } finally {
      setAction('')
    }
  }

  async function doReturn() {
    setAction('returning')
    setErr('')
    try {
      await api.books.return(id)
      const updated = await api.books.get(id)
      setBook(updated)
      toast.success('Book returned successfully')
    } catch (e) {
      const msg = e?.message || 'Failed'
      setErr(msg)
      toast.error(msg)
    } finally {
      setAction('')
    }
  }

  async function doReview(e) {
    e.preventDefault()
    setAction('reviewing')
    setErr('')
    try {
      await api.books.review(id, rating, reviewText || undefined)
      setReviewText('')

      const updated = await api.books.get(id)
      setBook(updated)

      const analysisData = await api.books.analysis(id)
      setAnalysis(analysisData)

      setTimeout(() => {
        api.books.analysis(id).then(setAnalysis).catch(() => {})
      }, 3000)

      toast.success('Review submitted')
    } catch (e) {
      const msg = e?.message || 'Failed'
      setErr(msg)
      toast.error(msg)
    } finally {
      setAction('')
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

  if (!book) {
    return (
      <div className="card">
        <p className="text-error">{err || 'Loading...'}</p>
        <Link href="/books" className="btn-secondary mt-4 inline-flex items-center gap-2">
          <IconArrowLeft className="h-4 w-4" />
          Back to books
        </Link>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Link
        href="/books"
        className="inline-flex items-center gap-2 text-sm font-medium text-muted transition hover:text-slate-900"
      >
        <IconArrowLeft className="h-4 w-4" />
        Back to books
      </Link>

      <div className="card">
        <div className="flex gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary-100">
            <IconBook2 className="h-8 w-8 text-primary-600" />
          </div>
          <div className="min-w-0 flex-1">
            <h1 className="page-title mb-1">{book.title}</h1>
            {book.author && <p className="text-muted mb-2">{book.author}</p>}
            {book.genre && (
              <span className="inline-block rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700">
                {book.genre}
              </span>
            )}
          </div>
        </div>
      </div>

      {err && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-error">
          {err}
        </div>
      )}

      {/* Buttons */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={doBorrow}
          disabled={!!action || book.currently_borrowed_by_me}
          className="btn-primary"
        >
          {action === 'borrowing' ? (
            <>
              <IconLoader2 className="h-4 w-4 animate-spin" />
              Borrowing...
            </>
          ) : (
            'Borrow'
          )}
        </button>

        <button
          onClick={doReturn}
          disabled={!!action || !book.currently_borrowed_by_me}
          className="btn-secondary"
        >
          {action === 'returning' ? (
            <>
              <IconLoader2 className="h-4 w-4 animate-spin" />
              Returning...
            </>
          ) : (
            'Return'
          )}
        </button>

        {book.file_name && (
          <button
            type="button"
            onClick={() => setViewModalOpen(true)}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <IconEye className="h-4 w-4" />
            View
          </button>
        )}
      </div>

      <BookViewModal
        open={viewModalOpen}
        onClose={() => setViewModalOpen(false)}
        bookId={id}
        bookTitle={book.title}
        fileName={book.file_name}
      />
    </div>
  )
}