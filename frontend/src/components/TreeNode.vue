<template>
  <div class="tree-node">
    <div 
      class="node-content"
      :class="{ 
        selected: node.selected,
        'category-node': node.type === 'category',
        'tag-node': node.type === 'tag'
      }"
      :style="{ paddingLeft: (level * 20) + 'px' }"
      @click="handleSelect"
    >
      <div class="node-toggle" v-if="hasChildren" @click.stop="handleToggle">
        <span :class="{ expanded: isExpanded }">▶</span>
      </div>
      <div class="node-spacer" v-else></div>
      
      <div class="node-icon">
        <div 
          class="color-indicator" 
          :style="{ backgroundColor: node.color }"
        ></div>
        <span class="type-icon">
          {{ node.type === 'category' ? '📁' : '🏷️' }}
        </span>
      </div>
      
      <div class="node-info">
        <span class="node-name">{{ node.name }}</span>
        <span class="node-type">{{ node.type === 'category' ? '分类' : '标签' }}</span>
      </div>
      
      <div class="node-actions" @click.stop>
        <button 
          v-if="node.type === 'category'" 
          @click="$emit('add-child', node)"
          class="action-btn add-btn"
          title="添加子项"
        >
          +
        </button>
        <button 
          @click="$emit('edit', node)"
          class="action-btn edit-btn"
          title="编辑"
        >
          ✎
        </button>
        <button 
          @click="$emit('delete', node)"
          class="action-btn delete-btn"
          title="删除"
        >
          ×
        </button>
      </div>
    </div>
    
    <div v-if="hasChildren && isExpanded" class="children">
      <TreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :level="level + 1"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @add-child="$emit('add-child', $event)"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { computed, ref, watch } from 'vue'

export default {
  name: 'TreeNode',
  props: {
    node: {
      type: Object,
      required: true
    },
    level: {
      type: Number,
      default: 0
    }
  },
  emits: ['select', 'toggle', 'edit', 'delete', 'add-child'],
  setup(props, { emit }) {
    const isExpanded = ref(false)
    
    const hasChildren = computed(() => {
      return props.node.children && props.node.children.length > 0
    })
    
    const handleSelect = () => {
      emit('select', props.node)
    }
    
    const handleToggle = () => {
      isExpanded.value = !isExpanded.value
      emit('toggle', props.node.id)
    }
    
    // 监听外部展开状态变化（例如"展开全部"按钮）
    watch(() => props.node.expanded, (newVal) => {
      if (newVal !== undefined) {
        isExpanded.value = newVal
      }
    })
    
    return {
      isExpanded,
      hasChildren,
      handleSelect,
      handleToggle
    }
  }
}
</script>

<style scoped>
.tree-node {
  user-select: none;
}

.node-content {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  margin: 2px 0;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s, border-color 0.2s;
  border: 1px solid transparent;
  position: relative;
}

.node-content:hover {
  background-color: #f8f9fa;
}

.node-content.selected {
  background-color: rgba(0, 123, 255, 0.1);
  border-color: #007bff;
}

.category-node {
  font-weight: 500;
}

.tag-node {
  font-weight: normal;
}

.node-toggle {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 5px;
  cursor: pointer;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.node-toggle:hover {
  background-color: #e9ecef;
}

.node-toggle span {
  font-size: 12px;
  color: #666;
  transition: transform 0.2s;
  transform: rotate(0deg);
}

.node-toggle span.expanded {
  transform: rotate(90deg);
}

.node-spacer {
  width: 25px;
  margin-right: 5px;
}

.node-icon {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-right: 10px;
}

.color-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1px solid #ddd;
  flex-shrink: 0;
}

.type-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.node-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.node-name {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.node-type {
  font-size: 11px;
  color: #888;
  background-color: #f1f3f4;
  padding: 2px 6px;
  border-radius: 10px;
  flex-shrink: 0;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.node-content:hover .node-actions {
  opacity: 1;
}

.action-btn {
  width: 20px;
  height: 20px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s;
}

.add-btn {
  background-color: #28a745;
  color: white;
}

.add-btn:hover {
  background-color: #218838;
}

.edit-btn {
  background-color: #ffc107;
  color: #212529;
}

.edit-btn:hover {
  background-color: #e0a800;
}

.delete-btn {
  background-color: #dc3545;
  color: white;
}

.delete-btn:hover {
  background-color: #c82333;
}

.children {
  margin-left: 10px;
  border-left: 1px solid #e9ecef;
  padding-left: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .node-content {
    padding: 6px 8px;
  }
  
  .node-name {
    font-size: 13px;
  }
  
  .node-type {
    font-size: 10px;
    padding: 1px 4px;
  }
  
  .action-btn {
    width: 18px;
    height: 18px;
    font-size: 11px;
  }
}
</style>
