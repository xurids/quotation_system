<template>
  <el-dialog v-model="visible" title="导入Excel功能模块" width="500px">
    <el-upload
      drag
      :action="`/api/imports/import-excel?project_id=${projectId}`"
      accept=".xlsx,.xls"
      @success="onSuccess"
      @error="onError"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">拖拽或点击上传Excel</div>
    </el-upload>
  </el-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
const props = defineProps(['projectId'])
const emit = defineEmits(['import-success'])
const visible = ref(false)
const show = () => visible.value = true
const onSuccess = (res) => {
  if (res.code === 0) {
    ElMessage.success(res.message)
    visible.value = false
    emit('import-success')
  } else ElMessage.error(res.message)
}
const onError = () => ElMessage.error('上传失败')
defineExpose({ show })
</script>
