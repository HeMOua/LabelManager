import { api } from '@/utils/api'

// 图片API
export const imageApi = {
  uploadImage: (projectId, formData) => api.post(`/images/upload/${projectId}`, formData),
  getProjectImages: (projectId, params = {}) => api.get(`/images/project/${projectId}`, { params }),
  getImage: (id) => api.get(`/images/${id}`),
  updateImageTags: (id, tagIds) => api.put(`/images/${id}/tags`, tagIds),
  deleteImage: (id) => api.delete(`/images/${id}`),
  getImageUrl: (id, thumbnail = false) => api.get(`/images/${id}/url`, { params: { thumbnail } })
}