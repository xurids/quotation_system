<template>
  <el-container class="app-wrapper">
    <!-- 左侧：全局深色导航 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon size="24"><Platform /></el-icon>
        <span>政务报价专家</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#1e222d"
        text-color="#b1b3b8"
        active-text-color="#409eff"
        router
      >
        <el-menu-item index="/">
          <el-icon><Fold /></el-icon>
          <span>项目中心</span>
        </el-menu-item>
        <el-menu-item index="/quotations">
          <el-icon><Document /></el-icon>
          <span>报价管理</span>
        </el-menu-item>
        <el-menu-item index="/clients">
          <el-icon><User /></el-icon>
          <span>客户档案</span>
        </el-menu-item>
        <el-menu-item index="/templates">
          <el-icon><Files /></el-icon>
          <span>标准库模板</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <router-view />
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-wrapper { height: 100vh; background: #f0f2f5; }
.sidebar { background: #1e222d; color: #fff; border-right: none; }
.logo { height: 60px; display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: bold; font-size: 16px; border-bottom: 1px solid #2d323d; }
.main-container { flex-direction: column; overflow: hidden; }
:deep(.el-menu) { border-right: none; }
</style>
