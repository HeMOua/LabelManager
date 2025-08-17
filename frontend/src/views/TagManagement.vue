<template>
  <div class="tag-management">
    <div class="tag-management-header">
      <el-page-header @back="$router.go(-1)" content="标签管理">
        <template #extra>
          <div class="tag-controls">
            <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
              创建标签
            </el-button>
          </div>
        </template>
      </el-page-header>
    </div>

    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-select v-model="selectedTagType" placeholder="标签类型">
            <el-option label="全部标签" value="all" />
            <el-option label="全局标签" value="global" />
            <el-option label="项目标签" value="project" />
          </el-select>
        </el-col>
        
        <el-col :span="6">
          <el-select 
            v-model="selectedProject" 
            @change="loadTags" 
            placeholder="选择项目" 
            clearable
            :disabled="selectedTagType === 'global'"
          >
            <el-option label="所有项目" value="" />
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-col>
        
        <el-col :span="6">
          <el-select v-model="selectedCategory" @change="filterTags" placeholder="选择分类" clearable>
            <el-option label="所有分类" value="" />
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-col>
        
        <el-col :span="6">
          <el-input
            v-model="searchQuery"
            @input="filterTags"
            placeholder="搜索标签名称..."
            :prefix-icon="Search"
            clearable
          />
        </el-col>
      </el-row>
      
      <el-row :gutter="16" style="margin-top: 16px;">
        <el-col :span="18">
          <div class="quick-filters">
            <el-button-group>
              <el-button
                :type="viewMode === 'grid' ? 'primary' : 'default'"
                @click="viewMode = 'grid'"
                :icon="Grid"
              />
              <el-button
                :type="viewMode === 'list' ? 'primary' : 'default'"
                @click="viewMode = 'list'"
                :icon="List"
              />
            </el-button-group>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="batch-actions" v-if="selectedTagType === 'global'">
            <el-button 
              type="info" 
              icon="CopyDocument"
              @click="showCopyDialog = true"
              :disabled="!filteredTags.length"
            >
              复制到项目
            </el-button>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <div class="project-statistics">
      <div class="stat-card">
        <h3>总标签数</h3>
        <div class="stat-number">{{ filteredTags.length }}</div>
      </div>
      <div class="stat-card">
        <h3>全局标签</h3>
        <div class="stat-number">{{ globalTagsCount }}</div>
      </div>
      <div class="stat-card">
        <h3>项目标签</h3>
        <div class="stat-number">{{ projectTagsCount }}</div>
      </div>
      <div class="stat-card">
        <h3>已使用</h3>
        <div class="stat-number">{{ usedTagsCount }}</div>
      </div>
    </div>

    <el-card class="content-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>标签列表</span>
          <div class="sort-controls">
            <el-select v-model="sortBy" style="width: 120px;">
              <el-option label="名称" value="name" />
              <el-option label="使用次数" value="imageCount" />
              <el-option label="创建时间" value="createdAt" />
            </el-select>
            <el-button
              @click="toggleSortOrder"
              :icon="sortOrder === 'asc' ? SortUp : SortDown"
              circle
            />
          </div>
        </div>
      </template>

      <div v-if="viewMode === 'grid'" class="tag-grid">
        <el-card 
          v-for="tag in sortedTags" 
          :key="tag.id" 
          class="tag-card"
          @click="selectTag(tag)"
          :class="{ selected: selectedTag?.id === tag.id }"
          shadow="hover"
        >
          <div class="tag-color-bar" :style="{ backgroundColor: tag.color }"></div>
          <div class="tag-info">
            <div class="tag-header">
              <h3>{{ tag.name }}</h3>
              <el-tag 
                :type="tag.isGlobal ? 'success' : 'info'" 
                size="small"
                class="tag-type"
              >
                {{ tag.isGlobal ? '全局' : '项目' }}
              </el-tag>
            </div>
            <el-tag size="small" type="warning">{{ tag.category }}</el-tag>
            <div class="project-info" v-if="!tag.isGlobal && tag.projectName">
              <el-tag size="small" type="primary">{{ tag.projectName }}</el-tag>
            </div>
            <div class="tag-stats">
              <el-statistic 
                title="使用次数" 
                :value="tag.image_count" 
                :value-style="{ fontSize: '14px' }" 
              />
              <span class="created-date">{{ formatDate(tag.createdAt) }}</span>
            </div>
          </div>
          <div class="tag-actions">
            <el-button size="small" @click.stop="editTag(tag)" :icon="Edit" circle />
            <el-button size="small" type="danger" @click.stop="deleteTag(tag)" :icon="Delete" circle />
          </div>
        </el-card>
      </div>

      <div v-else>
        <el-table :data="sortedTags" @row-click="selectTag" row-key="id">
          <el-table-column label="颜色" width="60">
            <template #default="{ row }">
              <div class="color-cell" :style="{ backgroundColor: row.color }"></div>
            </template>
          </el-table-column>
          <el-table-column property="name" label="名称" />
          <el-table-column label="类型" width="80">
            <template #default="{ row }">
              <el-tag :type="row.isGlobal ? 'success' : 'info'" size="small">
                {{ row.isGlobal ? '全局' : '项目' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="分类">
            <template #default="{ row }">
              <el-tag size="small" type="warning">{{ row.category }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="所属项目" width="120">
            <template #default="{ row }">
              <el-tag v-if="!row.isGlobal && row.projectName" size="small" type="primary">
                {{ row.projectName }}
              </el-tag>
              <span v-else-if="row.isGlobal" class="global-indicator">-</span>
              <span v-else class="unknown-project">未知项目</span>
            </template>
          </el-table-column>
          <el-table-column property="image_count" label="使用次数" width="100" />
          <el-table-column label="创建时间" width="150">
            <template #default="{ row }">
              {{ formatDate(row.createdAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button size="small" @click.stop="editTag(row)" :icon="Edit" circle />
              <el-button size="small" type="danger" @click.stop="deleteTag(row)" :icon="Delete" circle />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>

    <!-- 标签详情抽屉 -->
    <el-drawer
      v-model="showTagDetails"
      :title="selectedTag?.name"
      direction="rtl"
      size="400px"
    >
      <div v-if="selectedTag" class="tag-details-content">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="颜色">
            <div class="color-display" :style="{ backgroundColor: selectedTag.color }"></div>
          </el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="selectedTag.isGlobal ? 'success' : 'info'">
              {{ selectedTag.isGlobal ? '全局标签' : '项目标签' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="分类">
            {{ selectedTag.category }}
          </el-descriptions-item>
          <el-descriptions-item label="所属项目" v-if="!selectedTag.isGlobal">
            {{ selectedTag.projectName || '未知项目' }}
          </el-descriptions-item>
          <el-descriptions-item label="使用次数">
            {{ selectedTag.imageCount }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(selectedTag.createdAt) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">关联图片 ({{ tagImages.length }})</el-divider>
        <div class="related-images">
          <el-image
            v-for="image in tagImages"
            :key="image.id"
            :src="image.thumbnail"
            :alt="image.name"
            fit="cover"
            class="related-image"
            lazy
          />
        </div>
      </div>
    </el-drawer>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="showDialog"
      :title="showCreateDialog ? '创建标签' : '编辑标签'"
      width="500px"
    >
      <el-form ref="tagFormRef" :model="tagForm" :rules="tagFormRules" label-width="80px">
        <el-form-item label="标签类型" prop="tag_type">
          <el-radio-group v-model="tagForm.tagType" :disabled="showEditDialog">
            <el-radio label="global">全局标签</el-radio>
            <el-radio label="project">项目标签</el-radio>
          </el-radio-group>
          <div class="form-help-text">
            <span v-if="tagForm.tagType === 'global'">全局标签可以在所有项目中使用</span>
            <span v-else>项目标签只能在指定项目中使用</span>
          </div>
        </el-form-item>
        
        <el-form-item 
          label="所属项目" 
          prop="project_id"
          v-if="tagForm.tagType === 'project'"
        >
          <el-select v-model="tagForm.projectId" placeholder="选择项目" style="width: 100%">
            <el-option
              v-for="project in projects"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select 
            v-model="tagForm.category" 
            placeholder="选择或输入分类" 
            style="width: 100%"
            filterable
            allow-create
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="颜色" prop="color">
          <div class="color-picker">
            <el-color-picker v-model="tagForm.color" />
            <div class="preset-colors">
              <div 
                v-for="color in presetColors" 
                :key="color"
                class="preset-color"
                :style="{ backgroundColor: color }"
                @click="tagForm.color = color"
                :class="{ active: tagForm.color === color }"
              ></div>
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeDialogs">取消</el-button>
        <el-button type="primary" @click="saveTag" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 复制标签到项目对话框 -->
    <el-dialog
      v-model="showCopyDialog"
      title="复制全局标签到项目"
      width="600px"
    >
      <div class="copy-dialog-content">
        <el-form :model="copyForm" label-width="100px">
          <el-form-item label="目标项目" required>
            <el-select v-model="copyForm.project_id" placeholder="选择目标项目" style="width: 100%">
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="选择标签">
            <div class="tag-selection">
              <div class="selection-header">
                <el-checkbox 
                  v-model="selectAllGlobalTags"
                  :indeterminate="isGlobalTagsIndeterminate"
                  @change="handleSelectAllGlobalTags"
                >
                  全选 ({{ copyForm.tag_ids.length }}/{{ globalTags.length }})
                </el-checkbox>
              </div>
              <div class="tag-list">
                <el-checkbox-group v-model="copyForm.tag_ids">
                  <div 
                    v-for="tag in globalTags" 
                    :key="tag.id"
                    class="tag-checkbox-item"
                  >
                    <el-checkbox :label="tag.id">
                      <div class="tag-display">
                        <div 
                          class="tag-color-dot" 
                          :style="{ backgroundColor: tag.color }"
                        ></div>
                        <span class="tag-name">{{ tag.name }}</span>
                        <el-tag size="small" type="warning">{{ tag.category }}</el-tag>
                      </div>
                    </el-checkbox>
                  </div>
                </el-checkbox-group>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <el-button @click="showCopyDialog = false">取消</el-button>
        <el-button 
          type="primary" 
          @click="copyTagsToProject"
          :loading="copying"
          :disabled="!copyForm.project_id || !copyForm.tag_ids.length"
        >
          复制标签 ({{ copyForm.tag_ids.length }})
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Search, Grid, List, Edit, Delete, 
  SortUp, SortDown
} from '@element-plus/icons-vue'
import { tagApi } from '@/api/tags'
import { projectApi } from '@/api/project'

interface Tag {
  id: number
  name: string
  category: string
  color: string
  projectId: number | null
  createdAt: string
  tagType: 'global' | 'project'
  isGlobal: boolean
  imageCount: number
  projectName?: string
}

interface Project {
  id: number
  name: string
}

const tags = ref<Tag[]>([])
const filteredTags = ref<Tag[]>([])
const selectedTag = ref<Tag | null>(null)
const selectedTagType = ref('all')
const selectedProject = ref<number | string>('')
const selectedCategory = ref('')
const searchQuery = ref('')
const sortBy = ref('name')
const sortOrder = ref('asc')
const viewMode = ref('grid')
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showTagDetails = ref(false)
const showCopyDialog = ref(false)
const projects = ref<Project[]>([])
const categories = ref<string[]>([])
const tagImages = ref([])
const tagFormRef = ref()
const saving = ref(false)
const copying = ref(false)

const tagForm = reactive({
  id: null as number | null,
  name: '',
  category: '',
  color: '#409EFF',
  tagType: 'global' as 'global' | 'project',
  projectId: null as number | null
})

const copyForm = reactive({
  projectId: null as number | null,
  tagIds: [] as number[]
})

const tagFormRules = {
  name: [
    { required: true, message: '请输入标签名称', trigger: 'blur' }
  ],
  category: [
    { required: true, message: '请输入分类', trigger: 'blur' }
  ],
  tagType: [
    { required: true, message: '请选择标签类型', trigger: 'change' }
  ],
  projectId: [
    {
      validator: (rule: any, value: any, callback: any) => {
        if (tagForm.tagType === 'project' && !value) {
          callback(new Error('请选择所属项目'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

const showDialog = computed(() => showCreateDialog.value || showEditDialog.value)

const presetColors = [
  '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
  '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43',
  '#a55eea', '#26de81', '#fd79a8', '#fdcb6e', '#6c5ce7'
]

const globalTagsCount = computed(() => {
  return filteredTags.value.filter(tag => tag.isGlobal).length
})

const projectTagsCount = computed(() => {
  return filteredTags.value.filter(tag => !tag.isGlobal).length
})

const usedTagsCount = computed(() => {
  return filteredTags.value.filter(tag => tag.imageCount > 0).length
})

const sortedTags = computed(() => {
  const sorted = [...filteredTags.value].sort((a, b) => {
    let aVal = a[sortBy.value as keyof Tag]
    let bVal = b[sortBy.value as keyof Tag]
    
    if (sortBy.value === 'created_at') {
      aVal = new Date(aVal as string).getTime()
      bVal = new Date(bVal as string).getTime()
    }
    
    if (sortOrder.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
  return sorted
})

const globalTags = computed(() => {
  return tags.value.filter(tag => tag.isGlobal)
})

const selectAllGlobalTags = computed({
  get: () => {
    return copyForm.tagIds.length === globalTags.value.length && globalTags.value.length > 0
  },
  set: (val: boolean) => {
    if (val) {
      copyForm.tagIds = globalTags.value.map(tag => tag.id)
    } else {
      copyForm.tagIds = []
    }
  }
})

const isGlobalTagsIndeterminate = computed(() => {
  return copyForm.tagIds.length > 0 && copyForm.tagIds.length < globalTags.value.length
})

const loadProjects = async () => {
  try {
    const response = await projectApi.getProjects()
    if (response?.data) {
      projects.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载项目列表失败')
    console.error('Load projects error:', error)
  }
}

const loadTags = async () => {
  try {
    const params: any = {}
    
    if (selectedTagType.value !== 'all') {
      params.tagType = selectedTagType.value
    }
    
    if (selectedProject.value && selectedTagType.value === 'project') {
      params.projectId = selectedProject.value
    }
    
    const response = await tagApi.getTags(params)
    if (response?.data) {
      tags.value = response.data
      filterTags()
      loadCategories()
    }
  } catch (error) {
    ElMessage.error('加载标签列表失败')
    console.error('Load tags error:', error)
  }
}

const loadCategories = () => {
  const categorySet = new Set<string>()
  tags.value.forEach(tag => {
    if (tag.category) {
      categorySet.add(tag.category)
    }
  })
  categories.value = Array.from(categorySet)
}

const filterTags = () => {
  let filtered = [...tags.value]
  
  if (selectedCategory.value) {
    filtered = filtered.filter(tag => tag.category === selectedCategory.value)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(tag => 
      tag.name.toLowerCase().includes(query) ||
      tag.category.toLowerCase().includes(query)
    )
  }
  
  filteredTags.value = filtered
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const selectTag = (tag: Tag) => {
  selectedTag.value = tag
  showTagDetails.value = true
  loadTagImages(tag.id)
}

const loadTagImages = async (tagId: number) => {
  // 模拟关联图片数据
  tagImages.value = []
}

const editTag = (tag: Tag) => {
  tagForm.id = tag.id
  tagForm.name = tag.name
  tagForm.category = tag.category
  tagForm.color = tag.color
  tagForm.tagType = tag.tagType
  tagForm.projectId = tag.projectId
  showEditDialog.value = true
}

const deleteTag = async (tag: Tag) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${tag.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await tagApi.deleteTag(tag.id)
    if (response?.code === 200) {
      ElMessage.success('标签删除成功')
      await loadTags()
    } else {
      ElMessage.error(response?.message || '标签删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('标签删除失败')
      console.error('Delete tag error:', error)
    }
  }
}

const resetTagForm = () => {
  tagForm.id = null
  tagForm.name = ''
  tagForm.category = ''
  tagForm.color = '#409EFF'
  tagForm.tagType = 'global'
  tagForm.projectId = null
}

const closeDialogs = () => {
  showCreateDialog.value = false
  showEditDialog.value = false
  resetTagForm()
}

const saveTag = async () => {
  try {
    await tagFormRef.value.validate()
    
    saving.value = true
    
    const tagData = {
      name: tagForm.name,
      category: tagForm.category,
      color: tagForm.color,
      projectId: tagForm.tagType === 'global' ? null : tagForm.projectId
    }
    
    let response
    if (showEditDialog.value && tagForm.id) {
      response = await tagApi.updateTag(tagForm.id, tagData)
    } else {
      response = await tagApi.createTag(tagData)
    }
    
    if (response?.code === 200) {
      ElMessage.success(showEditDialog.value ? '标签更新成功' : '标签创建成功')
      await loadTags()
      closeDialogs()
    } else {
      ElMessage.error(response?.message || '保存失败')
    }
  } catch (error) {
    if (error !== false) {
      ElMessage.error('保存失败')
      console.error('Save tag error:', error)
    }
  } finally {
    saving.value = false
  }
}

const handleSelectAllGlobalTags = (checked: boolean) => {
  if (checked) {
    copyForm.tagIds = globalTags.value.map(tag => tag.id)
  } else {
    copyForm.tagIds = []
  }
}

const copyTagsToProject = async () => {
  if (!copyForm.projectId || !copyForm.tagIds.length) {
    ElMessage.warning('请选择项目和标签')
    return
  }
  
  copying.value = true
  try {
    const response = await tagApi.copyGlobalTagsToProject(copyForm.projectId, copyForm.tagIds)
    if (response?.code === 200) {
      ElMessage.success(`成功复制 ${copyForm.tagIds.length} 个标签到项目`)
      showCopyDialog.value = false
      copyForm.projectId = null
      copyForm.tagIds = []
      await loadTags()
    } else {
      ElMessage.error(response?.message || '复制失败')
    }
  } catch (error) {
    ElMessage.error('复制标签失败')
    console.error('Copy tags error:', error)
  } finally {
    copying.value = false
  }
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

// 监听标签类型变化
watch(() => selectedTagType.value, () => {
  if (selectedTagType.value === 'global') {
    selectedProject.value = ''
  }
  loadTags()
})

onMounted(() => {
  loadProjects()
  loadTags()
})
</script>

<style scoped>
.tag-management {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.tag-management-header {
  margin-bottom: 24px;
}

.filter-card {
  margin-bottom: 24px;
}

.quick-filters {
  display: flex;
  align-items: center;
  gap: 12px;
}

.batch-actions {
  text-align: right;
}

.statistics-row {
  margin-bottom: 20px;
}

.content-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.tag-card {
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.tag-card:hover {
  transform: translateY(-2px);
}

.tag-card.selected {
  border-color: var(--el-color-primary);
}

.tag-color-bar {
  height: 4px;
  width: 100%;
}

.tag-info {
  padding: 16px;
}

.tag-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.tag-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
  flex: 1;
  margin-right: 8px;
}

.tag-type {
  flex-shrink: 0;
}

.project-info {
  margin-top: 8px;
  margin-bottom: 12px;
}

.tag-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.created-date {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.tag-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  opacity: 0;
  transition: opacity 0.3s;
  display: flex;
  gap: 4px;
}

.tag-card:hover .tag-actions {
  opacity: 1;
}

.color-cell {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid var(--el-border-color);
}

.global-indicator {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.unknown-project {
  color: var(--el-color-danger);
  font-size: 12px;
}

.tag-details-content {
  padding: 0 16px;
}

.color-display {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  border: 1px solid var(--el-border-color);
}

.related-images {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.related-image {
  aspect-ratio: 1;
  border-radius: 4px;
  overflow: hidden;
}

.color-picker {
  display: flex;
  align-items: center;
  gap: 16px;
}

.preset-colors {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preset-color {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}

.preset-color.active {
  border-color: var(--el-color-primary);
}

.preset-color:hover {
  border-color: var(--el-border-color-darker);
}

.form-help-text {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.copy-dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.tag-selection {
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 12px;
}

.selection-header {
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  margin-bottom: 12px;
}

.tag-list {
  max-height: 300px;
  overflow-y: auto;
}

.tag-checkbox-item {
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-extra-light);
}

.tag-checkbox-item:last-child {
  border-bottom: none;
}

.tag-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tag-color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid var(--el-border-color);
}

.tag-name {
  font-weight: 500;
  margin-right: 8px;
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

@media (max-width: 768px) {
  .tag-management {
    padding: 16px;
  }
  
  .tag-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-card .el-row {
    flex-direction: column;
    gap: 12px;
  }
  
  .filter-card .el-col {
    width: 100%;
  }
  
  .batch-actions {
    text-align: center;
    margin-top: 12px;
  }
}
</style>