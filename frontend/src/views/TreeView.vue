<template>
  <div class="tree-view">
    <div class="tree-header">
      <h1>标签树形视图</h1>
      <div class="tree-controls">
        <button @click="expandAll" class="control-btn">展开全部</button>
        <button @click="collapseAll" class="control-btn">收起全部</button>
        <button @click="showAddDialog = true" class="add-btn">添加分类</button>
      </div>
    </div>

    <div class="tree-container">
      <div class="tree-sidebar">
        <div class="project-filter">
          <select v-model="selectedProject" @change="loadTreeData">
            <option value="">所有项目</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.name }}
            </option>
          </select>
        </div>
        
        <div class="tree-content">
          <TreeNode
            v-for="node in treeData"
            :key="node.id"
            :node="node"
            :level="0"
            @select="selectNode"
            @toggle="toggleNode"
            @edit="editNode"
            @delete="deleteNode"
            @add-child="addChildNode"
          />
        </div>
      </div>

      <div class="tree-details" v-if="selectedNode">
        <div class="details-header">
          <h2>{{ selectedNode.name }}</h2>
          <div class="node-actions">
            <button @click="editNode(selectedNode)" class="edit-btn">编辑</button>
            <button @click="deleteNode(selectedNode)" class="delete-btn">删除</button>
          </div>
        </div>
        
        <div class="node-info">
          <div class="info-item">
            <label>类型:</label>
            <span>{{ selectedNode.type === 'category' ? '分类' : '标签' }}</span>
          </div>
          <div class="info-item">
            <label>颜色:</label>
            <div class="color-display" :style="{ backgroundColor: selectedNode.color }"></div>
          </div>
          <div class="info-item">
            <label>描述:</label>
            <p>{{ selectedNode.description || '无描述' }}</p>
          </div>
          <div class="info-item">
            <label>创建时间:</label>
            <span>{{ formatDate(selectedNode.createdAt) }}</span>
          </div>
        </div>

        <div class="associated-images" v-if="selectedNode.type === 'tag'">
          <h3>关联图片 ({{ associatedImages.length }})</h3>
          <div class="image-list">
            <div 
              v-for="image in associatedImages" 
              :key="image.id" 
              class="image-item"
            >
              <img :src="image.thumbnail" :alt="image.name" />
              <span>{{ image.name }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <div v-if="showAddDialog || showEditDialog" class="dialog-overlay" @click="closeDialogs">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ showAddDialog ? '添加' : '编辑' }}{{ dialogForm.type === 'category' ? '分类' : '标签' }}</h3>
          <button @click="closeDialogs" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="saveNode" class="dialog-form">
          <div class="form-group">
            <label>名称:</label>
            <input v-model="dialogForm.name" type="text" required />
          </div>
          
          <div class="form-group">
            <label>类型:</label>
            <select v-model="dialogForm.type" required>
              <option value="category">分类</option>
              <option value="tag">标签</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>颜色:</label>
            <input v-model="dialogForm.color" type="color" />
          </div>
          
          <div class="form-group">
            <label>父级分类:</label>
            <select v-model="dialogForm.parentId">
              <option value="">顶级分类</option>
              <option 
                v-for="category in categories" 
                :key="category.id" 
                :value="category.id"
                :disabled="category.id === dialogForm.id"
              >
                {{ category.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>描述:</label>
            <textarea v-model="dialogForm.description" rows="3"></textarea>
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
import { ref, reactive, computed, onMounted } from 'vue'
import TreeNode from '@/components/TreeNode.vue'

export default {
  name: 'TreeView',
  components: {
    TreeNode
  },
  setup() {
    const treeData = ref([])
    const selectedNode = ref(null)
    const selectedProject = ref('')
    const projects = ref([])
    const associatedImages = ref([])
    const showAddDialog = ref(false)
    const showEditDialog = ref(false)
    const expandedNodes = ref(new Set())

    const dialogForm = reactive({
      id: null,
      name: '',
      type: 'category',
      color: '#007bff',
      parentId: '',
      description: ''
    })

    const categories = computed(() => {
      const getAllCategories = (nodes) => {
        let result = []
        nodes.forEach(node => {
          if (node.type === 'category') {
            result.push(node)
            if (node.children) {
              result = result.concat(getAllCategories(node.children))
            }
          }
        })
        return result
      }
      return getAllCategories(treeData.value)
    })

    const loadProjects = async () => {
      // 模拟数据
      projects.value = [
        { id: 1, name: '项目A' },
        { id: 2, name: '项目B' },
        { id: 3, name: '项目C' }
      ]
    }

    const loadTreeData = async () => {
      // 模拟树形数据
      treeData.value = [
        {
          id: 1,
          name: '人物分类',
          type: 'category',
          color: '#ff6b6b',
          description: '所有人物相关的标签',
          createdAt: new Date('2024-01-01'),
          children: [
            {
              id: 2,
              name: '成人',
              type: 'tag',
              color: '#ff6b6b',
              parentId: 1,
              createdAt: new Date('2024-01-02'),
              children: []
            },
            {
              id: 3,
              name: '儿童',
              type: 'tag',
              color: '#ff8e8e',
              parentId: 1,
              createdAt: new Date('2024-01-02'),
              children: []
            }
          ]
        },
        {
          id: 4,
          name: '动物分类',
          type: 'category',
          color: '#4ecdc4',
          description: '所有动物相关的标签',
          createdAt: new Date('2024-01-01'),
          children: [
            {
              id: 5,
              name: '哺乳动物',
              type: 'category',
              color: '#4ecdc4',
              parentId: 4,
              createdAt: new Date('2024-01-02'),
              children: [
                {
                  id: 6,
                  name: '猫',
                  type: 'tag',
                  color: '#4ecdc4',
                  parentId: 5,
                  createdAt: new Date('2024-01-03'),
                  children: []
                },
                {
                  id: 7,
                  name: '狗',
                  type: 'tag',
                  color: '#6ed5cd',
                  parentId: 5,
                  createdAt: new Date('2024-01-03'),
                  children: []
                }
              ]
            },
            {
              id: 8,
              name: '鸟类',
              type: 'tag',
              color: '#7fdedb',
              parentId: 4,
              createdAt: new Date('2024-01-02'),
              children: []
            }
          ]
        }
      ]
    }

    const selectNode = (node) => {
      selectedNode.value = node
      if (node.type === 'tag') {
        loadAssociatedImages(node.id)
      }
    }

    const loadAssociatedImages = async (tagId) => {
      // 模拟关联图片数据
      associatedImages.value = [
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

    const toggleNode = (nodeId) => {
      if (expandedNodes.value.has(nodeId)) {
        expandedNodes.value.delete(nodeId)
      } else {
        expandedNodes.value.add(nodeId)
      }
    }

    const expandAll = () => {
      const getAllNodeIds = (nodes) => {
        let ids = []
        nodes.forEach(node => {
          ids.push(node.id)
          if (node.children && node.children.length > 0) {
            ids = ids.concat(getAllNodeIds(node.children))
          }
        })
        return ids
      }
      
      const allIds = getAllNodeIds(treeData.value)
      expandedNodes.value = new Set(allIds)
    }

    const collapseAll = () => {
      expandedNodes.value.clear()
    }

    const editNode = (node) => {
      dialogForm.id = node.id
      dialogForm.name = node.name
      dialogForm.type = node.type
      dialogForm.color = node.color
      dialogForm.parentId = node.parentId || ''
      dialogForm.description = node.description || ''
      showEditDialog.value = true
    }

    const addChildNode = (parentNode) => {
      resetDialogForm()
      dialogForm.parentId = parentNode.id
      dialogForm.type = 'tag'
      showAddDialog.value = true
    }

    const deleteNode = (node) => {
      if (confirm(`确定要删除 "${node.name}" 吗？`)) {
        // 实现删除逻辑
        console.log('删除节点:', node)
        // 这里应该调用API删除节点，然后重新加载数据
        loadTreeData()
      }
    }

    const resetDialogForm = () => {
      dialogForm.id = null
      dialogForm.name = ''
      dialogForm.type = 'category'
      dialogForm.color = '#007bff'
      dialogForm.parentId = ''
      dialogForm.description = ''
    }

    const closeDialogs = () => {
      showAddDialog.value = false
      showEditDialog.value = false
      resetDialogForm()
    }

    const saveNode = async () => {
      try {
        if (showEditDialog.value) {
          // 更新节点
          console.log('更新节点:', dialogForm)
        } else {
          // 创建新节点
          console.log('创建节点:', dialogForm)
        }
        
        // 这里应该调用API保存数据
        await loadTreeData()
        closeDialogs()
      } catch (error) {
        console.error('保存失败:', error)
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('zh-CN')
    }

    onMounted(() => {
      loadProjects()
      loadTreeData()
    })

    return {
      treeData,
      selectedNode,
      selectedProject,
      projects,
      associatedImages,
      showAddDialog,
      showEditDialog,
      dialogForm,
      categories,
      expandedNodes,
      selectNode,
      toggleNode,
      expandAll,
      collapseAll,
      editNode,
      addChildNode,
      deleteNode,
      closeDialogs,
      saveNode,
      formatDate,
      loadTreeData
    }
  }
}
</script>

<style scoped>
.tree-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.tree-header h1 {
  margin: 0;
  color: #333;
}

.tree-controls {
  display: flex;
  gap: 10px;
}

.control-btn, .add-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  transition: background-color 0.3s;
}

.add-btn {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.control-btn:hover {
  background-color: #f8f9fa;
}

.add-btn:hover {
  background-color: #0056b3;
}

.tree-container {
  display: flex;
  gap: 30px;
  height: calc(100vh - 200px);
}

.tree-sidebar {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.project-filter {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
}

.project-filter select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.tree-content {
  padding: 15px;
  overflow-y: auto;
  height: calc(100% - 60px);
}

.tree-details {
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  overflow-y: auto;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.details-header h2 {
  margin: 0;
  color: #333;
}

.node-actions {
  display: flex;
  gap: 10px;
}

.edit-btn, .delete-btn {
  padding: 6px 12px;
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

.delete-btn {
  background-color: #dc3545;
  border-color: #dc3545;
  color: white;
}

.node-info {
  margin-bottom: 30px;
}

.info-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.info-item label {
  font-weight: bold;
  width: 80px;
  color: #666;
}

.color-display {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 1px solid #ddd;
}

.associated-images h3 {
  margin-bottom: 15px;
  color: #333;
}

.image-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}

.image-item {
  text-align: center;
}

.image-item img {
  width: 100%;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  margin-bottom: 5px;
}

.image-item span {
  font-size: 12px;
  color: #666;
  display: block;
  word-break: break-all;
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
  z-index: 1000;
}

.dialog {
  background: white;
  border-radius: 8px;
  width: 500px;
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

.form-group textarea {
  resize: vertical;
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
