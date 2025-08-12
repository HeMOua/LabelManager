import api from '@/utils/api'


// 树形结构API
export const treeApi = {
  buildTree: (projectId: number, data: any) => api.post(`/tree/build/${projectId}`, data),
  getAvailableCategories: (projectId: number) => api.get(`/tree/categories/${projectId}`)
}
