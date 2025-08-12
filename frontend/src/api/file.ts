import api from '@/utils/api'

// 图片API
export const fileApi = {
  serveFile: (path: string) => api.get(`/files/url/${path}`),
  getFileInfo: (path: string) => api.post(`/files/info/${path}`),
}