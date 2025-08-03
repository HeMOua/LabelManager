<template>
  <div class="project-management">
    <div class="project-header">
      <h1>项目管理</h1>
      <button @click="showCreateDialog = true" class="create-btn">创建项目</button>
    </div>

    <div class="project-filters">
      <div class="filter-group">
        <label>状态筛选:</label>
        <el-select v-model="selectedStatus" @change="filterProjects" style="width: 120px;" placeholder="所有状态">
          <el-option label="所有状态" value=""></el-option>
          <el-option label="进行中" value="active"></el-option>
          <el-option label="已完成" value="completed"></el-option>
          <el-option label="已暂停" value="paused"></el-option>
        </el-select>
      </div>
      
      <div class="filter-group">
        <label>搜索:</label>
        <el-input 
          v-model="searchQuery" 
          @input="filterProjects"
          type="text" 
          placeholder="搜索项目名称或描述..."
          class="search-input"
        />
      </div>
    </div>

    <div class="project-statistics">
      <div class="stat-card">
        <h3>总项目数</h3>
        <div class="stat-number">{{ filteredProjects.length }}</div>
      </div>
      <div class="stat-card">
        <h3>进行中</h3>
        <div class="stat-number">{{ activeProjectsCount }}</div>
      </div>
      <div class="stat-card">
        <h3>已完成</h3>
        <div class="stat-number">{{ completedProjectsCount }}</div>
      </div>
      <div class="stat-card">
        <h3>总图片数</h3>
        <div class="stat-number">{{ totalImagesCount }}</div>
      </div>
    </div>

    <div class="project-list">
      <div class="list-header">
        <div class="sort-controls">
          <label>排序:</label>
          <el-select v-model="sortBy" @change="sortProjects" style="width: 150px;">
            <el-option label="名称" value="name"></el-option>
            <el-option label="创建时间" value="createdAt"></el-option>
            <el-option label="更新时间" value="updatedAt"></el-option>
            <el-option label="图片数量" value="imageCount"></el-option>
          </el-select>
          <button @click="toggleSortOrder" class="sort-toggle">
            {{ sortOrder === 'asc' ? '↑' : '↓' }}
          </button>
        </div>
        
        <div class="view-controls">
          <button 
            @click="viewMode = 'grid'"
            :class="{ active: viewMode === 'grid' }"
            class="view-btn"
          >
            网格
          </button>
          <button 
            @click="viewMode = 'list'"
            :class="{ active: viewMode === 'list' }"
            class="view-btn"
          >
            列表
          </button>
        </div>
      </div>

      <div v-if="viewMode === 'grid'" class="project-grid">
        <div 
          v-for="project in sortedProjects" 
          :key="project.id" 
          class="project-card"
          @click="selectProject(project)"
          :class="{ selected: selectedProject?.id === project.id }"
        >
          <div class="project-status" :class="project.status">
            {{ getStatusText(project.status) }}
          </div>
          
          <div class="project-info">
            <h3>{{ project.name }}</h3>
            <p class="project-description">{{ project.description }}</p>
            
            <div class="project-stats">
              <div class="stat-item">
                <span class="stat-label">图片数:</span>
                <span class="stat-value">{{ project.imageCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">标签数:</span>
                <span class="stat-value">{{ project.tagCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">标注率:</span>
                <span class="stat-value">{{ project.labelProgress }}%</span>
              </div>
            </div>
            
            <div class="project-dates">
              <small>创建: {{ formatDate(project.createdAt) }}</small>
              <small>更新: {{ formatDate(project.updatedAt) }}</small>
            </div>
          </div>
          
          <div class="project-actions">
            <button @click.stop="editProject(project)" class="edit-btn">编辑</button>
            <button @click.stop="duplicateProject(project)" class="duplicate-btn">复制</button>
            <button @click.stop="deleteProject(project)" class="delete-btn">删除</button>
          </div>
        </div>
      </div>

      <div v-else class="project-table">
        <table>
          <thead>
            <tr>
              <th>名称</th>
              <th>状态</th>
              <th>图片数</th>
              <th>标签数</th>
              <th>标注进度</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="project in sortedProjects" 
              :key="project.id"
              @click="selectProject(project)"
              :class="{ selected: selectedProject?.id === project.id }"
            >
              <td>
                <div class="project-name-cell">
                  <strong>{{ project.name }}</strong>
                  <small>{{ project.description }}</small>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="project.status">
                  {{ getStatusText(project.status) }}
                </span>
              </td>
              <td>{{ project.imageCount }}</td>
              <td>{{ project.tagCount }}</td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: project.labelProgress + '%' }"
                    ></div>
                  </div>
                  <span>{{ project.labelProgress }}%</span>
                </div>
              </td>
              <td>{{ formatDate(project.createdAt) }}</td>
              <td>
                <div class="table-actions">
                  <button @click.stop="editProject(project)" class="edit-btn">编辑</button>
                  <button @click.stop="duplicateProject(project)" class="duplicate-btn">复制</button>
                  <button @click.stop="deleteProject(project)" class="delete-btn">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 项目详情侧边栏 -->
    <div v-if="selectedProject" class="project-details-sidebar">
      <div class="sidebar-header">
        <h2>{{ selectedProject.name }}</h2>
        <button @click="selectedProject = null" class="close-sidebar">×</button>
      </div>
      
      <div class="sidebar-content">
        <div class="detail-section">
          <h3>基本信息</h3>
          <div class="detail-item">
            <label>状态:</label>
            <span class="status-badge" :class="selectedProject.status">
              {{ getStatusText(selectedProject.status) }}
            </span>
          </div>
          <div class="detail-item">
            <label>描述:</label>
            <p>{{ selectedProject.description || '无描述' }}</p>
          </div>
          <div class="detail-item">
            <label>创建时间:</label>
            <span>{{ formatDate(selectedProject.createdAt) }}</span>
          </div>
          <div class="detail-item">
            <label>最后更新:</label>
            <span>{{ formatDate(selectedProject.updatedAt) }}</span>
          </div>
        </div>

        <div class="detail-section">
          <h3>数据统计</h3>
          <div class="stats-grid">
            <div class="stats-item">
              <div class="stats-number">{{ selectedProject.imageCount }}</div>
              <div class="stats-label">总图片</div>
            </div>
            <div class="stats-item">
              <div class="stats-number">{{ selectedProject.tagCount }}</div>
              <div class="stats-label">标签数</div>
            </div>
            <div class="stats-item">
              <div class="stats-number">{{ selectedProject.labeledImages }}</div>
              <div class="stats-label">已标注</div>
            </div>
            <div class="stats-item">
              <div class="stats-number">{{ selectedProject.labelProgress }}%</div>
              <div class="stats-label">完成度</div>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>标签分布</h3>
          <div class="tag-distribution">
            <div 
              v-for="tag in projectTags" 
              :key="tag.id"
              class="tag-item"
            >
              <div class="tag-color" :style="{ backgroundColor: tag.color }"></div>
              <span class="tag-name">{{ tag.name }}</span>
              <span class="tag-count">{{ tag.count }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>最近图片</h3>
          <div class="recent-images">
            <div 
              v-for="image in recentImages" 
              :key="image.id"
              class="recent-image"
            >
              <img :src="image.thumbnail" :alt="image.name" />
              <span>{{ image.name }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>快速操作</h3>
          <div class="quick-actions">
            <button @click="goToGallery(selectedProject)" class="action-btn gallery-btn">
              查看图片库
            </button>
            <button @click="goToTags(selectedProject)" class="action-btn tags-btn">
              管理标签
            </button>
            <button @click="exportProject(selectedProject)" class="action-btn export-btn">
              导出数据
            </button>
            <button @click="generateReport(selectedProject)" class="action-btn report-btn">
              生成报告
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑对话框 -->
    <div v-if="showCreateDialog || showEditDialog" class="dialog-overlay" @click="closeDialogs">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ showCreateDialog ? '创建' : '编辑' }}项目</h3>
          <button @click="closeDialogs" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveProject" class="dialog-form">
          <div class="form-group">
            <label>项目名称:</label>
            <input v-model="projectForm.name" type="text" required />
          </div>
          
          <div class="form-group">
            <label>项目状态:</label>
            <select v-model="projectForm.status" required>
              <option value="active">进行中</option>
              <option value="completed">已完成</option>
              <option value="paused">已暂停</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>项目描述:</label>
            <textarea v-model="projectForm.description" rows="4" placeholder="请输入项目描述..."></textarea>
          </div>
          
          <div class="form-group">
            <label>预设标签:</label>
            <div class="preset-tags">
              <div 
                v-for="tag in availableTags" 
                :key="tag.id"
                class="preset-tag"
                @click="togglePresetTag(tag)"
                :class="{ selected: projectForm.presetTags.includes(tag.id) }"
              >
                <div class="tag-color" :style="{ backgroundColor: tag.color }"></div>
                <span>{{ tag.name }}</span>
              </div>
            </div>
          </div>
          
          <div class="dialog-actions">
            <button type="button" @click="closeDialogs" class="cancel-btn">取消</button>
            <button type="submit" class="save-btn">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import type { Project, Tag } from '@/types/index'
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'ProjectManagement',
  setup() {
    const router = useRouter()

    const projects = ref<Project[]>([])
    const filteredProjects = ref<Project[]>([])
    const selectedProject = ref<Project | null>(null)
    const selectedStatus = ref('')
    const searchQuery = ref('')
    const sortBy = ref<'name' | 'createdAt' | 'updatedAt' | 'imageCount'>('updatedAt')
    const sortOrder = ref<'asc' | 'desc'>('desc')
    const viewMode = ref<'grid' | 'list'>('grid')
    const showCreateDialog = ref(false)
    const showEditDialog = ref(false)
    const availableTags = ref([])
    const projectTags = ref([])
    const recentImages = ref([])

    const projectForm = reactive({
      id: 0,
      name: '',
      description: '',
      status: 'active',
      presetTags: []
    })

    const activeProjectsCount = computed(() => {
      return filteredProjects.value.filter(p => p.status === 'active').length
    })

    const completedProjectsCount = computed(() => {
      return filteredProjects.value.filter(p => p.status === 'completed').length
    })

    const totalImagesCount = computed(() => {
      return filteredProjects.value.reduce((total, p) => total + p.imageCount, 0)
    })

    const sortedProjects = computed(() => {
      const sorted = [...filteredProjects.value].sort((a, b) => {
        let aVal: any = a[sortBy.value]
        let bVal: any = b[sortBy.value]

        if (typeof aVal === 'string') {
          aVal = aVal.toLowerCase()
          bVal = bVal.toLowerCase()
        } else if (typeof aVal === 'number') {
          aVal = Number(aVal)
          bVal = Number(bVal)
        } else if (aVal instanceof Date) {
          aVal = new Date(aVal).getTime()
          bVal = new Date(bVal).getTime()
        }
        
        if (sortOrder.value === 'asc') {
          return aVal > bVal ? 1 : -1
        } else {
          return aVal < bVal ? 1 : -1
        }
      })
      return sorted
    })

    const loadProjects = async () => {
      // 模拟项目数据
      projects.value = [
        {
          id: 1,
          name: '医疗影像标注项目',
          description: '用于医疗诊断的X光片和CT图像标注',
          status: 'active',
          imageCount: 1250,
          tagCount: 15,
          labeledImages: 892,
          labelProgress: 71,
          createdAt: new Date('2024-01-15'),
          updatedAt: new Date('2024-01-30')
        },
        {
          id: 2,
          name: '自动驾驶数据集',
          description: '道路场景图像的物体检测和分割标注',
          status: 'active',
          imageCount: 3200,
          tagCount: 25,
          labeledImages: 2880,
          labelProgress: 90,
          createdAt: new Date('2024-01-10'),
          updatedAt: new Date('2024-01-29')
        },
        {
          id: 3,
          name: '动物分类数据集',
          description: '野生动物图像的种类分类标注',
          status: 'completed',
          imageCount: 800,
          tagCount: 12,
          labeledImages: 800,
          labelProgress: 100,
          createdAt: new Date('2023-12-01'),
          updatedAt: new Date('2024-01-15')
        },
        {
          id: 4,
          name: '工业缺陷检测',
          description: '工业产品表面缺陷的识别和标注',
          status: 'paused',
          imageCount: 500,
          tagCount: 8,
          labeledImages: 150,
          labelProgress: 30,
          createdAt: new Date('2024-01-20'),
          updatedAt: new Date('2024-01-25')
        }
      ]
      filterProjects()
    }

    const loadAvailableTags = async () => {
      availableTags.value = [
        { id: 1, name: '人物', color: '#ff6b6b' },
        { id: 2, name: '动物', color: '#4ecdc4' },
        { id: 3, name: '建筑', color: '#45b7d1' },
        { id: 4, name: '车辆', color: '#feca57' },
        { id: 5, name: '自然景观', color: '#96ceb4' },
        { id: 6, name: '器械', color: '#a55eea' },
        { id: 7, name: '食物', color: '#fd79a8' },
        { id: 8, name: '文字', color: '#fdcb6e' }
      ]
    }

    const filterProjects = () => {
      let filtered = [...projects.value]
      
      if (selectedStatus.value) {
        filtered = filtered.filter(p => p.status === selectedStatus.value)
      }
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(p => 
          p.name.toLowerCase().includes(query) ||
          (p.description && p.description.toLowerCase().includes(query))
        )
      }
      
      filteredProjects.value = filtered
    }

    const sortProjects = () => {
      // sortedProjects computed 会自动处理排序
    }

    const toggleSortOrder = () => {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    }

    const selectProject = (project: Project) => {
      selectedProject.value = project
      loadProjectDetails(project.id)
    }

    const loadProjectDetails = async (projectId: number) => {
      // 模拟项目详情数据
      projectTags.value = [
        { id: 1, name: '正常', color: '#96ceb4', count: 450 },
        { id: 2, name: '异常', color: '#ff6b6b', count: 125 },
        { id: 3, name: '疑似', color: '#feca57', count: 75 }
      ]
      
      recentImages.value = [
        { id: 1, name: 'img_001.jpg', thumbnail: '/api/images/thumbnails/img_001.jpg' },
        { id: 2, name: 'img_002.jpg', thumbnail: '/api/images/thumbnails/img_002.jpg' },
        { id: 3, name: 'img_003.jpg', thumbnail: '/api/images/thumbnails/img_003.jpg' },
        { id: 4, name: 'img_004.jpg', thumbnail: '/api/images/thumbnails/img_004.jpg' }
      ]
    }

    const getStatusText = (status: Project['status']) => {
      const statusMap = {
        active: '进行中',
        completed: '已完成',
        paused: '已暂停'
      }
      return statusMap[status] || status
    }

    const editProject = (project: Project) => {
      projectForm.id = project.id
      projectForm.name = project.name
      projectForm.description = project.description
      projectForm.status = project.status
      projectForm.presetTags = []
      showEditDialog.value = true
    }

    const duplicateProject = async (project: Project) => {
      if (confirm(`确定要复制项目 "${project.name}" 吗？`)) {
        console.log('复制项目:', project)
        // 实现复制逻辑
        await loadProjects()
      }
    }

    const deleteProject = async (project: Project) => {
      if (confirm(`确定要删除项目 "${project.name}" 吗？此操作不可恢复！`)) {
        console.log('删除项目:', project)
        // 实现删除逻辑
        await loadProjects()
      }
    }

    const resetProjectForm = () => {
      projectForm.id = null
      projectForm.name = ''
      projectForm.description = ''
      projectForm.status = 'active'
      projectForm.presetTags = []
    }

    const closeDialogs = () => {
      showCreateDialog.value = false
      showEditDialog.value = false
      resetProjectForm()
    }

    const togglePresetTag = (tag: Tag) => {
      const index = projectForm.presetTags.indexOf(tag.id)
      if (index > -1) {
        projectForm.presetTags.splice(index, 1)
      } else {
        projectForm.presetTags.push(tag.id)
      }
    }

    const saveProject = async () => {
      try {
        if (showEditDialog.value) {
          console.log('更新项目:', projectForm)
        } else {
          console.log('创建项目:', projectForm)
        }
        
        await loadProjects()
        closeDialogs()
      } catch (error) {
        console.error('保存失败:', error)
      }
    }

    const goToGallery = (project: Project) => {
      router.push({ name: 'ImageGallery', query: { project: project.id } })
    }

    const goToTags = (project: Project) => {
      router.push({ name: 'TagManagement', query: { project: project.id } })
    }

    const exportProject = (project: Project) => {
      console.log('导出项目数据:', project)
      // 实现导出功能
    }

    const generateReport = (project: Project) => {
      console.log('生成项目报告:', project)
      // 实现报告生成功能
    }

    const formatDate = (date: string) => {
      return new Date(date).toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      loadProjects()
      loadAvailableTags()
    })

    return {
      projects,
      filteredProjects,
      selectedProject,
      selectedStatus,
      searchQuery,
      sortBy,
      sortOrder,
      viewMode,
      showCreateDialog,
      showEditDialog,
      availableTags,
      projectTags,
      recentImages,
      projectForm,
      activeProjectsCount,
      completedProjectsCount,
      totalImagesCount,
      sortedProjects,
      filterProjects,
      sortProjects,
      toggleSortOrder,
      selectProject,
      getStatusText,
      editProject,
      duplicateProject,
      deleteProject,
      closeDialogs,
      togglePresetTag,
      saveProject,
      goToGallery,
      goToTags,
      exportProject,
      generateReport,
      formatDate
    }
  }
}
</script>

