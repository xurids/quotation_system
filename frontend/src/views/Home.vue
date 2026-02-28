<template>
  <div style="padding: 40px; background: #f5f7fa; min-height: 100vh;">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2 style="margin: 0;">项目报价管理系统</h2>
          <el-button type="primary" @click="dialogVisible = true">+ 新建报价项目</el-button>
        </div>
      </template>
      <el-table :data="projectList" border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" />
        <el-table-column prop="code" label="项目代码" width="150" />
        <el-table-column label="总预算" width="150">
          <template #default="{row}">¥{{ row.total_budget?.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="操作" width="180">
          <template #default="{row}">
            <el-button type="primary" link @click="router.push(`/project/${row.id}`)">进入工作台</el-button>
            <el-button type="danger" link @click="onDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="创建新项目" width="400px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="项目名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="代码"><el-input v-model="form.code" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="onCreate">确定创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { projects } from '../api/quotation'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const projectList = ref([])
const dialogVisible = ref(false)
const form = ref({ name: '', code: '' })

const loadList = async () => {
  const res = await projects.list()
  projectList.value = res.data?.data || []
}

const onCreate = async () => {
  await projects.create(form.value)
  ElMessage.success('创建成功')
  dialogVisible.value = false
  loadList()
}

const onDelete = (id) => {
  ElMessageBox.confirm('确定删除吗？').then(async () => {
    await projects.delete(id)
    loadList()
  })
}

onMounted(loadList)
</script>
