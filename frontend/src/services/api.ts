import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Auth endpoints
export const login = async (email: string, password: string) => {
  const response = await api.post('/auth/login', { email, password })
  return response.data
}

export const register = async (email: string, password: string, full_name: string) => {
  const response = await api.post('/auth/register', { email, password, full_name })
  return response.data
}

// Document endpoints
export const getDocuments = async () => {
  const response = await api.get('/documents/')
  return response.data
}

export const getDocument = async (id: string) => {
  const response = await api.get(`/documents/${id}`)
  return response.data
}

export const uploadDocument = async (file: File, title?: string, description?: string) => {
  const formData = new FormData()
  formData.append('file', file)
  if (title) formData.append('title', title)
  if (description) formData.append('description', description)

  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
  return response.data
}

export const updateDocument = async (id: string, data: { title?: string; description?: string; status?: string }) => {
  const response = await api.patch(`/documents/${id}`, data)
  return response.data
}

export const deleteDocument = async (id: string) => {
  await api.delete(`/documents/${id}`)
}

export const verifyDocument = async (id: string) => {
  const response = await api.post(`/documents/${id}/verify`)
  return response.data
}

export default api
