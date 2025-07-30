import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 项目API
export const projectApi = {
  getProjects: () => api.get('/projects/'),
  createProject: (data) => api.post('/projects/', data),
  updateProject: (id, data) => api.put(`/projects/${id}`, data),
  deleteProject: (id) => api.delete(`/projects/${id}`)
}

// 标签API
export const tagApi = {
  getTags: () => api.get('/tags/'),
  createTag: (data) => api.post('/tags/', data),
  updateTag: (id, data) => api.put(`/tags/${id}`, data),
  deleteTag: (id) => api.delete(`/tags/${id}`)
}

// 图片API
export const imageApi = {
  uploadImage: (projectId, formData) => api.post(`/images/upload/${projectId}`, formData),
  getProjectImages: (projectId, params = {}) => api.get(`/images/project/${projectId}`, { params }),
  getImage: (id) => api.get(`/images/${id}`),
  updateImageTags: (id, tagIds) => api.put(`/images/${id}/tags`, tagIds),
  deleteImage: (id) => api.delete(`/images/${id}`),
  getImageUrl: (id, thumbnail = false) => api.get(`/images/${id}/url`, { params: { thumbnail } })
}

// 树形结构API
export const treeApi = {
  buildTree: (projectId, data) => api.post(`/tree/build/${projectId}`, data),
  getAvailableCategories: (projectId) => api.get(`/tree/categories/${projectId}`)
}

export default api