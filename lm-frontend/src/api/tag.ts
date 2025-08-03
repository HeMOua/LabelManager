import { api } from '@/utils/api'

// 标签API
export const tagApi = {
  getTags: () => api.get('/tags/'),
  createTag: (data) => api.post('/tags/', data),
  updateTag: (id, data) => api.put(`/tags/${id}`, data),
  deleteTag: (id) => api.delete(`/tags/${id}`)
}