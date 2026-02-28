<template>
  <div class="pro-quotation">
    <!-- 顶部控制台 -->
    <header class="top-nav">
      <div class="h-left">
        <el-button icon="ArrowLeft" circle @click="router.push('/')" />
        <el-input v-model="project.name" class="p-name-input" placeholder="项目名称" @blur="updateProjectMeta" />
        <el-tag :type="statusMap[project.status || 'draft']?.type" class="ml-10">
          {{ statusMap[project.status || 'draft']?.label }}
        </el-tag>
      </div>
      
      <div class="h-center">
        <div class="summary-box">
          <span class="lab">当前选中总报价:</span>
          <span class="val">¥ {{ formatPrice(calculatedTotals.grand) }}</span>
        </div>
      </div>

      <div class="h-right">
        <el-dropdown @command="handleStatusChange" class="mr-10">
          <el-button type="info">项目状态: {{ statusMap[project.status]?.label }}<el-icon class="el-icon--right"><arrow-down /></el-icon></el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="draft">设为草稿</el-dropdown-item>
              <el-dropdown-item command="auditing">提交审核</el-dropdown-item>
              <el-dropdown-item command="approved">标记批准</el-dropdown-item>
              <el-dropdown-item command="closed">项目结项</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="success" icon="Upload" @click="importDialog.show()">导入库文件</el-button>
        <el-button type="warning" icon="DocumentChecked" :loading="saving" @click="saveDraft">保存草稿</el-button>
        <el-button type="primary" :loading="saving" @click="saveAndArchive">正式存档导出</el-button>
      </div>
    </header>

    <main class="main-body">
      <div class="toolbar">
        <div class="t-left">
          <el-input v-model="searchQuery" placeholder="搜索功能..." prefix-icon="Search" style="width: 250px" />
          <el-button-group class="ml-20">
            <el-button @click="expandAll">全部展开</el-button>
            <el-button @click="collapseAll">全部折叠</el-button>
          </el-button-group>
          <el-checkbox v-model="hideUnselected" class="ml-20">仅看已选清单</el-checkbox>
        </div>

        <div class="t-right">
          <div class="config-item">
            <span class="label">关联客户:</span>
            <el-select v-model="project.client_id" placeholder="关联客户" style="width: 180px" @change="updateProjectMeta" clearable>
              <el-option v-for="c in clientList" :key="c.id" :label="c.company" :value="c.id" />
            </el-select>
          </div>
          <div class="config-item">
            <span class="label">税率:</span>
            <el-input-number v-model="project.tax_rate" :precision="2" :step="0.01" :min="0" :max="1" size="small" style="width: 100px" @change="updateProjectMeta" />
          </div>
          <div class="config-item">
            <span class="label">折扣:</span>
            <el-input-number v-model="project.discount" :precision="2" :step="0.05" :min="0" :max="2" size="small" style="width: 100px" @change="updateProjectMeta" />
          </div>
        </div>
      </div>

      <div class="table-container">
        <el-table
          ref="treeTable"
          :data="filteredTreeData"
          row-key="rowId"
          border
          height="100%"
          :indent="24"
          default-expand-all
          :row-class-name="tableRowClassName"
        >
          <el-table-column prop="name" label="业务层级结构" min-width="300" show-overflow-tooltip>
            <template #default="{row}">
              <span class="name-wrapper">
                <el-checkbox 
                  :model-value="row.checked" 
                  :indeterminate="row.indeterminate"
                  @change="(val) => handleRowCheck(row, val)" 
                  class="mr-8"
                />
                <span :class="['node-label', `depth-${row.depth}`]">{{ row.name }}</span>
              </span>
            </template>
            <template #header>
              <span class="header-wrapper">
                <el-checkbox :model-value="isAllChecked" :indeterminate="isIndeterminate" @change="handleCheckAll" class="mr-8" />
                <span>业务层级结构</span>
              </span>
            </template>
          </el-table-column>

          <el-table-column prop="description" label="功能说明" width="250" show-overflow-tooltip />

          <el-table-column label="工作量" width="180" align="center">
            <template #default="{row}">
              <div v-if="!row.children || row.children.length === 0" class="edit-box">
                <el-input-number 
                  v-model="row.work_months" 
                  :precision="2" :step="0.1" 
                  size="small" 
                  controls-position="right"
                  @change="onValChange(row)"
                />
                <span class="u">人月</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column label="单价" width="180" align="center">
            <template #default="{row}">
              <div v-if="!row.children || row.children.length === 0" class="edit-box">
                <span class="u">¥</span>
                <el-input-number 
                  v-model="row.unit_price" 
                  :step="1000" 
                  size="small" 
                  controls-position="right"
                  @change="onValChange(row)"
                />
              </div>
            </template>
          </el-table-column>

          <el-table-column label="小计" width="150" align="right">
            <template #default="{row}">
              <span :class="['price-font', row.children && row.children.length > 0 ? 'p-agg' : 'p-leaf']">
                ¥{{ formatPrice(row.total_price) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </main>

    <footer class="footer-bar">
      <div class="f-info">已选项目: <b class="highlight">{{ calculatedTotals.count }}</b> 项</div>
      <div class="f-prices">
        <div class="price-item">
          <span class="label">研发费用:</span>
          <span class="val">¥{{ formatPrice(calculatedTotals.dev) }}</span>
        </div>
        <div class="price-item">
          <span class="label">税费 ({{ (project.tax_rate * 100).toFixed(0) }}%):</span>
          <span class="val">¥{{ formatPrice(calculatedTotals.tax) }}</span>
        </div>
        <div class="price-item" v-if="project.discount < 1">
          <span class="label">折扣 ({{ (project.discount * 10).toFixed(1) }}折):</span>
          <span class="val">- ¥{{ formatPrice(calculatedTotals.discountAmount) }}</span>
        </div>
        <div class="price-item total">
          <span class="label">合同总价:</span>
          <span class="val">¥{{ formatPrice(calculatedTotals.grand) }}</span>
        </div>
      </div>
    </footer>

    <excel-import-dialog ref="importDialog" :project-id="projectId" @import-success="fetchData" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { projects, expenses, quotations, clients } from '../api/quotation'
import { ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import ExcelImportDialog from '../components/ExcelImportDialog.vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => parseInt(route.params.id))
const treeTable = ref(null)
const importDialog = ref(null)

const project = ref({ name: '', status: 'draft', tax_rate: 0.06, discount: 1.0 })
const treeData = ref([])
const clientList = ref([])
const searchQuery = ref('')
const hideUnselected = ref(false)
const saving = ref(false)
const debouncedSearch = ref('')

const statusMap = {
  draft: { label: '草稿', type: 'info' },
  auditing: { label: '审核中', type: 'warning' },
  approved: { label: '已批准', type: 'success' },
  closed: { label: '已结项', type: 'danger' }
}

let searchTimer = null
watch(searchQuery, (v) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    debouncedSearch.value = v
  }, 300)
})

