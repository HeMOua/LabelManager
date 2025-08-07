<template>
  <div class="image-gallery">
    <div class="gallery-header">
      <el-page-header @back="$router.go(-1)" content="图片画廊">
        <template #extra>
          <div class="gallery-controls">
            <el-upload
              ref="uploadRef"
              :show-file-list="false"
              :auto-upload="false"
              :on-change="handleFileUpload"
              accept="image/*"
              multiple
              action="#"
              :disabled="batchMode"
            >
              <el-button type="primary" :icon="Upload" :disabled="batchMode">
                选择图片
              </el-button>
            </el-upload>
            <el-button 
              @click="uploadImages" 
              type="success" 
              :icon="UploadFilled"
              :loading="uploading"
              :disabled="!selectedFiles.length || !selectedProject || batchMode"
            >
              上传图片 ({{ selectedFiles.length }})
            </el-button>
            <el-select 
              v-model="selectedProject" 
              placeholder="选择项目"
              style="width: 200px"
              clearable
              @change="onProjectChange"
              :disabled="batchMode"
            >
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
            
            <!-- 视图模式切换 -->
            <el-button-group class="view-toggle">
              <el-button 
                :type="viewMode === 'grid' ? 'primary' : ''"
                :icon="Grid"
                @click="switchViewMode('grid')"
                title="网格视图"
              />
              <el-button 
                :type="viewMode === 'list' ? 'primary' : ''"
                :icon="List"
                @click="switchViewMode('list')"
                title="列表视图"
              />
            </el-button-group>
            
            <!-- 批量选择开关 -->
            <el-switch
              v-model="batchMode"
              inactive-text="批量选择"
              :disabled="!filteredImages.length"
              @change="onBatchModeChange"
            />
          </div>
        </template>
      </el-page-header>
      
      <!-- 待上传图片预览容器 -->
      <div v-if="selectedFiles.length > 0" class="upload-preview-panel">
        <div class="upload-preview-header">
          <h4>待上传图片 ({{ selectedFiles.length }})</h4>
          <el-button 
            size="small" 
            type="danger" 
            text
            @click="clearAllFiles"
            :icon="Delete"
          >
            清空
          </el-button>
        </div>
        
        <div class="upload-preview-container">
          <div 
            v-for="(file, index) in selectedFiles" 
            :key="`${file.name}-${file.size}-${index}`"
            class="upload-preview-item"
          >
            <div class="preview-image-wrapper">
              <img 
                :src="getFilePreviewUrl(file)" 
                :alt="file.name"
                class="preview-image"
                @error="handlePreviewError($event, file)"
                @load="handlePreviewLoad($event, file)"
              />
              <div class="preview-loading" v-if="!filePreviewStates[getFileKey(file)]?.loaded">
                <el-icon class="loading-icon"><Loading /></el-icon>
              </div>
              <div class="preview-overlay">
                <div class="preview-actions">
                  <el-button 
                    size="small" 
                    circle 
                    type="danger"
                    :icon="Delete"
                    @click="removeFileFromSelection(index)"
                    title="移除"
                  />
                </div>
              </div>
            </div>
            
            <div class="preview-info">
              <div class="file-name" :title="file.name">
                {{ truncateText(file.name, 15) }}
              </div>
              <div class="file-size">
                {{ formatFileSize(file.size) }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 批量操作面板 -->
      <div v-if="batchMode" class="batch-panel">
        <div class="batch-info">
          <el-checkbox 
            v-model="selectAll"
            :indeterminate="isIndeterminate"
            @change="handleSelectAll"
          >
            全选 ({{ selectedImages.length }}/{{ filteredImages.length }})
          </el-checkbox>
        </div>
        <div class="batch-actions" v-if="selectedImages.length > 0">
          <el-button 
            type="primary"
            :icon="Plus"
            @click="showBatchTagDialog = true"
          >
            批量添加标签
          </el-button>
          <el-button 
            type="danger"
            :icon="Delete"
            @click="batchDeleteImages"
          >
            批量删除 ({{ selectedImages.length }})
          </el-button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="8" animated />
    </div>

    <!-- 网格视图 -->
    <div class="gallery-grid" v-else-if="filteredImages.length > 0 && viewMode === 'grid'">
      <el-card 
        v-for="image in filteredImages" 
        :key="image.id" 
        class="image-card"
        :class="{ 
          selected: selectedImage?.id === image.id,
          'batch-selected': selectedImages.includes(image.id) 
        }"
        shadow="hover"
      >
        <!-- 批量选择复选框 -->
        <div v-if="batchMode" class="batch-checkbox">
          <el-checkbox 
            :model-value="selectedImages.includes(image.id)"
            @change="toggleImageSelection(image.id)"
          />
        </div>
        
        <div class="image-container">
          <el-image
            :src="getImageThumbnail(image)"
            :alt="image.filename || '图片'"
            fit="cover"
            class="image-preview"
            lazy
            loading="lazy"
            @click="handleImageClick(image)"
            @error="handleImageError(image)"
            :ref="(el) => setImageRef(el, getImageCacheKey(image))"
          >
            <template #placeholder>
              <div class="image-placeholder">
                <el-icon class="loading-icon"><Loading /></el-icon>
                <span>加载中...</span>
              </div>
            </template>
            <template #error>
              <div class="image-error">
                <el-icon><Picture /></el-icon>
                <span>{{ getImageErrorText(image) }}</span>
                <el-button size="small" @click.stop="retryLoadImage(image)">重试</el-button>
              </div>
            </template>
          </el-image>
          
          <!-- 图片操作按钮 -->
          <div v-if="!batchMode" class="image-actions">
            <el-button-group>
              <el-button 
                size="small" 
                :icon="View" 
                @click.stop="openImagePreview(image)"
                title="预览"
              />
              <el-button 
                size="small" 
                :icon="Edit" 
                @click.stop="editImageTags(image)"
                title="编辑标签"
              />
              <el-button 
                size="small" 
                :icon="Delete" 
                type="danger"
                @click.stop="deleteImage(image)"
                title="删除"
              />
            </el-button-group>
          </div>
        </div>
        
        <div class="image-info" @click="handleImageInfoClick(image)">
          <h3 :title="image.filename || '图片'">
            {{ truncateText(image.filename || '图片', 20) }}
          </h3>
          <div class="image-meta">
            <span class="upload-time">{{ formatDate(image.createdAt) }}</span>
          </div>
          <div class="image-tags">
            <el-tag 
              v-for="tag in image.tags?.slice(0, 3)" 
              :key="tag.id" 
              :color="tag.color"
              size="small"
              class="image-tag"
            >
              {{ tag.name }}
            </el-tag>
            <el-tag 
              v-if="image.tags && image.tags.length > 3"
              size="small"
              type="info"
              class="image-tag"
            >
              +{{ image.tags.length - 3 }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 列表视图 -->
    <div v-else-if="filteredImages.length > 0 && viewMode === 'list'" class="gallery-list">
      <el-table 
        :data="filteredImages" 
        stripe
        :height="batchMode ? 'calc(100vh - 400px)' : 'calc(100vh - 320px)'"
        @row-click="handleRowClick"
        :row-class-name="getRowClassName"
      >
        <el-table-column v-if="batchMode" width="55">
          <template #header>
            <el-checkbox 
              v-model="selectAll"
              :indeterminate="isIndeterminate"
              @change="handleSelectAll"
            />
          </template>
          <template #default="{ row }">
            <el-checkbox 
              :model-value="selectedImages.includes(row.id)"
              @change="toggleImageSelection(row.id)"
              @click.stop
            />
          </template>
        </el-table-column>
        
        <el-table-column label="预览" width="80">
          <template #default="{ row }">
            <el-image
              :src="getImageThumbnail(row)"
              :alt="row.filename || '图片'"
              fit="cover"
              lazy
              loading="lazy"
              class="table-image-preview"
              @click.stop="openImagePreview(row)"
              @error="handleImageError(row)"
             :ref="(el) => setImageRef(el, getImageCacheKey(row))"
            >
              <template #error>
                <div class="table-image-error">
                  <el-icon><Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>
        
        <el-table-column label="文件名" prop="filename" min-width="200">
          <template #default="{ row }">
            <span :title="row.filename">{{ row.filename || '图片' }}</span>
          </template>
        </el-table-column>
        
        <el-table-column label="上传时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        
        <el-table-column label="标签" min-width="200">
          <template #default="{ row }">
            <div class="table-tags">
              <el-tag 
                v-for="tag in (row.tags || []).slice(0, 3)" 
                :key="tag.id" 
                :color="tag.color"
                size="small"
                style="margin-right: 4px; margin-bottom: 2px;"
              >
                {{ tag.name }}
              </el-tag>
              <el-tag 
                v-if="row.tags && row.tags.length > 3"
                size="small"
                type="info"
              >
                +{{ row.tags.length - 3 }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column v-if="!batchMode" label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button-group size="small">
              <el-button 
                :icon="View" 
                @click.stop="openImagePreview(row)"
                title="预览"
              />
              <el-button 
                :icon="Edit" 
                @click.stop="editImageTags(row)"
                title="编辑标签"
              />
              <el-button 
                :icon="Delete" 
                type="danger"
                @click.stop="deleteImage(row)"
                title="删除"
              />
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 空状态 -->
    <el-empty v-else>
      <template #description>
        <span v-if="!selectedProject">请先选择一个项目</span>
        <span v-else>该项目暂无图片，请上传图片开始标注</span>
      </template>
      <el-button 
        v-if="selectedProject" 
        type="primary" 
        @click="uploadImages"
      >
        立即上传
      </el-button>
    </el-empty>

    <!-- 分页 -->
    <div class="pagination-container" v-show="!loading && selectedProject">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="showImagePreview"
      :title="previewImageData?.filename || '图片预览'"
      width="80%"
      :before-close="closeImagePreview"
      class="image-preview-dialog"
    >
      <div class="preview-container" v-if="previewImageData">
        <el-image
          :src="getImageFullUrl(previewImageData)"
          :alt="previewImageData.filename || '图片'"
          fit="contain"
          style="width: 100%; max-height: 85vh;"
        >
          <template #error>
            <div class="preview-error">
              <el-icon><Picture /></el-icon>
              <span>图片加载失败</span>
            </div>
          </template>
        </el-image>
      </div>
    </el-dialog>

    <!-- 图片标签编辑对话框 -->
    <el-dialog
      v-model="showTagDialog"
      title="编辑图片标签"
      width="600px"
      :before-close="closeTagDialog"
    >
      <div class="tag-dialog-content" v-if="selectedImage">
        <div class="image-preview-small">
          <el-image 
            :src="getImageThumbnail(selectedImage)"
            :alt="selectedImage.filename || '图片'"
            fit="cover"
            style="width: 100px; height: 100px; border-radius: 8px;"
          />
          <div class="image-name">
            <h4>{{ selectedImage.filename || '图片' }}</h4>
          </div>
        </div>
        
        <el-divider />
        
        <div class="tag-editor">
          <div class="current-tags">
            <h5>当前标签：</h5>
            <div class="existing-tags">
              <el-tag 
                v-for="tag in currentImageTags" 
                :key="tag.id" 
                :color="tag.color"
                closable
                @close="removeTagFromCurrent(tag.id)"
                class="tag-item"
              >
                {{ tag.name }}
              </el-tag>
              <span v-if="!currentImageTags.length" class="no-tags">暂无标签</span>
            </div>
          </div>
          
          <div class="add-tag-section">
            <h5>添加标签：</h5>
            <div class="add-tag">
              <el-select 
                v-model="newTagId" 
                placeholder="选择要添加的标签"
                style="width: 100%;"
                clearable
                filterable
              >
                <el-option-group
                  v-for="category in tagsByCategory"
                  :key="category.name"
                  :label="category.name"
                >
                  <el-option
                    v-for="tag in category.tags"
                    :key="tag.id"
                    :label="tag.name"
                    :value="tag.id"
                    :disabled="currentImageTags.some(t => t.id === tag.id)"
                  >
                    <div style="display: flex; align-items: center; gap: 8px;">
                      <div 
                        style="width: 12px; height: 12px; border-radius: 50%;"
                        :style="{ backgroundColor: tag.color }"
                      ></div>
                      <span>{{ tag.name }}</span>
                    </div>
                  </el-option>
                </el-option-group>
              </el-select>
              <el-button 
                @click="addTagToCurrent" 
                type="primary" 
                :icon="Plus"
                style="margin-top: 10px; width: 100%;"
                :disabled="!newTagId"
              >
                添加标签
              </el-button>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeTagDialog">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveImageTags"
            :loading="savingTags"
          >
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 批量添加标签对话框 -->
    <el-dialog
      v-model="showBatchTagDialog"
      title="批量添加标签"
      width="500px"
    >
      <div class="batch-tag-content">
        <p>为 {{ selectedImages.length }} 张图片添加标签：</p>
        <el-select 
          v-model="batchTagIds" 
          placeholder="选择要添加的标签"
          style="width: 100%;"
          multiple
          filterable
        >
          <el-option-group
            v-for="category in tagsByCategory"
            :key="category.name"
            :label="category.name"
          >
            <el-option
              v-for="tag in category.tags"
              :key="tag.id"
              :label="tag.name"
              :value="tag.id"
            >
              <div style="display: flex; align-items: center; gap: 8px;">
                <div 
                  style="width: 12px; height: 12px; border-radius: 50%;"
                  :style="{ backgroundColor: tag.color }"
                ></div>
                <span>{{ tag.name }}</span>
              </div>
            </el-option>
          </el-option-group>
        </el-select>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showBatchTagDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveBatchTags"
            :loading="savingBatchTags"
            :disabled="!batchTagIds.length"
          >
            批量添加
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Upload, UploadFilled, Plus, View, Edit, Delete, Picture, Loading, Grid, List } from '@element-plus/icons-vue'
import { useImageLazyLoad } from '@/hooks/useImageLazyLoad'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Image, Tag, Project } from '@/types/index'
import { projectApi } from '@/api/project'
import { useRoute } from 'vue-router'
import { tagApi } from '@/api/tags'
import { imageApi } from '@/api/image'
import { fileApi } from '@/api/file'

