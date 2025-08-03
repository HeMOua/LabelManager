export interface Project {
  id: number
  name: string
  status: 'active' | 'completed' | 'paused'
  imageCount: number
  description?: string
  createdAt?: string
  updatedAt?: string
}