<style scoped>
.project-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  position: relative;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.project-header h1 {
  margin: 0;
  color: #333;
}

.create-btn {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.create-btn:hover {
  background-color: #0056b3;
}

.project-filters {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: bold;
  color: #666;
  white-space: nowrap;
}

.project-statistics {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  flex: 1;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #666;
  font-size: 14px;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
}

.project-list {
  margin-bottom: 30px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-controls label {
  font-weight: bold;
  color: #666;
  white-space: nowrap;
}

.sort-toggle {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
}

.view-controls {
  display: flex;
  gap: 5px;
}

.view-btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background-color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.view-btn:first-child {
  border-radius: 4px 0 0 4px;
}

.view-btn:last-child {
  border-radius: 0 4px 4px 0;
}

.view-btn.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.project-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background-color: white;
  position: relative;
}

.project-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.project-card.selected {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}

.project-status {
  position: absolute;
  top: 15px;
  right: 15px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.project-status.active {
  background-color: #28a745;
}

.project-status.completed {
  background-color: #007bff;
}

.project-status.paused {
  background-color: #ffc107;
  color: #212529;
}

.project-info h3 {
  margin: 0 0 10px 0;
  color: #333;
  padding-right: 80px;
}

.project-description {
  color: #666;
  font-size: 14px;
  margin: 0 0 15px 0;
  line-height: 1.4;
}

.project-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #666;
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.project-dates {
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 12px;
  margin-bottom: 15px;
}

.project-actions {
  display: flex;
  gap: 8px;
}

.project-table {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
}

.project-table table {
  width: 100%;
  border-collapse: collapse;
}

.project-table th,
.project-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.project-table th {
  background-color: #f8f9fa;
  font-weight: bold;
  color: #333;
}

.project-table tbody tr {
  cursor: pointer;
  transition: background-color 0.2s;
}

.project-table tbody tr:hover {
  background-color: #f8f9fa;
}

.project-table tbody tr.selected {
  background-color: rgba(0,123,255,0.1);
}

.project-name-cell strong {
  display: block;
  margin-bottom: 2px;
}

.project-name-cell small {
  color: #666;
  font-size: 12px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.status-badge.active {
  background-color: #28a745;
}

.status-badge.completed {
  background-color: #007bff;
}

.status-badge.paused {
  background-color: #ffc107;
  color: #212529;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #28a745;
  transition: width 0.3s;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn, .duplicate-btn {
  padding: 4px 8px;
  border: 1px solid;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.edit-btn {
  background-color: #ffc107;
  border-color: #ffc107;
  color: #212529;
}

.duplicate-btn {
  background-color: #6c757d;
  border-color: #6c757d;
  color: white;
}

.delete-btn {
  background-color: #dc3545;
  border-color: #dc3545;
  color: white;
}

.project-details-sidebar {
  position: fixed;
  top: 0;
  right: 0;
  width: 450px;
  height: 100vh;
  background-color: white;
  border-left: 1px solid #e0e0e0;
  z-index: 1000;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
}

.sidebar-header h2 {
  margin: 0;
  color: #333;
}

.close-sidebar {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.sidebar-content {
  padding: 20px;
}

.detail-section {
  margin-bottom: 30px;
}

.detail-section h3 {
  margin-bottom: 15px;
  color: #333;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 5px;
}

.detail-item {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.detail-item label {
  font-weight: bold;
  width: 80px;
  color: #666;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stats-item {
  text-align: center;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.stats-number {
  font-size: 24px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 5px;
}

.stats-label {
  font-size: 12px;
  color: #666;
}

.tag-distribution {
  max-height: 200px;
  overflow-y: auto;
}

.tag-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.tag-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.tag-name {
  flex: 1;
  font-size: 14px;
}

.tag-count {
  font-size: 12px;
  color: #666;
  background-color: #e9ecef;
  padding: 2px 6px;
  border-radius: 10px;
}

.recent-images {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.recent-image {
  text-align: center;
}

.recent-image img {
  width: 100%;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 5px;
}

.recent-image span {
  font-size: 12px;
  color: #666;
  display: block;
  word-break: break-all;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.action-btn {
  padding: 10px;
  border: 1px solid;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  text-align: center;
  transition: background-color 0.3s;
}

.gallery-btn {
  background-color: #007bff;
  border-color: #007bff;
  color: white;
}

.tags-btn {
  background-color: #28a745;
  border-color: #28a745;
  color: white;
}

.export-btn {
  background-color: #ffc107;
  border-color: #ffc107;
  color: #212529;
}

.report-btn {
  background-color: #6c757d;
  border-color: #6c757d;
  color: white;
}

.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.dialog {
  background: white;
  border-radius: 8px;
  width: 600px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.dialog-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.dialog-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.preset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  max-height: 150px;
  overflow-y: auto;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
}

.preset-tag {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 15px;
  cursor: pointer;
  background-color: white;
  transition: all 0.3s;
}

.preset-tag:hover {
  background-color: #e9ecef;
}

.preset-tag.selected {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.preset-tag .tag-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

.cancel-btn, .save-btn {
  padding: 10px 20px;
  border: 1px solid;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  background-color: white;
  border-color: #6c757d;
  color: #6c757d;
}

.save-btn {
  background-color: #007bff;
  border-color: #007bff;
  color: white;
}

.cancel-btn:hover {
  background-color: #f8f9fa;
}

.save-btn:hover {
  background-color: #0056b3;
}
</style>
