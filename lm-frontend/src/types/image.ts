import type { Tag } from "./tag"


export interface Image {
  id: number
  projectId: number
  url: string
  thumbnailUrl?: string
  tags: Tag[]
  createdAt: string
  updatedAt: string
}
