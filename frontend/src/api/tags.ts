import type { TagCreate, TagSearch, TagUpdate } from '@/types'
import api from '@/utils/api'

// 标签API
export const tagApi = {
  getTags: (params: TagSearch) => api.get('/tags/', { params }),
  createTag: (data: TagCreate) => api.post('/tags/', data),
  updateTag: (id: number, data: TagUpdate) => api.put(`/tags/${id}`, data),
  deleteTag: (id: number) => api.delete(`/tags/${id}`)
}