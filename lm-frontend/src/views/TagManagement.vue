<template>
  <div class="tag-management">
    <el-page-header @back="$router.go(-1)" content="标签管理">
      <template #extra>
        <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
          创建标签
        </el-button>
      </template>
    </el-page-header>

    <el-card class="filter-card" shadow="never">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-select v-model="selectedProject" @change="loadTags" placeholder="选择项目" clearable>
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
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-col>
        
        <el-col :span="8">
          <el-input
            v-model="searchQuery"
            @input="filterTags"
            placeholder="搜索标签名称..."
            :prefix-icon="Search"
            clearable
          />
        </el-col>
        
        <el-col :span="4">
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
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" class="statistics-row">
      <el-col :span="6">
        <el-statistic title="总标签数" :value="filteredTags.length" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="已使用" :value="usedTagsCount" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="未使用" :value="unusedTagsCount" />
      </el-col>
      <el-col :span="6">
        <el-statistic title="使用率" :value="usageRate" suffix="%" />
      </el-col>
    </el-row>

    <el-card class="content-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>标签列表</span>
          <div class="sort-controls">
            <el-select v-model="sortBy" @change="sortTags" style="width: 120px;">
              <el-option label="名称" value="name" />
              <el-option label="使用次数" value="usageCount" />
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
            <h3>{{ tag.name }}</h3>
            <el-tag size="small" type="info">{{ getCategoryName(tag.categoryId) }}</el-tag>
            <div class="tag-stats">
              <el-statistic 
                title="使用次数" 
                :value="tag.usageCount" 
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
          <el-table-column label="分类">
            <template #default="{ row }">
              <el-tag size="small" type="info">{{ getCategoryName(row.categoryId) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column property="usageCount" label="使用次数" />
          <el-table-column label="创建时间">
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
          <el-descriptions-item label="分类">
            {{ getCategoryName(selectedTag.categoryId) }}
          </el-descriptions-item>
          <el-descriptions-item label="描述">
            {{ selectedTag.description || '无描述' }}
          </el-descriptions-item>
          <el-descriptions-item label="使用次数">
            {{ selectedTag.usageCount }}
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
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        
        <el-form-item label="分类" prop="categoryId">
          <el-select v-model="tagForm.categoryId" placeholder="选择分类" style="width: 100%">
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
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
        
        <el-form-item label="描述">
          <el-input 
            v-model="tagForm.description" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="closeDialogs">取消</el-button>
        <el-button type="primary" @click="saveTag">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, Search, Grid, List, Edit, Delete, 
  SortUp, SortDown 
} from '@element-plus/icons-vue'

export default {
  name: 'TagManagement',
  setup() {
    const tags = ref([])
    const filteredTags = ref([])
    const selectedTag = ref(null)
    const selectedProject = ref('')
    const selectedCategory = ref('')
    const searchQuery = ref('')
    const sortBy = ref('name')
    const sortOrder = ref('asc')
    const viewMode = ref('grid')
    const showCreateDialog = ref(false)
    const showEditDialog = ref(false)
    const showTagDetails = ref(false)
    const projects = ref([])
    const categories = ref([])
    const tagImages = ref([])
    const tagFormRef = ref()

    const tagForm = reactive({
      id: null,
      name: '',
      categoryId: '',
      color: '#409EFF',
      description: ''
    })

    const tagFormRules = {
      name: [
        { required: true, message: '请输入标签名称', trigger: 'blur' }
      ],
      categoryId: [
        { required: true, message: '请选择分类', trigger: 'change' }
      ]
    }

    const showDialog = computed(() => showCreateDialog.value || showEditDialog.value)

    const presetColors = [
      '#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57',
      '#ff9ff3', '#54a0ff', '#5f27cd', '#00d2d3', '#ff9f43',
      '#a55eea', '#26de81', '#fd79a8', '#fdcb6e', '#6c5ce7'
    ]

    const usedTagsCount = computed(() => {
      return filteredTags.value.filter(tag => tag.usageCount > 0).length
    })

    const unusedTagsCount = computed(() => {
      return filteredTags.value.filter(tag => tag.usageCount === 0).length
    })

    const usageRate = computed(() => {
      if (filteredTags.value.length === 0) return 0
      return Math.round((usedTagsCount.value / filteredTags.value.length) * 100)
    })

    const sortedTags = computed(() => {
      const sorted = [...filteredTags.value].sort((a, b) => {
        let aVal = a[sortBy.value]
        let bVal = b[sortBy.value]
        
        if (sortBy.value === 'createdAt') {
          aVal = new Date(aVal)
          bVal = new Date(bVal)
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
      projects.value = [
        { id: 1, name: '项目A' },
        { id: 2, name: '项目B' },
        { id: 3, name: '项目C' }
      ]
    }

    const loadCategories = async () => {
      categories.value = [
        { id: 1, name: '人物分类' },
        { id: 2, name: '动物分类' },
        { id: 3, name: '建筑分类' },
        { id: 4, name: '风景分类' },
        { id: 5, name: '车辆分类' }
      ]
    }

    const loadTags = async () => {
      // 模拟标签数据
      tags.value = [
        {
          id: 1,
          name: '成人',
          categoryId: 1,
          color: '#ff6b6b',
          description: '成年人物标签',
          usageCount: 15,
          createdAt: new Date('2024-01-15'),
          projectId: 1
        },
        {
          id: 2,
          name: '儿童',
          categoryId: 1,
          color: '#ff8e8e',
          description: '儿童人物标签',
          usageCount: 8,
          createdAt: new Date('2024-01-16'),
          projectId: 1
        },
        {
          id: 3,
          name: '猫',
          categoryId: 2,
          color: '#4ecdc4',
          description: '猫科动物',
          usageCount: 12,
          createdAt: new Date('2024-01-17'),
          projectId: 2
        },
        {
          id: 4,
          name: '狗',
          categoryId: 2,
          color: '#6ed5cd',
          description: '犬科动物',
          usageCount: 9,
          createdAt: new Date('2024-01-18'),
          projectId: 2
        },
        {
          id: 5,
          name: '现代建筑',
          categoryId: 3,
          color: '#45b7d1',
          description: '现代风格建筑',
          usageCount: 0,
          createdAt: new Date('2024-01-19'),
          projectId: 3
        }
      ]
      filterTags()
    }

    const filterTags = () => {
      let filtered = [...tags.value]
      
      if (selectedProject.value) {
        filtered = filtered.filter(tag => tag.projectId === parseInt(selectedProject.value))
      }
      
      if (selectedCategory.value) {
        filtered = filtered.filter(tag => tag.categoryId === parseInt(selectedCategory.value))
      }
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(tag => 
          tag.name.toLowerCase().includes(query) ||
          (tag.description && tag.description.toLowerCase().includes(query))
        )
      }
      
      filteredTags.value = filtered
    }

    const sortTags = () => {
      // sortedTags computed 会自动处理排序
    }

    const toggleSortOrder = () => {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    }

    const selectTag = (tag) => {
      selectedTag.value = tag
      showTagDetails.value = true
      loadTagImages(tag.id)
    }

    const loadTagImages = async (tagId) => {
      // 模拟关联图片
      tagImages.value = [
        {
          id: 1,
          name: 'sample1.jpg',
          thumbnail: '/api/images/thumbnails/sample1.jpg'
        },
        {
          id: 2,
          name: 'sample2.jpg',
          thumbnail: '/api/images/thumbnails/sample2.jpg'
        }
      ]
    }

    const getCategoryName = (categoryId) => {
      const category = categories.value.find(c => c.id === categoryId)
      return category ? category.name : '未分类'
    }

    const editTag = (tag) => {
      tagForm.id = tag.id
      tagForm.name = tag.name
      tagForm.categoryId = tag.categoryId
      tagForm.color = tag.color
      tagForm.description = tag.description
      showEditDialog.value = true
    }

    const deleteTag = async (tag) => {
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
        
        console.log('删除标签:', tag)
        ElMessage.success('标签删除成功')
        await loadTags()
      } catch {
        ElMessage.info('已取消删除')
      }
    }

    const resetTagForm = () => {
      tagForm.id = null
      tagForm.name = ''
      tagForm.categoryId = ''
      tagForm.color = '#409EFF'
      tagForm.description = ''
    }

    const closeDialogs = () => {
      showCreateDialog.value = false
      showEditDialog.value = false
      resetTagForm()
    }

    const saveTag = async () => {
      try {
        await tagFormRef.value.validate()
        
        if (showEditDialog.value) {
          console.log('更新标签:', tagForm)
          ElMessage.success('标签更新成功')
        } else {
          console.log('创建标签:', tagForm)
          ElMessage.success('标签创建成功')
        }
        
        await loadTags()
        closeDialogs()
      } catch (error) {
        if (error !== false) { // 排除表单验证失败的情况
          ElMessage.error('保存失败')
        }
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      loadProjects()
      loadCategories()
      loadTags()
    })

    return {
      tags,
      filteredTags,
      selectedTag,
      selectedProject,
      selectedCategory,
      searchQuery,
      sortBy,
      sortOrder,
      viewMode,
      showCreateDialog,
      showEditDialog,
      showTagDetails,
      showDialog,
      projects,
      categories,
      tagImages,
      tagForm,
      tagFormRef,
      tagFormRules,
      presetColors,
      usedTagsCount,
      unusedTagsCount,
      usageRate,
      sortedTags,
      filterTags,
      sortTags,
      toggleSortOrder,
      selectTag,
      getCategoryName,
      editTag,
      deleteTag,
      closeDialogs,
      saveTag,
      formatDate,
      loadTags,
      // Element Plus 图标
      Plus,
      Search,
      Grid,
      List,
      Edit,
      Delete,
      SortUp,
      SortDown
    }
  }
}
</script>

<style scoped>
.tag-management {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 20px;
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
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
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

.tag-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
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
</style>
