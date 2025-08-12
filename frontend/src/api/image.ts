import api from '@/utils/api'

// 图片API
export const imageApi = {
  uploadImage: (projectId: number, formData: FormData) => api.post(`/images/upload/${projectId}`, formData),
  getProjectImages: (projectId: number, params = {}) => api.get(`/images/project/${projectId}`, { params }),
  getImage: (id: number) => api.get(`/images/${id}`),
  updateImageTags: (id: number, tagIds: number[]) => api.put(`/images/${id}/tags`, tagIds),
  deleteImage: (id: number) => api.delete(`/images/${id}`),
  getImageUrl: (id: number, thumbnail = false) => api.get(`/images/${id}/url`, { params: { thumbnail } })
}