const formatPrice = (v) => (v || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fetchData = async () => {
  try {
    const [pRes, mRes, cRes] = await Promise.all([
      projects.get(projectId.value),
      expenses.getProjectSummary(projectId.value),
      clients.list()
    ])
    project.value = pRes.data?.data || pRes.data
    clientList.value = cRes.data?.data || []
    const all = []
    const data = mRes.data?.data || mRes.data
    if (data.categories) data.categories.forEach(c => all.push(...(c.modules || [])))
    treeData.value = buildTree(all)
  } catch (err) {
    ElMessage.error('获取项目数据失败')
  }
}

const buildTree = (list) => {
  const root = []; const map = {}
  list.forEach(m => {
    const path = [m.system_name, m.subsystem_name, m.level1, m.level2, m.level3].filter(v => v)
    let cur = root; let pid = ""
    path.forEach((name, i) => {
      pid += (pid ? '||' : '') + name
      if (!map[pid]) {
        map[pid] = { 
          rowId: pid, name, children: [], depth: i, 
          total_price: 0, work_months: 0, unit_price: 15000,
          checked: false, indeterminate: false
        }
        cur.push(map[pid])
      }
      if (i === path.length - 1) {
        Object.assign(map[pid], { 
          ...m, rowId: pid, depth: i, 
          checked: m.checked || false,
          unit_price: m.unit_price || 15000 
        })
        delete map[pid].children
      } else {
        cur = map[pid].children
      }
    })
  })
  syncAggs(root)
  syncParentCheck(root)
  return root
}

const syncAggs = (nodes) => {
  let p = 0; nodes.forEach(n => {
    if (n.children && n.children.length > 0) { n.total_price = syncAggs(n.children) }
    else { n.total_price = (n.work_months || 0) * (n.unit_price || 0) }
    p += n.total_price
  })
  return p
}

const handleRowCheck = (row, val) => {
  row.checked = val; row.indeterminate = false
  const walkDown = (node, state) => {
    if (node.children) node.children.forEach(c => { c.checked = state; c.indeterminate = false; walkDown(c, state) })
  }
  walkDown(row, val)
  syncParentCheck(treeData.value)
}

const syncParentCheck = (nodes) => {
  nodes.forEach(n => {
    if (n.children && n.children.length > 0) {
      syncParentCheck(n.children)
      const allC = n.children.every(c => c.checked)
      const noneC = n.children.every(c => !c.checked && !c.indeterminate)
      n.checked = allC
      n.indeterminate = !allC && !noneC
    }
  })
}

const handleCheckAll = (val) => {
  const walk = (nodes) => nodes.forEach(n => { n.checked = val; n.indeterminate = false; if(n.children) walk(n.children) })
  walk(treeData.value)
}

const isAllChecked = computed(() => treeData.value.length > 0 && treeData.value.every(n => n.checked))
const isIndeterminate = computed(() => !isAllChecked.value && treeData.value.some(n => n.checked || n.indeterminate))

const calculatedTotals = computed(() => {
  let dev = 0; let count = 0
  const walk = (nodes) => nodes.forEach(n => {
    if (!n.children || n.children.length === 0) { if (n.checked) { dev += n.total_price; count++ } }
    else walk(n.children)
  })
  walk(treeData.value)
  const tax = dev * (project.value.tax_rate || 0.06)
  const subTotal = dev + tax
  const grand = subTotal * (project.value.discount || 1.0)
  return { 
    dev, 
    tax, 
    discountAmount: subTotal - grand,
    grand, 
    count 
  }
})

const onValChange = (row) => { 
  row.total_price = (row.work_months || 0) * (row.unit_price || 0)
  syncAggs(treeData.value)
}

const filteredTreeData = computed(() => {
  const q = debouncedSearch.value.toLowerCase()
  const hide = hideUnselected.value
  if (!q && !hide) return treeData.value

  const filterNodes = (nodes) => {
    const res = []
    nodes.forEach(n => {
      const isMatch = n.name.toLowerCase().includes(q) || (n.description || '').toLowerCase().includes(q)
      const isSelected = n.checked || n.indeterminate
      if (hide && !isSelected) return
      if (n.children && n.children.length > 0) {
        const filteredChildren = filterNodes(n.children)
        if (filteredChildren.length > 0 || isMatch) {
          res.push({ ...n, children: filteredChildren })
        }
      } else if (isMatch) {
        res.push(n)
      }
    })
    return res
  }
  return filterNodes(treeData.value)
})

const tableRowClassName = ({ row }) => {
  let cls = [`depth-${row.depth || 0}`]
  if (row.checked) cls.push('row-checked')
  return cls.join(' ')
}

const expandAll = () => {
  const walk = (nodes) => nodes.forEach(n => {
    treeTable.value.toggleRowExpansion(n, true)
    if (n.children) walk(n.children)
  })
  walk(filteredTreeData.value)
}

const collapseAll = () => {
  const walk = (nodes) => nodes.forEach(n => {
    treeTable.value.toggleRowExpansion(n, false)
    if (n.children) walk(n.children)
  })
  walk(filteredTreeData.value)
}

const updateProjectMeta = async () => {
  try {
    await projects.update(projectId.value, { 
      name: project.value.name,
      client_id: project.value.client_id,
      status: project.value.status,
      tax_rate: project.value.tax_rate,
      discount: project.value.discount
    })
    ElMessage.success('项目信息已同步')
  } catch (err) {
    ElMessage.error('项目信息同步失败')
  }
}
const handleStatusChange = async (cmd) => {
  project.value.status = cmd
  await updateProjectMeta()
  ElMessage.success(`项目状态已更新为: ${statusMap[cmd].label}`)
}

const saveDraft = async () => {
  saving.value = true
  try {
    const modules = []
    const find = (nodes) => nodes.forEach(n => {
      if (!n.children || n.children.length === 0) {
        modules.push({ id: n.id, work_months: n.work_months, unit_price: n.unit_price, checked: n.checked })
      } else find(n.children)
    })
    find(treeData.value)
    await expenses.batchUpdate(projectId.value, modules)
    ElMessage.success('预算草稿已保存')
    fetchData()
  } catch (err) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const saveAndArchive = async () => {
  saving.value = true
  try {
    await saveDraft()
    await quotations.createVersion(projectId.value, {
      total_amount: calculatedTotals.value.grand,
      client_id: project.value.client_id,
      tax_rate: project.value.tax_rate,
      discount: project.value.discount,
      remark: '导出快照存档'
    })
    
    const ids = []
    const getChecked = (nodes) => nodes.forEach(n => {
      if (!n.children && n.checked) ids.push(n.id)
      else if(n.children) getChecked(n.children)
    })
    getChecked(treeData.value)
    
    const res = await axios.post(`/api/projects/${projectId.value}/export-excel`, ids, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `${project.value.name}_报价单_${new Date().toLocaleDateString()}.xlsx`
    a.click()
    ElMessage.success('版本已存档并导出')
  } catch (err) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.pro-quotation { height: 100vh; display: flex; flex-direction: column; background: #f5f7fa; }
.top-nav { height: 64px; background: #1e222d; color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); z-index: 10; }
.p-name-input { width: 300px; margin-left: 15px; }
:deep(.p-name-input .el-input__wrapper) { background: rgba(255,255,255,0.1); box-shadow: none; border: 1px solid rgba(255,255,255,0.2); }
:deep(.p-name-input .el-input__inner) { color: #fff; font-size: 18px; font-weight: bold; }
.summary-box { background: rgba(255,255,255,0.1); padding: 8px 25px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.1); }
.summary-box .val { font-size: 22px; font-weight: bold; color: #ffcd00; margin-left: 10px; font-family: 'Courier New', Courier, monospace; }

.main-body { flex: 1; padding: 16px; overflow: hidden; display: flex; flex-direction: column; gap: 12px; }
.toolbar { background: #fff; padding: 12px 20px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #e2e8f0; }
.t-right { display: flex; gap: 24px; }
.config-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #606266; }

.table-container { flex: 1; background: #fff; border-radius: 4px; overflow: hidden; border: 1px solid #e2e8f0; }

.edit-box { display: flex; align-items: center; gap: 6px; justify-content: center; }
.u { font-size: 12px; color: #909399; }

.footer-bar { height: 70px; background: #fff; border-top: 1px solid #dcdfe6; display: flex; align-items: center; justify-content: space-between; padding: 0 32px; box-shadow: 0 -2px 10px rgba(0,0,0,0.05); }
.highlight { color: #409eff; font-size: 18px; }
.f-prices { display: flex; align-items: flex-end; gap: 40px; }
.price-item { display: flex; flex-direction: column; align-items: flex-end; }
.price-item .label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.price-item .val { font-size: 16px; font-family: 'Courier New', Courier, monospace; font-weight: 600; }
.price-item.total .val { font-size: 24px; color: #f56c6c; }

:deep(.el-table__row.depth-0) { background: #f8fafc !important; font-weight: bold; }
:deep(.el-table__row.depth-1) { background: #fafbfc !important; font-weight: 600; }
:deep(.row-checked) { background-color: #f0f9ff !important; }
.ml-10 { margin-left: 10px; }
.ml-20 { margin-left: 20px; }
.mr-10 { margin-right: 10px; }
.price-font { font-family: 'Courier New', Courier, monospace; }
</style>