const {
  setImageRef,
  isImageVisible,
  clearVisible
} = useImageLazyLoad({
  rootMargin: '50px',
  threshold: 0.1
})

const route = useRoute()

// 响应式数据
const images = ref<Image[]>([])
const selectedImage = ref<Image | null>(null)
const previewImageData = ref<Image | null>(null)
const currentImageTags = ref<Tag[]>([])
const selectedProject = ref<number | null>(null)
const newTagId = ref<number | null>(null)
const projects = ref<Project[]>([])
const availableTags = ref<Tag[]>([])
const selectedFiles = ref<File[]>([])

// 文件预览相关
const filePreviewUrls = ref<Record<string, string>>({})
const filePreviewStates = ref<Record<string, { loaded: boolean; error: boolean }>>({})

// 批量选择相关
const batchMode = ref(false)
const selectedImages = ref<number[]>([])
const batchTagIds = ref<number[]>([])
const showBatchTagDialog = ref(false)
const savingBatchTags = ref(false)

// 视图模式
const viewMode = ref<'grid' | 'list'>('grid')

// 图片URL缓存
const imageUrls = ref<Record<string, { 
  thumbnailUrl?: string; 
  fullUrl?: string; 
  thumbnailLoading?: boolean; 
  fullLoading?: boolean;
  thumbnailError?: boolean;
  fullError?: boolean;
}>>({})

