<template>
  <el-menu
    :default-active="$route.name"
    router
    class="navigation-menu"
  >
    <el-menu-item index="/">
      <el-icon><House /></el-icon>
      <span>首页</span>
    </el-menu-item>
    
    <el-menu-item index="/gallery">
      <el-icon><Picture /></el-icon>
      <span>图片库</span>
    </el-menu-item>
    
    <el-menu-item index="/tree">
      <el-icon><Operation /></el-icon>
      <span>树形浏览</span>
    </el-menu-item>
    
    <el-menu-item index="/tags">
      <el-icon><Collection /></el-icon>
      <span>标签管理</span>
    </el-menu-item>
    
    <el-menu-item index="/projects">
      <el-icon><Folder /></el-icon>
      <span>项目管理</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { defineComponent } from 'vue';

defineComponent({
  name: 'NavigationMenu'
});
</script>

<style scoped>
.navigation-menu {
  border-right: none;
  height: 100%;
}
</style>