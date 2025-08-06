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
            >
              <el-button type="primary" :icon="Upload">
                选择图片
              </el-button>
            </el-upload>
            <el-button 
              @click="uploadImages" 
              type="success" 
              :icon="UploadFilled"
              :loading="uploading"
              :disabled="!selectedFiles.length || !selectedProject"
            >
              上传图片 ({{ selectedFiles.length }})
            </el-button>
            <el-select 
              v-model="selectedProject" 
              placeholder="选择项目"
              style="width: 200px"
              clearable
              @change="onProjectChange"
            >
              <el-option
                v-for="project in projects"
                :key="project.id"
                :label="project.name"
                :value="project.id"
              />
            </el-select>
          </div>
        </template>
      </el-page-header>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- 图片网格 -->
    <div class="gallery-grid" v-else-if="filteredImages.length > 0">
      <el-card 
        v-for="image in filteredImages" 
        :key="image.id" 
        class="image-card"
        :class="{ selected: selectedImage?.id === image.id }"
        shadow="hover"
      >
        <div class="image-container">
          <el-image
            :src="getImageThumbnail(image)"
            :alt="image.filename || '图片'"
            fit="cover"
            class="image-preview"
            lazy
            loading="lazy"
            @click="previewImage(image)"
            @error="handleImageError(image)"
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
          <div class="image-actions">
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
        
        <div class="image-info" @click="editImageTags(image)">
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
    <div class="pagination-container" v-if="total > pageSize">
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
          style="width: 100%; max-height: 70vh;"
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Upload, UploadFilled, Plus, View, Edit, Delete, Picture, Loading } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Image, Tag, Project } from '@/types/index'
import { projectApi } from '@/api/project'
import { useRoute } from 'vue-router'
import { tagApi } from '@/api/tags'
import { imageApi } from '@/api/image'
import { fileApi } from '@/api/file'

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

// 图片URL缓存 - 使用响应式对象而不是Map，确保Vue能检测到变化
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
  const cacheKey = initImageCache(image)
  const cache = imageUrls.value[cacheKey]
  
  // 如果缓存中有缩略图URL，直接返回
  if (cache.thumbnailUrl && !cache.thumbnailError) {
    return cache.thumbnailUrl
  }
  
  // 如果有直接的URL，使用它
  if (image.url) {
    cache.thumbnailUrl = image.url
    return image.url
  }
  
  // 如果正在加载，返回占位符
  if (cache.thumbnailLoading) {
    return ''
  }
  
  // 开始异步加载
  loadImageThumbnail(image, cacheKey)
  
  return ''
}

// 获取完整图片URL
const getImageFullUrl = (image: Image): string => {
  const cacheKey = initImageCache(image)
  const cache = imageUrls.value[cacheKey]
  
  // 如果缓存中有完整URL，直接返回
  if (cache.fullUrl && !cache.fullError) {
    return cache.fullUrl
  }
  
  // 如果有直接的URL，使用它
  if (image.url) {
    cache.fullUrl = image.url
    return image.url
  }
  
  // 如果正在加载，返回缩略图或占位符
  if (cache.fullLoading) {
    return cache.thumbnailUrl || ''
  }
  
  // 开始异步加载
  loadImageFullUrl(image, cacheKey)
  
  return cache.thumbnailUrl || ''
}

// 异步加载缩略图
const loadImageThumbnail = async (image: Image, cacheKey: string) => {
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
  } catch (error) {
    console.error(`Failed to load thumbnail for image ${image.id}:`, error)
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
    // 重新触发加载
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
      
      // 设置选中的项目
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
      
      // 预加载图片URL
      await nextTick()
      images.value.forEach(image => {
        // 初始化缓存并开始加载
        getImageThumbnail(image)
      })
      
      // 如果API返回总数，更新total
      if (response.total !== undefined) {
        total.value = response.total
      } else if (Array.isArray(response.data)) {
        total.value = response.data.length
      }
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
  // 清空URL缓存
  imageUrls.value = {}
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
      formData.append('tag_ids', '[]') // 暂时不添加标签
      
      try {
        await imageApi.uploadImage(selectedProject.value, formData)
        successCount++
      } catch (error) {
        console.error(`Upload failed for ${file.name}:`, error)
      }
    }
    
    ElMessage.success(`成功上传 ${successCount}/${selectedFiles.value.length} 张图片`)
    
    // 清空选择的文件
    selectedFiles.value = []
    uploadRef.value?.clearFiles()
    
    // 重新加载图片列表
    await loadImages()
    
  } catch (error) {
    ElMessage.error('图片上传失败')
    console.error('Upload error:', error)
  } finally {
    uploading.value = false
  }
}

// 打开图片预览 - 独立的预览功能
const openImagePreview = (image: Image) => {
  previewImageData.value = image
  showImagePreview.value = true
  // 预加载完整图片
  getImageFullUrl(image)
}

// 关闭图片预览
const closeImagePreview = () => {
  showImagePreview.value = false
  // 延迟清空预览图片，避免闪烁
  setTimeout(() => {
    if (!showImagePreview.value) {
      previewImageData.value = null
    }
  }, 300)
}

// 预览图片 - 点击图片本身时的处理
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
  // 延迟清空，避免闪烁
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
      // 更新本地数据
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
      // 从缓存中移除
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

// 监听选中文件变化，使用防抖提示
watch(selectedFiles, (newVal) => {
  if (newVal.length > 0) {
    // 清除之前的定时器
    if (fileSelectTimer.value) {
      clearTimeout(fileSelectTimer.value)
    }
    
    // 设置新的定时器，延迟 300ms 后提示
    fileSelectTimer.value = setTimeout(() => {
      ElMessage.success(`已选择 ${newVal.length} 个文件`)
      fileSelectTimer.value = null
    }, 300)
  }
})

// 组件挂载
onMounted(() => {
  loadProjects()
  loadTags()
})

// 组件卸载时清理定时器和缓存
onUnmounted(() => {
  if (fileSelectTimer.value) {
    clearTimeout(fileSelectTimer.value)
  }
  // 清理URL缓存
  imageUrls.value = {}
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
}

.loading-container {
  margin: 40px 0;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.image-card {
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
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

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 图片预览对话框样式 */
.image-preview-dialog :deep(.el-dialog__body) {
  padding: 20px;
  text-align: center;
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-container :deep(.el-image) {
  overflow-y: auto;
}

.preview-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--el-text-color-placeholder);
  background: var(--el-fill-color-light);
  border-radius: 8px;
}

/* 标签编辑对话框样式 */
.tag-dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.image-preview-small {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.image-name h4 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.tag-editor {
  space-y: 20px;
}

.current-tags,
.add-tag-section {
  margin-bottom: 24px;
}

.current-tags h5,
.add-tag-section h5 {
  margin: 0 0 12px 0;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.existing-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 32px;
  padding: 12px;
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  background: var(--el-fill-color-extra-light);
}

.no-tags {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.tag-item {
  margin: 0;
}

.add-tag {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 768px) {
  .image-gallery {
    padding: 16px;
  }
  
  .gallery-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .gallery-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 16px;
  }
  
  .image-preview-small {
    flex-direction: column;
    text-align: center;
  }

  .image-preview-dialog {
    width: 95% !important;
  }
}
</style>