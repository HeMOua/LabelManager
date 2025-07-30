<template>
  <div class="home">
    <el-card>
      <h2>欢迎使用图片管理工具</h2>
      <p>这是一个支持多维度标签和树形结构展示的图片管理系统。</p>
      
      <div class="features">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="feature-item">
                <el-icon size="32" color="#409eff"><Picture /></el-icon>
                <h3>图片管理</h3>
                <p>支持批量上传、缩略图生成、元数据管理</p>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="feature-item">
                <el-icon size="32" color="#67c23a"><Collection /></el-icon>
                <h3>标签系统</h3>
                <p>多维度标签分类，支持颜色、材质、用途等</p>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover">
              <div class="feature-item">
                <el-icon size="32" color="#e6a23c"><Operation /></el-icon>
                <h3>树形展示</h3>
                <p>根据标签维度生成树形结构浏览</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <div class="quick-actions">
        <h3>快速操作</h3>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-button type="primary" @click="$router.push('/gallery')">
              <el-icon><Picture /></el-icon>
              图片库
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="success" @click="$router.push('/tree')">
              <el-icon><Operation /></el-icon>
              树形浏览
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="warning" @click="$router.push('/tags')">
              <el-icon><Collection /></el-icon>
              标签管理
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="info" @click="$router.push('/projects')">
              <el-icon><Folder /></el-icon>
              项目管理
            </el-button>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.features {
  margin: 30px 0;
}

.feature-item {
  text-align: center;
  padding: 20px;
}

.feature-item h3 {
  margin: 15px 0 10px;
  color: #333;
}

.feature-item p {
  color: #666;
  font-size: 14px;
}

.quick-actions {
  margin-top: 40px;
}

.quick-actions h3 {
  margin-bottom: 20px;
}

.quick-actions .el-button {
  width: 100%;
  height: 60px;
  font-size: 16px;
}
</style>