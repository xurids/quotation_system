<template>
  <div class="quotation-history">
    <el-card>
      <template #header>
        <div class="h-box">
          <span>报价单历史归档 (版本追踪)</span>
          <el-input v-model="q" placeholder="搜索报价单号/项目" style="width: 250px" clearable />
        </div>
      </template>
      
      <el-table :data="filteredList" border stripe v-loading="loading">
        <el-table-column prop="quotation_number" label="报价单号" width="180" />
        <el-table-column prop="title" label="报价标题" min-width="200" />
        <el-table-column label="项目" width="200">
          <template #default="{row}">{{ row.project?.name || '未知项目' }}</template>
        </el-table-column>
        <el-table-column label="客户" width="180">
          <template #default="{row}">{{ row.client?.company || '未关联' }}</template>
        </el-table-column>
        <el-table-column label="最终金额" width="150" align="right">
          <template #default="{row}">¥{{ row.total_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 }) }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{row}">
            <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{row}">
            <el-button type="primary" link @click="viewDetail(row)">历史版本</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { quotations } from '../api/quotation'
import { ElMessage } from 'element-plus'

const list = ref([])
const loading = ref(false)
const q = ref('')

const filteredList = computed(() => {
  if (!q.value) return list.value
  const query = q.value.toLowerCase()
  return list.value.filter(item => 
    item.quotation_number?.toLowerCase().includes(query) || 
    item.title?.toLowerCase().includes(query) ||
    item.project?.name?.toLowerCase().includes(query)
  )
})

const statusType = (status) => {
  const map = { draft: 'info', sent: 'primary', accepted: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const load = async () => {
  loading.value = true
  try {
    const res = await quotations.list()
    list.value = res.data?.data || []
  } catch (error) {
    ElMessage.error('加载报价历史失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (row) => {
  ElMessage.info('版本详情功能开发中...')
}

onMounted(load)
</script>

<style scoped>
.quotation-history { padding: 20px; }
.h-box { display: flex; justify-content: space-between; align-items: center; }
</style>
