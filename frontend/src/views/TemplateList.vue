<template>
  <div class="template-manager" style="padding: 30px;">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2 style="margin: 0;">标准报价模板库</h2>
          <el-button type="primary" disabled>+ 新增模板</el-button>
        </div>
      </template>
      
      <div v-loading="loading">
        <el-empty v-if="list.length === 0" description="暂无标准模板" />
        <el-row :gutter="20" v-else>
          <el-col v-for="tpl in list" :key="i" :span="6">
            <el-card shadow="hover" style="margin-bottom: 20px;">
              <h3>{{ tpl.name }}</h3>
              <p style="color: #909399; font-size: 13px;">{{ tpl.description || '预设政务概算层级' }}</p>
              <div style="margin-top: 15px; text-align: right;">
                <el-button type="primary" link @click="useTemplate(tpl)">引用此模板</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { templates } from '../api/quotation'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)

const load = async () => {
  loading.value = true
  try {
    const res = await templates.list()
    list.value = res.data?.data || []
  } catch (error) {
    ElMessage.error('加载模板失败')
  } finally {
    loading.value = false
  }
}

const useTemplate = (tpl) => {
  ElMessage.info('模板引用功能正在开发中，请使用 Excel 导入功能。')
}

onMounted(load)
</script>
