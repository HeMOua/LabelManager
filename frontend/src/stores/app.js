import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const currentProject = ref(null)
  const projects = ref([])
  const loading = ref(false)

  const setCurrentProject = (project) => {
    currentProject.value = project
    localStorage.setItem('currentProject', JSON.stringify(project))
  }

  const initCurrentProject = () => {
    const saved = localStorage.getItem('currentProject')
    if (saved) {
      currentProject.value = JSON.parse(saved)
    }
  }

  const setLoading = (value) => {
    loading.value = value
  }

  return {
    currentProject,
    projects,
    loading,
    setCurrentProject,
    initCurrentProject,
    setLoading
  }
})