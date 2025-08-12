<template>
  <div class="tabs-bar">
    <div class="tabs-container" ref="tabsContainer">
      <div
        v-for="tab in tabsStore.tabs"
        :key="tab.name"
        class="tab-item"
        :class="{ active: tab.name === tabsStore.activeTab }"
        @click="handleTabClick(tab)"
        @contextmenu="handleRightClick($event, tab)"
      >
        <span class="tab-title">{{ tab.title }}</span>
        <el-icon
          v-if="tab.closable !== false"
          class="close-icon"
          @click.stop="tabsStore.removeTab(tab.name)"
        >
          <Close />
        </el-icon>
      </div>
    </div>

    <!-- 右键菜单 -->
    <div
      v-if="contextMenu.visible"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
    >
      <div class="menu-item" @click="closeOther">关闭其他</div>
      <div class="menu-item" @click="closeLeft">关闭左侧</div>
      <div class="menu-item" @click="closeRight">关闭右侧</div>
      <div class="menu-item" @click="closeAll">关闭所有</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTabsStore } from '@/stores/tabs'
import type { TabItem } from '@/types'
import { Close } from '@element-plus/icons-vue'
import { onMounted, onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const tabsStore = useTabsStore()
const router = useRouter()

const tabsContainer = ref<HTMLElement>()
const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  tab: null as TabItem | null
})

const handleTabClick = (tab: TabItem) => {
  tabsStore.activeTab = tab.name
  router.push(tab.path)
}

const handleRightClick = (event: MouseEvent, tab: TabItem) => {
  event.preventDefault()
  event.stopPropagation()
  contextMenu.visible = true
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.tab = tab
}

const closeOther = () => {
  console.log(contextMenu)
  if (contextMenu.tab) {
    tabsStore.removeOtherTabs(contextMenu.tab.name)
  }
  contextMenu.visible = false
}

const closeLeft = () => {
  if (contextMenu.tab) {
    tabsStore.removeLeftTabs(contextMenu.tab.name)
  }
  contextMenu.visible = false
}

const closeRight = () => {
  if (contextMenu.tab) {
    tabsStore.removeRightTabs(contextMenu.tab.name)
  }
  contextMenu.visible = false
}

const closeAll = () => {
  tabsStore.removeAllTabs()
  contextMenu.visible = false
}

const handleDocumentClick = (e: MouseEvent) => {
  // 只在左键点击 & 点击目标不在菜单内时关闭
  if (e.button === 0 && !(e.target as HTMLElement).closest('.context-menu')) {
    contextMenu.visible = false
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleDocumentClick)
})
</script>

<style scoped>
.tabs-bar {
  height: 42px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  position: relative;
  font-size: 14px;
}

.tabs-container {
  display: flex;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}

.tabs-container::-webkit-scrollbar {
  height: 4px;
}

.tabs-container::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 2px;
}

.tab-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 14px;
  min-width: 110px;
  background: #fafafa;
  border-right: 1px solid #f0f0f0;
  cursor: pointer;
  user-select: none;
  transition: background 0.25s, box-shadow 0.25s;
  position: relative;
}

.tab-item:hover {
  background: linear-gradient(180deg, #f5faff, #e8f4ff);
}

.tab-item.active {
  background: #fff;
  color: #1890ff;
  font-weight: 500;
  box-shadow: inset 0 -2px 0 #1890ff;
}

.tab-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-icon {
  margin-left: 6px;
  font-size: 13px;
  padding: 2px;
  border-radius: 50%;
  transition: background-color 0.2s, color 0.2s;
}

.close-icon:hover {
  background: #ff4d4f;
  color: #fff;
}

.context-menu {
  position: fixed;
  background: #fff;
  border: 1px solid #e8e8e8;
  border-radius: 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  z-index: 2000;
  min-width: 130px;
  padding: 4px 0;
  animation: fadeIn 0.15s ease-out;
}

.menu-item {
  padding: 8px 14px;
  cursor: pointer;
  transition: background-color 0.25s;
}

.menu-item:hover {
  background: #f5f5f5;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