// 防抖定时器
const fileSelectTimer = ref<number | null>(null)

// 对话框状态
const showTagDialog = ref(false)
const showImagePreview = ref(false)

// 加载状态
const loading = ref(false)
const uploading = ref(false)
const savingTags = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

// 引用
const uploadRef = ref()

// 计算属性
const filteredImages = computed(() => {
  if (!selectedProject.value) return []
  return images.value
})

const tagsByCategory = computed(() => {
  const categories = new Map<string, Tag[]>()
  
  availableTags.value.forEach(tag => {
    const category = tag.category || '未分类'
    if (!categories.has(category)) {
      categories.set(category, [])
    }
    categories.get(category)!.push(tag)
  })
  
  return Array.from(categories.entries()).map(([name, tags]) => ({
    name,
    tags
  }))
})

// 批量选择相关计算属性
const selectAll = computed({
  get: () => {
    return selectedImages.value.length === filteredImages.value.length && filteredImages.value.length > 0
  },
  set: (val: boolean) => {
    if (val) {
      selectedImages.value = filteredImages.value.map(img => img.id)
    } else {
      selectedImages.value = []
    }
  }
})

const isIndeterminate = computed(() => {
  return selectedImages.value.length > 0 && selectedImages.value.length < filteredImages.value.length
})

