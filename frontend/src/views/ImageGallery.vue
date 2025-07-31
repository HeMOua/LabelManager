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
              accept="image/*"
              multiple
              @change="handleFileUpload"
              action="#"
            >
              <el-button type="primary" :icon="Upload">
                选择图片
              </el-button>
            </el-upload>
            <el-button @click="uploadImages" type="success" :icon="UploadFilled">
              上传图片
            </el-button>
            <el-select 
              v-model="selectedProject" 
              placeholder="选择项目"
              style="width: 200px"
              clearable
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

    <div class="gallery-grid" v-if="images.length > 0">
      <el-card 
        v-for="image in filteredImages" 
        :key="image.id" 
        class="image-card"
        @click="selectImage(image)"
        :class="{ selected: selectedImage?.id === image.id }"
        shadow="hover"
      >
        <el-image
          :src="image.thumbnail"
          :alt="image.name"
          fit="cover"
          style="width: 100%; height: 200px;"
          lazy
        />
        <div class="image-info">
          <h3>{{ image.name }}</h3>
          <div class="image-tags">
            <el-tag 
              v-for="tag in image.tags" 
              :key="tag.id" 
              :color="tag.color"
              size="small"
              class="image-tag"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <el-empty v-else description="暂无图片，请上传图片开始标注" />

    <!-- 图片详情对话框 -->
    <el-dialog
      v-model="showImageDialog"
      title="图片详情"
      width="80%"
      :before-close="closeModal"
    >
      <div class="image-dialog-content" v-if="selectedImage">
        <div class="image-preview">
          <el-image 
            :src="selectedImage.url" 
            :alt="selectedImage.name"
            fit="contain"
            style="width: 100%; max-height: 60vh;"
          />
        </div>
        <div class="image-details">
          <el-descriptions :title="selectedImage.name" :column="2" border>
            <el-descriptions-item label="文件名">{{ selectedImage.name }}</el-descriptions-item>
            <el-descriptions-item label="项目">{{ getProjectName(selectedImage.projectId) }}</el-descriptions-item>
          </el-descriptions>
          
          <div class="tag-editor">
            <el-divider content-position="left">标签管理</el-divider>
            
            <div class="existing-tags">
              <el-tag 
                v-for="tag in selectedImage.tags" 
                :key="tag.id" 
                :color="tag.color"
                closable
                @close="removeTag(tag.id)"
                class="tag-item"
              >
                {{ tag.name }}
              </el-tag>
            </div>
            
            <div class="add-tag">
              <el-select 
                v-model="newTagId" 
                placeholder="选择要添加的标签"
                style="width: 200px; margin-right: 10px;"
                clearable
              >
                <el-option
                  v-for="tag in availableTags"
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
              </el-select>
              <el-button @click="addTag" type="primary" :icon="Plus">添加标签</el-button>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAppStore } from '../stores/app.js'
