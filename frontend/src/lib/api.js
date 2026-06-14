import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8500/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

function getErrorMessage(error) {
  const payload = error.response?.data

  if (!payload) {
    return error.message || 'Request failed'
  }

  if (typeof payload.errors === 'string') {
    return payload.errors
  }

  if (payload.errors?.error) {
    if (typeof payload.errors.error === 'string') {
      return payload.errors.error
    }

    return Object.entries(payload.errors.error)
      .map(([field, message]) => `${field}: ${message}`)
      .join(', ')
  }

  if (payload.message) {
    return payload.message
  }

  return 'Request failed'
}

api.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(new Error(getErrorMessage(error))),
)

export const authApi = {
  currentUser: () => api.get('/me'),
  login: (payload) => api.post('/login', payload),
  logout: () => api.post('/logout', {}),
  register: (payload) => api.post('/register', payload),
}

export const usersApi = {
  list: (params) => api.get('/users', { params }),
  create: (payload) => api.post('/register', payload),
}

export const artistsApi = {
  availableUsers: (params) => api.get('/artists/available-users', { params }),
  list: (params) => api.get('/artists', { params }),
  create: (payload) => api.post('/artists/create', payload),
  update: (payload) => api.post('/artists/update', payload),
  remove: (id) => api.post('/artists/delete', { id }),
}

export const songsApi = {
  availableArtists: (params) => api.get('/songs/available-artists', { params }),
  list: (params) => api.get('/songs', { params }),
  create: (payload) => api.post('/songs/create', payload),
  update: (payload) => api.post('/songs/update', payload),
  remove: (id) => api.post('/songs/delete', { id }),
}