// 工具函数
const truncateText = (text: string | undefined, maxLength: number) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 文件大小格式化
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// 文件预览相关方法
const getFileKey = (file: File): string => {
  return `${file.name}-${file.size}-${file.lastModified}`
}

const getFilePreviewUrl = (file: File): string => {
  const key = getFileKey(file)
  if (!filePreviewUrls.value[key]) {
    filePreviewUrls.value[key] = URL.createObjectURL(file)
    filePreviewStates.value[key] = { loaded: false, error: false }
  }
  return filePreviewUrls.value[key]
}

const handlePreviewLoad = (event: Event, file: File) => {
  const key = getFileKey(file)
  if (filePreviewStates.value[key]) {
    filePreviewStates.value[key].loaded = true
    filePreviewStates.value[key].error = false
  }
}

const handlePreviewError = (event: Event, file: File) => {
  const key = getFileKey(file)
  if (filePreviewStates.value[key]) {
    filePreviewStates.value[key].loaded = true
    filePreviewStates.value[key].error = true
  }
}

const removeFileFromSelection = (index: number) => {
  const removedFile = selectedFiles.value[index]
  const key = getFileKey(removedFile)
  
  // 清理预览URL
  if (filePreviewUrls.value[key]) {
    URL.revokeObjectURL(filePreviewUrls.value[key])
    delete filePreviewUrls.value[key]
    delete filePreviewStates.value[key]
  }
  
  // 从选择列表中移除
  selectedFiles.value.splice(index, 1)
  
  uploadRef.value?.clearFiles()
  
  ElMessage.success('已移除文件')
}

const clearAllFiles = () => {
  // 清理所有预览URL
  Object.values(filePreviewUrls.value).forEach(url => {
    URL.revokeObjectURL(url)
  })
  
  filePreviewUrls.value = {}
  filePreviewStates.value = {}
  selectedFiles.value = []
  
  // 清理上传组件
  uploadRef.value?.clearFiles()
}

// 视图模式持久化
const saveViewMode = (mode: 'grid' | 'list') => {
  localStorage.setItem('image-gallery-view-mode', mode)
}

const loadViewMode = () => {
  const saved = localStorage.getItem('image-gallery-view-mode') as 'grid' | 'list'
  if (saved && ['grid', 'list'].includes(saved)) {
    viewMode.value = saved
  }
}

// 视图模式切换
const switchViewMode = (mode: 'grid' | 'list') => {
  viewMode.value = mode
  saveViewMode(mode)
  
  // 退出批量模式
  if (batchMode.value) {
    batchMode.value = false
    selectedImages.value = []
  }
}

// 批量选择相关方法
const onBatchModeChange = (enabled: boolean) => {
  if (!enabled) {
    selectedImages.value = []
  }
}

const handleSelectAll = (checked: boolean) => {
  if (checked) {
    selectedImages.value = filteredImages.value.map(img => img.id)
  } else {
    selectedImages.value = []
  }
}

const toggleImageSelection = (imageId: number) => {
  const index = selectedImages.value.indexOf(imageId)
  if (index > -1) {
    selectedImages.value.splice(index, 1)
  } else {
    selectedImages.value.push(imageId)
  }
}

