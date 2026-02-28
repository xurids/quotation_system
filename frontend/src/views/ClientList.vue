<template>
  <div class="client-manager">
    <el-card>
      <template #header>
        <div class="card-h">
          <span>客户档案库</span>
          <el-button type="primary" @click="openCreate">+ 新增客户</el-button>
        </div>
      </template>
      
      <el-table :data="list" border stripe v-loading="loading">
        <el-table-column prop="company" label="单位名称" min-width="200" />
        <el-table-column prop="name" label="主要联系人" width="120" />
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{row}">
            <el-button type="primary" link @click="onEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="onDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="visible" :title="form.id ? '编辑客户' : '新增客户'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="单位名称"><el-input v-model="form.company" placeholder="如：北京市经开区XX局" /></el-form-item>
        <el-form-item label="联系人"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="form.address" type="textarea" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="submit" :loading="submitting">提交保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { clients } from '../api/quotation'
import { ElMessage, ElMessageBox } from 'element-plus'

const list = ref([])
const loading = ref(false)
const submitting = ref(false)
const visible = ref(false)
const form = ref({ company: '', name: '', phone: '', email: '', address: '' })

const load = async () => {
  loading.value = true
  try {
    const res = await clients.list()
    list.value = res.data?.data || []
  } catch (error) {
    ElMessage.error('加载客户列表失败')
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  form.value = { company: '', name: '', phone: '', email: '', address: '' }
  visible.value = true
}

const onEdit = (row) => {
  form.value = { ...row }
  visible.value = true
}

const submit = async () => {
  submitting.value = true
  try {
    if (form.value.id) {
      await clients.update(form.value.id, form.value)
    } else {
      await clients.create(form.value)
    }
    ElMessage.success('操作成功')
    visible.value = false
    load()
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    submitting.value = false
  }
}

const onDelete = (id) => {
  ElMessageBox.confirm('确定删除此客户档案吗？', '提示', {
    type: 'warning'
  }).then(async () => {
    try {
      await clients.delete(id)
      ElMessage.success('删除成功')
      load()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

onMounted(load)
</script>

<style scoped>
.client-manager { padding: 20px; }
.card-h { display: flex; justify-content: space-between; align-items: center; }
</style>
