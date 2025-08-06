export interface Tag {
  id: number
  name: string
  color: string
  category?: string
  createdAt?: string
  updatedAt?: string
}

export interface TagCreate {
  name: string
  color?: string
}

export interface TagUpdate {
  name?: string
  color?: string
}