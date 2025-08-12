<template>
  <template v-if="!menuItem.hidden">
    <el-sub-menu
      v-if="menuItem.children && menuItem.children.length > 0"
      :index="menuItem.id"
    >
      <template #title>
        <el-icon v-if="menuItem.icon">
          <component :is="menuItem.icon" />
        </el-icon>
        <span>{{ menuItem.title }}</span>
      </template>
      
      <template v-for="child in menuItem.children" :key="child.id">
        <SidebarItem :menu-item="child" />
      </template>
    </el-sub-menu>
    
    <el-menu-item
      v-else-if="menuItem.path"
      :index="menuItem.path"
      @click="handleMenuClick"
    >
      <el-icon v-if="menuItem.icon">
        <component :is="menuItem.icon" />
      </el-icon>
      <template #title>{{ menuItem.title }}</template>
    </el-menu-item>
  </template>
</template>

<script setup lang="ts">
import type { MenuItem } from '@/types'
import { useTabsStore } from '@/stores/tabs'
import { useRouter } from 'vue-router'

const props = defineProps({
  menuItem: {
    type: Object as () => MenuItem,
    required: true
  }
})

const tabsStore = useTabsStore()
const router = useRouter()

const handleMenuClick = () => {
  
  if (props.menuItem.path) {
    // 添加到标签页
    tabsStore.addTab({
      name: props.menuItem.path.replace(/\//g, '-').substring(1) || 'dashboard',
      title: props.menuItem.title,
      path: props.menuItem.path,
      closable: props.menuItem.closable || true,
    })
    
    // 路由跳转
    router.push(props.menuItem.path)
  }
}
</script>