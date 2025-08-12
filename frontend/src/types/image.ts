import type { Tag } from "./tag"


export interface Image {
  id: number
  projectId: number
  url: string
  filename?: string
  filePath?: string
  thumbnailPath?: string
  fileSize?: number
  width?: number
  height?: number
  tags: Tag[]
  createdAt: string
  updatedAt: string
}
