import type { ProjectCreate, ProjectUpdate } from '@/types'
import api from '@/utils/api'

// 项目API
export const projectApi = {
  getProjects: () => api.get('/projects/'),
  createProject: (data: ProjectCreate) => api.post('/projects/', data),
  updateProject: (id: number, data: ProjectUpdate) => api.put(`/projects/${id}`, data),
  deleteProject: (id: number) => api.delete(`/projects/${id}`)
}
