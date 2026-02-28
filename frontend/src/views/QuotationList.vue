<template>
  <div class="quotation-history">
    <el-card>
      <template #header>
        <div class="header-box">
          <div class="h-left">
            <h2 class="title">报价版本管理</h2>
            <div class="search-bar">
              <el-input v-model="queryParams.q" placeholder="报价单号/标题" style="width: 220px" clearable @keyup.enter="handleSearch" />
              <el-select v-model="queryParams.status" placeholder="状态" style="width: 120px" clearable @change="handleSearch">
                <el-option label="草稿" value="draft" />
                <el-option label="已发送" value="sent" />
                <el-option label="已接受" value="accepted" />
                <el-option label="已拒绝" value="rejected" />
              </el-select>
              <el-button type="primary" icon="Search" @click="handleSearch">查询</el-button>
            </div>
          </div>
        </div>
      </template>
      
      <el-table :data="quotationList" border stripe v-loading="loading">
        <el-table-column prop="quotation_number" label="报价单号" width="180" />
        <el-table-column prop="title" label="报价标题" min-width="200" />
        <el-table-column label="关联项目" width="200">
          <template #default="{row}">
            <el-link type="primary" @click="router.push(`/project/${row.project_id}`)">{{ row.project?.name || '未知项目' }}</el-link>
          </template>
        </el-table-column>
        <el-table-column label="客户单位" width="200">
          <template #default="{row}">{{ row.client?.company || '未关联' }}</template>
        </el-table-column>
        <el-table-column label="金额详情" width="180" align="right">
          <template #default="{row}">
            <div class="amount-detail">
              <span class="total">¥{{ row.total_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 }) }}</span>
              <span class="sub">税:{{ (row.tax_rate*100).toFixed(0) }}% | 折:{{ (row.discount*10).toFixed(1) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{row}">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="最后更新" width="160">
          <template #default="{row}">{{ new Date(row.updated_at).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{row}">
            <el-button type="primary" link icon="Files" @click="showVersions(row)">历史版本</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.size"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="handleSearch"
          @current-change="load"
        />
      </div>
    </el-card>

    <!-- 版本列表抽屉 -->
    <el-drawer v-model="drawerVisible" :title="`报价版本历史 - ${activeQuotation.quotation_number}`" size="500px">
      <el-timeline v-if="versions.length > 0" class="version-timeline">
        <el-timeline-item
          v-for="(v, index) in versions"
          :key="v.id"
          :timestamp="new Date(v.created_at).toLocaleString()"
          :type="index === 0 ? 'primary' : ''"
        >
          <div class="v-card">
            <h4>版本 V{{ v.version_number }}</h4>
            <p class="remark">{{ v.changes }}</p>
            <div class="v-total">金额: ¥{{ v.total_amount?.toLocaleString(undefined, { minimumFractionDigits: 2 }) }}</div>
          </div>
        </el-timeline-item>
      </Timeline>
      <el-empty v-else description="暂无历史版本" />
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { quotations } from '../api/quotation'
import { ElMessage } from 'element-plus'

const router = useRouter()
const quotationList = ref([])
const loading = ref(false)
const total = ref(0)
const drawerVisible = ref(false)
const versions = ref([])
const activeQuotation = ref({})

const queryParams = reactive({
  q: '',
  status: '',
  page: 1,
  size: 10
})

const statusMap = {
  draft: { label: '草稿', type: 'info' },
  sent: { label: '已发送', type: 'primary' },
  accepted: { label: '已接受', type: 'success' },
  rejected: { label: '已拒绝', type: 'danger' }
}

const load = async () => {
  loading.value = true
  try {
    const res = await quotations.list(queryParams)
    const responseData = res.data?.data || {}
    quotationList.value = responseData.list || []
    total.value = responseData.length || 0
  } catch (error) {
    ElMessage.error('加载报价历史失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  queryParams.page = 1
  load()
}

const showVersions = async (row) => {
  activeQuotation.value = row
  drawerVisible.value = true
  try {
    const res = await quotations.getVersions(row.id)
    versions.value = res.data?.data || []
  } catch (err) {
    ElMessage.error('获取版本失败')
  }
}

onMounted(load)
</script>

<style scoped>
.quotation-history { padding: 24px; background: #f5f7fa; min-height: calc(100vh - 64px); }
.header-box { display: flex; justify-content: space-between; align-items: center; }
.h-left { display: flex; align-items: center; gap: 24px; }
.title { margin: 0; font-size: 20px; color: #303133; }
.search-bar { display: flex; gap: 12px; }
.amount-detail { display: flex; flex-direction: column; }
.amount-detail .total { font-weight: bold; color: #f56c6c; font-family: 'Courier New', Courier, monospace; }
.amount-detail .sub { font-size: 11px; color: #909399; margin-top: 2px; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }

.v-card { background: #f8f9fa; padding: 12px; border-radius: 4px; border-left: 4px solid #409eff; }
.v-card h4 { margin: 0 0 8px 0; color: #303133; }
.v-card .remark { font-size: 13px; color: #606266; margin-bottom: 8px; }
.v-card .v-total { font-weight: bold; color: #f56c6c; font-family: 'Courier New', Courier, monospace; font-size: 14px; }
.version-timeline { padding: 20px; }
</style>
