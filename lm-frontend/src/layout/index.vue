<template>
  <div class="layout-container">
    <Sidebar />
    <div class="main-container" :class="{ 'collapsed': appStore.collapsed }">
      <Header />
      <TabsBar />
      <MainContent />
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from '@/layout/components/Sidebar.vue'
import Header from '@/layout/components/Header.vue'
import TabsBar from '@/layout/components/TabsBar.vue'
import MainContent from '@/layout/components/MainContent.vue'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  background-color: #f0f2f5;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 220px;
  transition: margin-left 0.3s ease;
}

.main-container.collapsed {
  margin-left: 64px;
}

@media (max-width: 768px) {
  .main-container {
    margin-left: 0;
  }
  
  .main-container.collapsed {
    margin-left: 0;
  }
}
</style>