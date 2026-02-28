<template>
  <div class="home-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2 class="title">项目预算报价管理</h2>
            <div class="search-bar">
              <el-input v-model="queryParams.q" placeholder="项目名称/代码" style="width: 200px" clearable @keyup.enter="handleSearch" />
              <el-select v-model="queryParams.status" placeholder="项目状态" style="width: 150px" clearable @change="handleSearch">
                <el-option label="草稿" value="draft" />
                <el-option label="审核中" value="auditing" />
                <el-option label="已批准" value="approved" />
                <el-option label="已结项" value="closed" />
              </el-select>
              <el-button type="primary" icon="Search" @click="handleSearch">查询</el-button>
            </div>
          </div>
          <el-button type="primary" icon="Plus" @click="dialogVisible = true">新建项目</el-button>
        </div>
      </template>

      <el-table :data="projectList" border stripe v-loading="loading">
        <el-table-column prop="code" label="项目代码" width="160" />
        <el-table-column prop="name" label="项目名称" min-width="200" />
        <el-table-column prop="client_name" label="客户单位" width="180" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{row}">
            <el-tag :type="statusMap[row.status]?.type">{{ statusMap[row.status]?.label }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="预算总额" width="150" align="right">
          <template #default="{row}">
            <span class="price-text">¥{{ (row.total_budget || 0).toLocaleString(undefined, { minimumFractionDigits: 2 }) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{row}">{{ new Date(row.created_at).toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{row}">
            <el-button type="primary" link icon="Monitor" @click="router.push(`/project/${row.id}`)">工作台</el-button>
            <el-divider direction="vertical" />
            <el-button type="danger" link icon="Delete" @click="onDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.size"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="创建新项目" width="500px">
      <el-form :model="form" label-width="100px" ref="formRef" :rules="rules">
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入项目全称" />
        </el-form-item>
        <el-form-item label="项目代码" prop="code">
          <el-input v-model="form.code" placeholder="留空则自动生成" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="onCreate" :loading="creating">确定创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { projects } from '../api/quotation'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const projectList = ref([])
const total = ref(0)
const loading = ref(false)
const creating = ref(false)
const dialogVisible = ref(false)

const queryParams = reactive({
  q: '',
  status: '',
  page: 1,
  size: 10
})

const form = ref({ name: '', code: '' })
const rules = {
  name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }]
}

const statusMap = {
  draft: { label: '草稿', type: 'info' },
  auditing: { label: '审核中', type: 'warning' },
  approved: { label: '已批准', type: 'success' },
  closed: { label: '已结项', type: 'danger' }
}

const loadList = async () => {
  loading.value = true
  try {
    const res = await projects.list(queryParams)
    // 适配新的响应结构: data.list 和 data.length
    const responseData = res.data?.data || {}
    projectList.value = responseData.list || []
    total.value = responseData.length || 0
  } catch (error) {
    ElMessage.error('加载项目列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  queryParams.page = 1
  loadList()
}

const handleSizeChange = (val) => {
  queryParams.size = val
  loadList()
}

const handleCurrentChange = (val) => {
  queryParams.page = val
  loadList()
}

const onCreate = async () => {
  creating.value = true
  try {
    const res = await projects.create(form.value)
    ElMessage.success('项目创建成功')
    dialogVisible.value = false
    router.push(`/project/${res.data.data.id}`)
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const onDelete = (id) => {
  ElMessageBox.confirm('确定删除该项目及其所有预算数据吗？', '严重警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await projects.delete(id)
    ElMessage.success('项目已删除')
    loadList()
  }).catch(() => {})
}

onMounted(loadList)
</script>

<style scoped>
.home-container { padding: 24px; background: #f5f7fa; min-height: calc(100vh - 64px); }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; gap: 24px; }
.title { margin: 0; font-size: 20px; color: #303133; }
.search-bar { display: flex; gap: 12px; }
.price-text { font-family: 'Courier New', Courier, monospace; font-weight: bold; color: #f56c6c; }
.pagination-container { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