// 批量操作方法
const batchDeleteImages = async () => {
  if (selectedImages.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedImages.value.length} 张图片吗？`,
      '批量删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    let successCount = 0
    const totalCount = selectedImages.value.length
    
    // 显示进度
    ElMessage.info(`正在删除 ${totalCount} 张图片...`)
    
    for (const imageId of selectedImages.value) {
      try {
        const response = await imageApi.deleteImage(imageId) as unknown as { code: number }
        if (response?.code === 200) {
          successCount++
          // 从缓存中移除
          const image = images.value.find(img => img.id === imageId)
          if (image) {
            const cacheKey = getImageCacheKey(image)
            delete imageUrls.value[cacheKey]
          }
        }
      } catch (error) {
        console.error(`Delete image ${imageId} error:`, error)
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`成功删除 ${successCount}/${totalCount} 张图片`)
      selectedImages.value = []
      await loadImages()
    } else {
      ElMessage.error('删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('批量删除操作失败')
      console.error('Batch delete error:', error)
    }
  }
}

const saveBatchTags = async () => {
  if (selectedImages.value.length === 0 || batchTagIds.value.length === 0) return
  
  savingBatchTags.value = true
  let successCount = 0
  const totalCount = selectedImages.value.length
  
  try {
    ElMessage.info(`正在为 ${totalCount} 张图片添加标签...`)
    
    for (const imageId of selectedImages.value) {
      try {
        // 获取当前图片的标签
        const currentImage = images.value.find(img => img.id === imageId)
        const currentTagIds = currentImage?.tags?.map(tag => tag.id) || []
        
        // 合并现有标签和新标签，去重
        const allTagIds = [...new Set([...currentTagIds, ...batchTagIds.value])]
        
        const response = await imageApi.updateImageTags(imageId, allTagIds) as unknown as { code: number }
        if (response?.code === 200) {
          successCount++
          
          // 更新本地数据
          const imageIndex = images.value.findIndex(img => img.id === imageId)
          if (imageIndex !== -1) {
            const newTags = availableTags.value.filter(tag => allTagIds.includes(tag.id))
            images.value[imageIndex].tags = newTags
          }
        }
      } catch (error) {
        console.error(`Update tags for image ${imageId} error:`, error)
      }
    }
    
    if (successCount > 0) {
      ElMessage.success(`成功为 ${successCount}/${totalCount} 张图片添加标签`)
      showBatchTagDialog.value = false
      batchTagIds.value = []
    } else {
      ElMessage.error('标签添加失败')
    }
  } catch (error) {
    ElMessage.error('批量添加标签操作失败')
    console.error('Batch add tags error:', error)
  } finally {
    savingBatchTags.value = false
  }
}

// 表格行点击处理
const handleRowClick = (row: Image) => {
  if (batchMode.value) {
    toggleImageSelection(row.id)
  } else {
    previewImage(row)
  }
}

const getRowClassName = ({ row }: { row: Image }) => {
  return selectedImages.value.includes(row.id) ? 'selected-row' : ''
}

// 图片点击处理
const handleImageClick = (image: Image) => {
  if (batchMode.value) {
    toggleImageSelection(image.id)
  } else {
    previewImage(image)
  }
}

const handleImageInfoClick = (image: Image) => {
  if (batchMode.value) {
    toggleImageSelection(image.id)
  } else {
    editImageTags(image)
  }
}

// 获取图片缓存键
const getImageCacheKey = (image: Image): string => {
  return `img_${image.id}`
}

// 初始化图片缓存条目
const initImageCache = (image: Image) => {
  const cacheKey = getImageCacheKey(image)
  if (!imageUrls.value[cacheKey]) {
    imageUrls.value[cacheKey] = {}
  }
  return cacheKey
}

// 获取图片缩略图URL
const getImageThumbnail = (image: Image): string => {
  if (!image || Object.keys(image).length === 0) return ''

  const cacheKey = initImageCache(image)
  const cache = imageUrls.value[cacheKey]
  
  if (cache.thumbnailUrl && !cache.thumbnailError) {
    return cache.thumbnailUrl
  }

  if (image.url) {
    cache.thumbnailUrl = image.url
    return image.url
  }

  // 添加更严格的检查，避免重复调用
  if (cache.thumbnailLoading || cache.thumbnailUrl) {
    return cache.thumbnailUrl || ''
  }

  if (!isImageVisible(cacheKey)) {
    return ''
  }
  
  loadImageThumbnail(image, cacheKey)
  return ''
}

// 获取完整图片URL
const getImageFullUrl = (image: Image): string => {
  const cacheKey = initImageCache(image)
  const cache = imageUrls.value[cacheKey]
  
  if (cache.fullUrl && !cache.fullError) {
    return cache.fullUrl
  }
  
  if (image.url) {
    cache.fullUrl = image.url
    return image.url
  }
  
  if (cache.fullLoading) {
    return cache.thumbnailUrl || ''
  }
  
  loadImageFullUrl(image, cacheKey)
  return cache.thumbnailUrl || ''
}

// 异步加载缩略图
const loadImageThumbnail = async (image: Image, cacheKey: string) => {
  if (!image) return ''

  const cache = imageUrls.value[cacheKey]
  if (cache.thumbnailLoading) return
  
  cache.thumbnailLoading = true
  cache.thumbnailError = false
  
  try {
    const path = image.thumbnailPath || image.filePath
    if (!path) {
      throw new Error('No image path available')
    }
    
    const response = await fileApi.serveFile(path)
    if (response?.data?.url) {
      cache.thumbnailUrl = response.data.url
    } else {
      throw new Error('No URL in response')
    }
  } catch {
    cache.thumbnailError = true
  } finally {
    cache.thumbnailLoading = false
  }
}

// 异步加载完整图片
const loadImageFullUrl = async (image: Image, cacheKey: string) => {
  const cache = imageUrls.value[cacheKey]
  if (cache.fullLoading) return
  
  cache.fullLoading = true
  cache.fullError = false
  
  try {
    const path = image.filePath
    if (!path) {
      throw new Error('No image file path available')
    }
    
    const response = await fileApi.serveFile(path)
    if (response?.data?.url) {
      cache.fullUrl = response.data.url
    } else {
      throw new Error('No URL in response')
    }
  } catch (error) {
    console.error(`Failed to load full image for ${image.id}:`, error)
    cache.fullError = true
  } finally {
    cache.fullLoading = false
  }
}

// 处理图片错误
const handleImageError = (image: Image) => {
  const cacheKey = getImageCacheKey(image)
  const cache = imageUrls.value[cacheKey]
  if (cache) {
    cache.thumbnailError = true
  }
}

// 获取图片错误文本
const getImageErrorText = (image: Image) => {
  const cacheKey = getImageCacheKey(image)
  const cache = imageUrls.value[cacheKey]
  if (cache?.thumbnailLoading) {
    return '加载中...'
  }
  return '加载失败'
}

// 重试加载图片
const retryLoadImage = (image: Image) => {
  const cacheKey = getImageCacheKey(image)
  const cache = imageUrls.value[cacheKey]
  if (cache) {
    cache.thumbnailError = false
    cache.thumbnailUrl = undefined
    cache.thumbnailLoading = false
    nextTick(() => {
      getImageThumbnail(image)
    })
  }
}

// API调用函数
const loadProjects = async () => {
  try {
    const response = await projectApi.getProjects()
    if (response?.data) {
      projects.value = response.data
      
      if (route.query.project) {
        selectedProject.value = parseInt(route.query.project as string)
      } else if (projects.value.length > 0) {
        selectedProject.value = projects.value[0].id
      }
    }
  } catch (error) {
    ElMessage.error('加载项目列表失败')
    console.error('Load projects error:', error)
  }
}

const loadTags = async () => {
  try {
    const response = await tagApi.getTags()
    if (response?.data) {
      availableTags.value = response.data
    }
  } catch (error) {
    ElMessage.error('加载标签列表失败')
    console.error('Load tags error:', error)
  }
}

const loadImages = async () => {
  if (!selectedProject.value) return
  
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    const response = await imageApi.getProjectImages(selectedProject.value, params) as { data: Image[], total?: number }
    if (response?.data) {
      images.value = response.data.map((img: Image) => ({
        ...img,
        tags: img.tags || []
      }))
      
      await nextTick()
      images.value.forEach(image => {
        getImageThumbnail(image)
      })
      
      if (response.total !== undefined) {
        total.value = response.total
      } else if (Array.isArray(response.data)) {
        total.value = response.data.length
      }
      
      // 清理已删除图片的选择状态
      selectedImages.value = selectedImages.value.filter(id => 
        images.value.some(img => img.id === id)
      )
    }
  } catch (error) {
    ElMessage.error('加载图片列表失败')
    console.error('Load images error:', error)
  } finally {
    loading.value = false
  }
}

// 事件处理函数
const onProjectChange = () => {
  currentPage.value = 1
  imageUrls.value = {}
  selectedImages.value = []
  clearVisible()
  loadImages()
}

const handleFileUpload = (uploadFile: { raw: File }, uploadFiles: { raw: File }[]) => {
  selectedFiles.value = uploadFiles.map(file => file.raw)
}

const uploadImages = async () => {
  if (!selectedProject.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  
  if (!selectedFiles.value.length) {
    ElMessage.warning('请先选择图片文件')
    return
  }

  uploading.value = true
  let successCount = 0
  
  try {
    for (const file of selectedFiles.value) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('tag_ids', '[]')
      
      try {
        await imageApi.uploadImage(selectedProject.value, formData)
        successCount++
      } catch (error) {
        console.error(`Upload failed for ${file.name}:`, error)
      }
    }
    
    ElMessage.success(`成功上传 ${successCount}/${selectedFiles.value.length} 张图片`)
    
    // 清理文件选择
    clearAllFiles()
    
    await loadImages()
    
  } catch (error) {
    ElMessage.error('图片上传失败')
    console.error('Upload error:', error)
  } finally {
    uploading.value = false
  }
}

const openImagePreview = (image: Image) => {
  previewImageData.value = image
  showImagePreview.value = true
  getImageFullUrl(image)
}

const closeImagePreview = () => {
  showImagePreview.value = false
  setTimeout(() => {
    if (!showImagePreview.value) {
      previewImageData.value = null
    }
  }, 300)
}

const previewImage = (image: Image) => {
  openImagePreview(image)
}

const editImageTags = (image: Image) => {
  selectedImage.value = image
  currentImageTags.value = [...(image.tags || [])]
  showTagDialog.value = true
}

const closeTagDialog = () => {
  showTagDialog.value = false
  setTimeout(() => {
    if (!showTagDialog.value) {
      selectedImage.value = null
      currentImageTags.value = []
      newTagId.value = null
    }
  }, 300)
}

const addTagToCurrent = () => {
  if (!newTagId.value) {
    ElMessage.warning('请选择要添加的标签')
    return
  }
  
  const tag = availableTags.value.find(t => t.id === newTagId.value)
  if (tag && !currentImageTags.value.find(t => t.id === tag.id)) {
    currentImageTags.value.push(tag)
    newTagId.value = null
    ElMessage.success('标签添加成功')
  } else {
    ElMessage.warning('标签已存在或无效')
  }
}

const removeTagFromCurrent = (tagId: number) => {
  currentImageTags.value = currentImageTags.value.filter(t => t.id !== tagId)
  ElMessage.success('标签移除成功')
}

const saveImageTags = async () => {
  if (!selectedImage.value) return
  
  savingTags.value = true
  try {
    const tagIds = currentImageTags.value.map(tag => tag.id)
    const response = await imageApi.updateImageTags(selectedImage.value.id, tagIds) as unknown as { code: number, message?: string }
    
    if (response?.code === 200) {
      const imageIndex = images.value.findIndex(img => img.id === selectedImage.value!.id)
      if (imageIndex !== -1) {
        images.value[imageIndex].tags = [...currentImageTags.value]
      }
      
      ElMessage.success('标签保存成功')
      closeTagDialog()
    } else {
      ElMessage.error(response?.message || '标签保存失败')
    }
  } catch (error) {
    ElMessage.error('标签保存失败')
    console.error('Save tags error:', error)
  } finally {
    savingTags.value = false
  }
}

const deleteImage = async (image: Image) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除图片 "${image.filename || '图片'}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const response = await imageApi.deleteImage(image.id) as unknown as { code: number, message?: string }
    if (response?.code === 200) {
      ElMessage.success('图片删除成功')
      const cacheKey = getImageCacheKey(image)
      delete imageUrls.value[cacheKey]
      await loadImages()
    } else {
      ElMessage.error(response?.message || '图片删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('图片删除失败')
      console.error('Delete image error:', error)
    }
  }
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadImages()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadImages()
}

// 监听路由变化
watch(
  () => route.query.project,
  () => {
    loadProjects()
  }
)

// 监听项目变化
watch(
  () => selectedProject.value,
  () => {
    if (selectedProject.value) {
      loadImages()
    }
  }
)

// 监听选中文件变化
watch(selectedFiles, (newVal) => {
  if (newVal.length > 0) {
    if (fileSelectTimer.value) {
      clearTimeout(fileSelectTimer.value)
    }
    
    fileSelectTimer.value = setTimeout(() => {
      ElMessage.success(`已选择 ${newVal.length} 个文件`)
      fileSelectTimer.value = null
    }, 300)
  }
})

// 组件挂载
onMounted(() => {
  loadViewMode()
  loadProjects()
  loadTags()
})

// 组件卸载时清理
onUnmounted(() => {
  if (fileSelectTimer.value) {
    clearTimeout(fileSelectTimer.value)
  }
  
  // 清理所有预览URL
  Object.values(filePreviewUrls.value).forEach(url => {
    URL.revokeObjectURL(url)
  })
  
  imageUrls.value = {}
  filePreviewUrls.value = {}
  filePreviewStates.value = {}
})
</script>

<style scoped>
.image-gallery {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.gallery-header {
  margin-bottom: 24px;
}

.gallery-controls {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.view-toggle {
  margin-left: auto;
}

@media (max-width: 768px) {
  .gallery-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .view-toggle {
    margin-left: 0;
    align-self: center;
  }
}

/* 待上传图片预览面板 */
.upload-preview-panel {
  margin-top: 16px;
  margin-bottom: 16px;
  padding: 16px;
  background: var(--el-fill-color-extra-light);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

.upload-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.upload-preview-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.upload-preview-container {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 4px 0;
}

.upload-preview-container::-webkit-scrollbar {
  height: 6px;
}

.upload-preview-container::-webkit-scrollbar-track {
  background: var(--el-fill-color-lighter);
  border-radius: 3px;
}

.upload-preview-container::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 3px;
}

.upload-preview-container::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-darker);
}

.upload-preview-item {
  flex-shrink: 0;
  width: 120px;
  background: white;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
  overflow: hidden;
  transition: all 0.2s ease;
}

.upload-preview-item:hover {
  border-color: var(--el-color-primary-light-5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.preview-image-wrapper {
  position: relative;
  width: 100%;
  height: 80px;
  overflow: hidden;
  background: var(--el-fill-color-light);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.upload-preview-item:hover .preview-image {
  transform: scale(1.05);
}

.preview-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  color: var(--el-text-color-secondary);
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.upload-preview-item:hover .preview-overlay {
  opacity: 1;
}

.preview-actions {
  display: flex;
  gap: 4px;
}

.preview-info {
  padding: 8px;
  background: white;
}

.file-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
  line-height: 1.2;
  word-break: break-all;
}

.file-size {
  font-size: 11px;
  color: var(--el-text-color-secondary);
}

/* 移动端适配 */
@media (max-width: 768px) {
  .upload-preview-panel {
    padding: 12px;
  }
  
  .upload-preview-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .upload-preview-item {
    width: 100px;
  }
  
  .preview-image-wrapper {
    height: 70px;
  }
}

@media (max-width: 480px) {
  .upload-preview-container {
    gap: 8px;
  }
  
  .upload-preview-item {
    width: 80px;
  }
  
  .preview-image-wrapper {
    height: 60px;
  }
  
  .preview-info {
    padding: 6px;
  }
}

/* 批量操作面板 */
.batch-panel {
  margin-top: 16px;
  padding: 16px;
  background: var(--el-fill-color-extra-light);
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.batch-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .batch-panel {
    flex-direction: column;
    align-items: stretch;
  }
  
  .batch-info {
    justify-content: center;
  }
  
  .batch-actions {
    justify-content: center;
  }
}

/* 加载状态 */
.loading-container {
  margin: 40px 0;
}

/* 网格视图样式 */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .gallery-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
}

.image-card {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  border: 2px solid var(--el-border-color);
  box-sizing: border-box;
}

.image-card:hover {
  transform: translateY(-2px);
}

.image-card:hover .image-actions {
  opacity: 1;
}

.image-card.selected {
  border: 2px solid var(--el-color-primary);
}

.image-card.batch-selected {
  border: 2px solid var(--el-color-success);
  box-shadow: 0 0 0 2px var(--el-color-success-light-9);
}

.batch-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  border-radius: 4px;
  padding: 4px;
}

.image-container {
  position: relative;
}

.image-preview {
  width: 100%;
  height: 200px;
  cursor: pointer;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--el-text-color-placeholder);
  background: var(--el-fill-color-light);
}

.loading-icon {
  animation: rotate 2s linear infinite;
  margin-bottom: 8px;
  font-size: 24px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--el-text-color-placeholder);
  background: var(--el-fill-color-light);
  gap: 8px;
}

.image-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-info {
  padding: 16px;
  cursor: pointer;
}

.image-info:hover {
  background: var(--el-fill-color-extra-light);
}

.image-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.image-meta {
  margin-bottom: 12px;
}

.upload-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.image-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.image-tag {
  margin: 0;
  font-size: 11px;
}

/* 列表视图样式 */
.gallery-list {
  margin-bottom: 24px;
}

.table-image-preview {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  cursor: pointer;
}

.table-image-error {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  color: var(--el-text-color-placeholder);
}

.table-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

:deep(.selected-row) {
  background-color: var(--el-color-success-light-9) !important;
}

:deep(.selected-row:hover) {
  background-color: var(--el-color-success-light-8) !important;
}

/* 分页容器 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 预览对话框 */
:deep(.image-preview-dialog) {
  border-radius: 12px;
  top: 50% !important;
  transform: translateY(-50%);
  margin: auto;
}

.preview-container {
  text-align: center;
}

.preview-container .el-image {
  overflow-y: auto;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--el-text-color-placeholder);
}

/* 标签编辑对话框 */
.tag-dialog-content {
  padding: 0;
}

.image-preview-small {
  display: flex;
  align-items: center;
  gap: 16px;
}

.image-name h4 {
  margin: 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

.tag-editor {
  padding: 0;
}

.current-tags h5,
.add-tag-section h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.existing-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
  min-height: 32px;
  align-items: flex-start;
}

.tag-item {
  margin: 0;
}

.no-tags {
  color: var(--el-text-color-placeholder);
  font-size: 12px;
}

.add-tag {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dialog-footer {
  text-align: right;
}

/* 批量添加标签对话框 */
.batch-tag-content p {
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
}

/* 响应式设计 */
@media (max-width: 480px) {
  .image-gallery {
    padding: 16px;
  }
  
  .gallery-grid {
    grid-template-columns: 1fr;
  }
  
  .image-card .image-actions {
    opacity: 1;
  }
  
  .batch-panel {
    padding: 12px;
  }
  
  .batch-actions {
    width: 100%;
  }
  
  .batch-actions .el-button {
    flex: 1;
  }
}

/* 动画效果 */
.gallery-grid,
.gallery-list {
  animation: fadeIn 0.3s ease-in-out;
}

.upload-preview-panel {
  animation: slideDown 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
    max-height: 0;
  }
  to {
    opacity: 1;
    transform: translateY(0);
    max-height: 200px;
  }
}

/* 批量选择模式下的视觉反馈 */
.image-card.batch-selected .image-preview {
  filter: brightness(0.9);
}

.image-card.batch-selected:hover .image-preview {
  filter: brightness(1);
}

/* 待上传预览项的错误状态 */
.upload-preview-item .preview-image[src=""] {
  background: var(--el-fill-color-light);
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-preview-item .preview-image[src=""]:after {
  content: "❌";
  font-size: 24px;
}
</style>