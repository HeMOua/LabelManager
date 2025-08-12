<template>
  <div class="main-content">
    <router-view v-slot="{ Component }">
      <keep-alive>
        <component :is="Component" />
      </keep-alive>
    </router-view>
  </div>
</template>

<script setup lang="ts">
// 主内容区域
</script>

<style scoped>
.main-content {
  flex: 1;
  padding: 24px;
  background: #f0f2f5;
  overflow-y: auto;
  position: relative;
}
</style>