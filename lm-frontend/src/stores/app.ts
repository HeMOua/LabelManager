import type { Project } from '@/types/index'
import { menuList } from '@/utils/menuList'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const currentProject = ref<Project | null>(null)
  const projects = ref<Project[]>([])
  const loading = ref(false)
  // 侧边栏是否收缩
  const collapsed = ref(false)
  // 是否全屏
  const isFullscreen = ref(false)

  const setCurrentProject = (project: Project) => {
    currentProject.value = project
    localStorage.setItem('currentProject', JSON.stringify(project))
  }

  const initCurrentProject = () => {
    const saved = localStorage.getItem('currentProject')
    if (saved) {
      currentProject.value = JSON.parse(saved)
    }
  }

  const setLoading = (value: boolean) => {
    loading.value = value
  }

  const toggleCollapsed = () => {
    collapsed.value = !collapsed.value
  }

  const toggleFullscreen = () => {
    if (!isFullscreen.value) {
      document.documentElement.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
    isFullscreen.value = !isFullscreen.value
  }

  return {
    currentProject,
    projects,
    loading,
    collapsed,
    isFullscreen,
    menuList,
    setCurrentProject,
    initCurrentProject,
    setLoading,
    toggleCollapsed,
    toggleFullscreen
  }
})
