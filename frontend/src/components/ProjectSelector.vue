<template>
  <el-select
    v-model="selectedProject"
    placeholder="选择项目"
    @change="handleProjectChange"
    style="width: 200px"
  >
    <el-option
      v-for="project in projects"
      :key="project.id"
      :label="project.name"
      :value="project.id"
    />
  </el-select>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAppStore } from '@/stores/app'
import { projectApi } from '@/api/project'
import type { Project } from '@/types'

const appStore = useAppStore()
const projects = ref<Project[]>([])

const selectedProject = computed({
  get: () => appStore.currentProject?.id,
  set: (value) => {
    const project = projects.value.find(p => p.id === value)
    if (project) {
      appStore.setCurrentProject(project)
    }
  }
})

const handleProjectChange = (projectId: number) => {
  selectedProject.value = projectId
}

const loadProjects = async () => {
  try {
    const data = await projectApi.getProjects()
    projects.value = data
    
    // 如果没有当前项目且有项目列表，选择第一个
    if (!appStore.currentProject && data.length > 0) {
      appStore.setCurrentProject(data[0])
    }
  } catch (error) {
    console.error('Failed to load projects:', error)
  }
}

onMounted(() => {
  appStore.initCurrentProject()
  loadProjects()
})
</script>