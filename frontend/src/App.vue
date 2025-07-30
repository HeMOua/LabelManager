<template>
  <div id="app">
    <el-container class="app-container">
      <el-header class="app-header">
        <div class="header-content">
          <h1>图片管理工具</h1>
          <div class="header-actions">
            <project-selector />
          </div>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="250px" class="app-sidebar">
          <navigation-menu />
        </el-aside>
        
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import NavigationMenu from './components/NavigationMenu.vue'
import ProjectSelector from './components/ProjectSelector.vue'
</script>

<style scoped>
.app-container {
  height: 100vh;
}

.app-header {
  background-color: #409eff;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-content h1 {
  margin: 0;
  font-size: 24px;
}

.app-sidebar {
  background-color: #f5f7fa;
  border-right: 1px solid #dcdfe6;
}

.app-main {
  background-color: #ffffff;
  padding: 20px;
}
</style>