<template>
  <div class="header">
    <div class="header-left">
      <el-button
        type="text"
        @click="appStore.toggleCollapsed"
        class="collapse-btn"
      >
        <el-icon size="18">
          <Fold v-if="!appStore.collapsed" />
          <Expand v-else />
        </el-icon>
      </el-button>
    </div>
    
    <div class="header-right">
      <el-button type="text" @click="showSearch = true">
        <el-icon><Search /></el-icon>
      </el-button>
      
      <el-button type="text" @click="appStore.toggleFullscreen">
        <el-icon>
          <FullScreen v-if="!appStore.isFullscreen" />
          <Aim v-else />
        </el-icon>
      </el-button>
      
      <el-dropdown @command="handleCommand">
        <div class="user-info">
          <el-avatar :src="userStore.userInfo.avatar" size="small" />
          <span class="username">{{ userStore.userInfo.username }}</span>
          <el-icon><ArrowDown /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人中心</el-dropdown-item>
            <el-dropdown-item command="settings">设置</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
    
    <!-- 搜索对话框 -->
    <el-dialog v-model="showSearch" title="搜索" width="600px">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索菜单..."
        @input="handleSearch"
        clearable
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <div class="search-results" v-if="searchResults.length > 0">
        <div
          v-for="item in searchResults"
          :key="item.id"
          class="search-item"
          @click="handleSearchItemClick(item)"
        >
          <el-icon v-if="item.icon">
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.title }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { defineComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useUserStore } from '@/stores/user'
import { useTabsStore } from '@/stores/tabs'
import type { MenuItem } from '@/types/index'
import {
  Fold,
  Expand,
  Search,
  FullScreen,
  Aim,
  ArrowDown
} from '@element-plus/icons-vue'

defineComponent({
  name: 'HeaderComponent'
})

const appStore = useAppStore()
const userStore = useUserStore()
const tabsStore = useTabsStore()
const router = useRouter()

const showSearch = ref(false)
const searchKeyword = ref('')
const searchResults = ref<MenuItem[]>([])

const handleCommand = (command: string) => {
  switch (command) {
    case 'profile':
      // 跳转到个人中心
      break
    case 'settings':
      // 跳转到设置页面
      break
    case 'logout':
      userStore.logout()
      break
  }
}

const flattenMenus = (menus: MenuItem[]): MenuItem[] => {
  const result: MenuItem[] = []
  
  const flatten = (items: MenuItem[]) => {
    items.forEach(item => {
      if (item.path) {
        result.push(item)
      }
      if (item.children) {
        flatten(item.children)
      }
    })
  }
  
  flatten(menus)
  return result
}

const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = []
    return
  }
  
  const allMenus = flattenMenus(appStore.menuList)
  searchResults.value = allMenus.filter(item =>
    item.title.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
}

const handleSearchItemClick = (item: MenuItem) => {
  if (item.path) {
    tabsStore.addTab({
      name: item.path.replace(/\//g, '-').substring(1),
      title: item.title,
      path: item.path
    })
    router.push(item.path)
    showSearch.value = false
    searchKeyword.value = ''
    searchResults.value = []
  }
}
</script>

<style scoped>
.header {
  height: 64px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0,21,41,.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  font-size: 18px;
  color: #666;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.username {
  font-size: 14px;
  color: #333;
}

.search-results {
  margin-top: 16px;
  max-height: 300px;
  overflow-y: auto;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.search-item:hover {
  background-color: #f5f5f5;
}
</style>