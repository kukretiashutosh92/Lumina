const BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

function getToken() {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('token')
}

async function request(path, opts = {}) {
  const { body, ...rest } = opts

  const headers = {
    'Content-Type': 'application/json',
    ...(rest.headers || {}),
  }

  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, {
    ...rest,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({
      detail: res.statusText,
    }))
    throw new Error(err.detail || String(err) || res.statusText)
  }

  if (res.status === 204) return

  return res.json()
}

async function formRequest(path, form) {
  const token = getToken()
  const headers = {}

  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers,
    body: form,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({
      detail: res.statusText,
    }))
    throw new Error(err.detail || String(err) || res.statusText)
  }

  return res.json()
}

export const api = {
  auth: {
    signup: (email, password, full_name) =>
      request('/auth/signup', {
        method: 'POST',
        body: { email, password, full_name },
      }),

    login: (email, password) =>
      request('/auth/login', {
        method: 'POST',
        body: { email, password },
      }),

    me: () => request('/auth/me'),

    updateMe: (full_name) =>
      request('/auth/me', {
        method: 'PUT',
        body: { full_name },
      }),
  },

  books: {
    list: (skip = 0, limit = 20) =>
      request(`/books?skip=${skip}&limit=${limit}`),

    get: (id) => request(`/books/${id}`),

    create: (form) => formRequest('/books', form),

    update: (id, data) =>
      request(`/books/${id}`, {
        method: 'PUT',
        body: data,
      }),

    delete: (id) =>
      request(`/books/${id}`, {
        method: 'DELETE',
      }),

    borrow: (id) =>
      request(`/books/${id}/borrow`, {
        method: 'POST',
      }),

    return: (id) =>
      request(`/books/${id}/return`, {
        method: 'POST',
      }),

    review: (id, rating, text) =>
      request(`/books/${id}/reviews`, {
        method: 'POST',
        body: { rating, text },
      }),

    analysis: (id) =>
      request(`/books/${id}/analysis`),

    getFile: async (id) => {
      const token = getToken()

      const res = await fetch(`${BASE}/books/${id}/file`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({
          detail: res.statusText,
        }))
        throw new Error(err.detail || res.statusText)
      }

      return res.blob()
    },
  },

  recommendations: {
    list: () => request('/recommendations'),

    suggestions: (limit) =>
      request(
        `/recommendations/suggestions${
          limit != null ? `?limit=${limit}` : ''
        }`
      ),

    suggestionsSimilar: (bookId, limit) =>
      request(
        `/recommendations/suggestions/similar/${bookId}${
          limit != null ? `?limit=${limit}` : ''
        }`
      ),

    similar: (bookId, limit) =>
      request(
        `/recommendations/similar/${bookId}${
          limit != null ? `?limit=${limit}` : ''
        }`
      ),
  },

  preferences: {
    list: () => request('/preferences'),

    add: (genre, weight) =>
      request('/preferences', {
        method: 'POST',
        body: { genre, weight },
      }),
  },
}


