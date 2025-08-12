
export interface MenuItem {
  id: string
  title: string
  icon?: string
  path?: string
  children?: MenuItem[]
  closable?: boolean
  hidden?: boolean
}

export interface TabItem {
  name: string
  title: string
  path: string
  closable?: boolean
}

export interface UserInfo {
  username: string
  avatar: string
  email: string
  role: string
}