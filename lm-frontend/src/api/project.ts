import api from '@/utils/api'

// 项目API
export const projectApi = {
  getProjects: () => api.get('/projects/'),
  createProject: (data) => api.post('/projects/', data),
  updateProject: (id: number, data: any) => api.put(`/projects/${id}`, data),
  deleteProject: (id: number) => api.delete(`/projects/${id}`)
}
