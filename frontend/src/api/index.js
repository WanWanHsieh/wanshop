import axios from 'axios'

const base = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export const api = axios.create({
  baseURL: base + '/api',
  timeout: 15000,
})

// Auto-prefix /api and handle FormData upload
export function fileUpload(url, files) {
  const fixed = url.startsWith('/api/') ? url : '/api' + (url.startsWith('/') ? url : '/' + url)
  const fd = new FormData()
  for (const f of files) fd.append('files', f)
  return axios.post(base + fixed, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}
