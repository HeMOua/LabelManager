<template>
  <div class="sidebar" :class="{ 'collapsed': appStore.collapsed }">
    <div class="logo">
      <span v-if="!appStore.collapsed" >
        <img src="/logo.png" alt="Logo"/>
      </span>
      <img v-else src="/logo-mini.png" alt="Logo"/>
    </div>
    
    <el-menu
      :default-active="$route.path"
      :collapse="appStore.collapsed"
      :unique-opened="true"
      router
      class="sidebar-menu"
    >
      <template v-for="item in appStore.menuList" :key="item.id">
        <SidebarItem :menu-item="item" />
      </template>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { defineComponent } from 'vue'
import SidebarItem from './SidebarItem.vue'
import { useAppStore } from '@/stores/app'

defineComponent({
  name: 'SidebarComponent'
})

const appStore = useAppStore()
</script>

<style scoped>
.sidebar {
  width: 220px;
  height: 100vh;
  background-color: #001529;
  position: fixed;
  left: 0;
  top: 0;
  transition: width 0.3s ease;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 64px;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #1f2937;
}

.logo img {
  height: 32px;
  margin-right: 8px;
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.85);
  border-bottom: none;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: #1f2937;
  color: white;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #1890ff;
  color: white;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item) {
  background-color: #0c1222;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item:hover) {
  background-color: #1f2937;
}

.sidebar-menu :deep(.el-sub-menu .el-menu-item.is-active) {
  background-color: #1890ff;
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }
  
  .sidebar.collapsed {
    transform: translateX(0);
    width: 64px;
  }
}
</style>