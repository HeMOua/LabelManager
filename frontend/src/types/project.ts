export interface Project {
  id: number
  name: string
  status: 'active' | 'completed' | 'paused'
  imageCount: number
  description?: string
  createdAt?: string
  updatedAt?: string
}

export interface ProjectCreate {
  name: string
  description?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  status?: 'active' | 'completed' | 'paused'
}