import { Upload, UploadFilled, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

export default {
  name: 'ImageGallery',
  setup() {
    const appStore = useAppStore()
    
    const images = ref([])
    const selectedImage = ref(null)
    const selectedProject = ref('')
    const newTagId = ref('')
    const projects = ref([])
    const availableTags = ref([])
    const showImageDialog = ref(false)
    const uploadRef = ref()

    const filteredImages = computed(() => {
      if (!selectedProject.value) return images.value
      return images.value.filter(img => img.projectId === selectedProject.value)
    })

    const getProjectName = (projectId) => {
      const project = projects.value.find(p => p.id === projectId)
      return project ? project.name : '未知项目'
    }

    const loadProjects = async () => {
      // 模拟数据，实际应该从API获取
      projects.value = [
        { id: 1, name: '项目A' },
        { id: 2, name: '项目B' },
        { id: 3, name: '项目C' }
      ]
    }

    const loadTags = async () => {
      // 模拟数据，实际应该从API获取
      availableTags.value = [
        { id: 1, name: '人物', color: '#ff6b6b' },
        { id: 2, name: '动物', color: '#4ecdc4' },
        { id: 3, name: '建筑', color: '#45b7d1' },
        { id: 4, name: '风景', color: '#96ceb4' },
        { id: 5, name: '车辆', color: '#feca57' }
      ]
    }

    const loadImages = async () => {
      // 模拟数据，实际应该从API获取
      images.value = [
        {
          id: 1,
          name: 'sample1.jpg',
          url: '/api/images/sample1.jpg',
          thumbnail: '/api/images/thumbnails/sample1.jpg',
          projectId: 1,
          tags: [
            { id: 1, name: '人物', color: '#ff6b6b' },
            { id: 3, name: '建筑', color: '#45b7d1' }
          ]
        },
        {
          id: 2,
          name: 'sample2.jpg',
          url: '/api/images/sample2.jpg',
          thumbnail: '/api/images/thumbnails/sample2.jpg',
          projectId: 1,
          tags: [
            { id: 2, name: '动物', color: '#4ecdc4' }
          ]
        }
      ]
    }

    const handleFileUpload = (uploadFile, uploadFiles) => {
      console.log('选择的文件:', uploadFiles)
      ElMessage.success(`已选择 ${uploadFiles.length} 个文件`)
    }

    const uploadImages = async () => {
      try {
        console.log('上传图片')
        ElMessage.success('图片上传成功！')
        await loadImages()
      } catch (error) {
        ElMessage.error('图片上传失败')
      }
    }

    const selectImage = (image) => {
      selectedImage.value = image
      showImageDialog.value = true
    }

    const closeModal = () => {
      selectedImage.value = null
      showImageDialog.value = false
    }

    const addTag = () => {
      if (!newTagId.value || !selectedImage.value) {
        ElMessage.warning('请选择要添加的标签')
        return
      }
      
      const tag = availableTags.value.find(t => t.id === parseInt(newTagId.value))
      if (tag && !selectedImage.value.tags.find(t => t.id === tag.id)) {
        selectedImage.value.tags.push(tag)
        newTagId.value = ''
        ElMessage.success('标签添加成功')
      } else {
        ElMessage.warning('标签已存在或无效')
      }
    }

    const removeTag = (tagId) => {
      if (selectedImage.value) {
        selectedImage.value.tags = selectedImage.value.tags.filter(t => t.id !== tagId)
        ElMessage.success('标签移除成功')
      }
    }

    onMounted(() => {
      loadProjects()
      loadTags()
      loadImages()
    })

    return {
      images,
      selectedImage,
      selectedProject,
      newTagId,
      projects,
      availableTags,
      filteredImages,
      showImageDialog,
      uploadRef,
      handleFileUpload,
      uploadImages,
      selectImage,
      closeModal,
      addTag,
      removeTag,
      getProjectName,
      // Element Plus 图标
      Upload,
      UploadFilled,
      Plus
    }
  }
}
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

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.image-card {
  cursor: pointer;
  transition: all 0.3s ease;
}

.image-card:hover {
  transform: translateY(-2px);
}

.image-card.selected {
  border: 2px solid var(--el-color-primary);
}

.image-info {
  padding: 16px;
}

.image-info h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: var(--el-text-color-primary);
}

.image-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.image-tag {
  margin: 0;
}

.image-dialog-content {
  display: flex;
  gap: 24px;
  flex-direction: column;
}

.image-preview {
  text-align: center;
}

.tag-editor {
  margin-top: 20px;
}

.existing-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  min-height: 32px;
  padding: 8px;
  border: 1px dashed var(--el-border-color);
  border-radius: 4px;
}

.tag-item {
  margin: 0;
}

.add-tag {
  display: flex;
  align-items: center;
  gap: 10px;
}

@media (min-width: 768px) {
  .image-dialog-content {
    flex-direction: row;
  }
  
  .image-preview {
    flex: 1;
  }
  
  .image-details {
    flex: 1;
    min-width: 300px;
  }
}
</style>
