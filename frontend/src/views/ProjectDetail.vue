<template>
  <div class="pro-quotation">
    <!-- 顶部控制台 -->
    <header class="top-nav">
      <div class="h-left">
        <el-button icon="ArrowLeft" circle @click="router.push('/')" />
        <span class="p-name">{{ project.name || '项目加载中...' }}</span>
      </div>
      <div class="h-center">
        <div class="summary-box">
          <span class="lab">当前选中总报价:</span>
          <span class="val">¥ {{ formatPrice(calculatedTotals.grand) }}</span>
        </div>
      </div>
      <div class="h-right">
        <el-button type="success" icon="Upload" @click="importDialog.show()">导入库文件</el-button>
        <el-button type="primary" :loading="saving" @click="saveAndArchive">正式存档导出</el-button>
      </div>
    </header>

    <main class="main-body">
      <div class="toolbar">
        <el-input v-model="searchQuery" placeholder="全局搜索搜索系统、模块、功能..." prefix-icon="Search" style="width: 350px" />
        <el-button-group class="ml-20">
          <el-button @click="expandAll">全部展开</el-button>
          <el-button @click="collapseAll">全部折叠</el-button>
        </el-button-group>
        <el-checkbox v-model="hideUnselected" class="ml-20">仅看已选清单</el-checkbox>
      </div>

      <!-- 核心：深度驱动表格 -->
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
          <!-- 1. 业务层级结构 (合并复选框，确保原生缩进) -->
          <el-table-column prop="name" label="业务层级结构" min-width="350" show-overflow-tooltip>
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

          <el-table-column prop="description" label="功能说明" width="300" show-overflow-tooltip />

          <!-- 2. 多级编辑区 (全量开放修改) -->
          <el-table-column label="工作量" width="220" align="center">
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

          <el-table-column label="单价" width="220" align="center">
            <template #default="{row}">
              <el-input-number 
                v-if="!row.children || row.children.length === 0"
                v-model="row.unit_price" 
                :step="1000" 
                size="small" 
                controls-position="right"
                @change="onValChange(row)"
              />
            </template>
          </el-table-column>

          <el-table-column label="小计" width="160" align="right">
            <template #default="{row}">
              <span :class="['price-font', row.children && row.children.length > 0 ? 'p-agg' : 'p-leaf']">
                ¥ {{ formatPrice(row.total_price) }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </main>

    <footer class="footer-bar">
      <div class="f-info">已选项目: {{ calculatedTotals.count }} 项</div>
      <div class="f-prices">
        <span>开发费: ¥{{ formatPrice(calculatedTotals.dev) }}</span>
        <span>税费(6%): ¥{{ formatPrice(calculatedTotals.tax) }}</span>
        <span class="total">合同报价: ¥{{ formatPrice(calculatedTotals.grand) }}</span>
      </div>
    </footer>

    <excel-import-dialog ref="importDialog" :project-id="projectId" @import-success="fetchData" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { projects, expenses, quotations } from '../api/quotation'
import { ElMessage } from 'element-plus'
import ExcelImportDialog from '../components/ExcelImportDialog.vue'
import axios from 'axios'

const route = useRoute(); const router = useRouter()
const projectId = computed(() => parseInt(route.params.id))
const treeTable = ref(null); const importDialog = ref(null)

const project = ref({}); const treeData = ref([])
const searchQuery = ref(''); const hideUnselected = ref(false); const saving = ref(false)
const debouncedSearch = ref('')

// 原生防抖实现
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
    const [pRes, mRes] = await Promise.all([projects.get(projectId.value), expenses.getProjectSummary(projectId.value)])
    project.value = pRes.data?.data || pRes.data
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
        Object.assign(map[pid], { ...m, rowId: pid, depth: i, checked: false })
        delete map[pid].children
      } else {
        cur = map[pid].children
      }
    })
  })
  syncAggs(root); return root
}

const syncAggs = (nodes) => {
  let p = 0; nodes.forEach(n => {
    if (n.children && n.children.length > 0) { n.total_price = syncAggs(n.children) }
    else { n.total_price = (n.work_months || 0) * (n.unit_price || 0) }
    p += n.total_price
  })
  return p
}

// --- 勾选引擎优化 ---
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
  return { dev, tax: dev * 0.06, grand: dev * 1.06, count }
})

const onValChange = (row) => { 
  row.total_price = (row.work_months || 0) * (row.unit_price || 0)
  syncAggs(treeData.value)
}

// 优化后的过滤：避免不必要的递归和对象创建
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

const saveAndArchive = async () => {
  saving.value = true
  try {
    const ids = []
    const find = (nodes) => nodes.forEach(n => { if((!n.children || n.children.length === 0) && n.checked) ids.push(n.id); if(n.children) find(n.children) })
    find(treeData.value)
    if (ids.length === 0) return ElMessage.warning('请先勾选项目')
    const res = await axios.post(`/api/projects/${projectId.value}/export-excel`, ids, { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data])); const a = document.createElement('a'); a.href = url; a.download = `${project.value.name}_报价单.xlsx`; a.click()
  } catch (err) {
    ElMessage.error('导出失败')
  } finally {
    saving.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.pro-quotation { height: 100vh; display: flex; flex-direction: column; background: #f5f7fa; }
.top-nav { height: 64px; background: #1e222d; color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; }
.summary-box { background: rgba(255,255,255,0.1); padding: 8px 20px; border-radius: 4px; }
.summary-box .val { font-size: 20px; font-weight: bold; color: #ffcd00; margin-left: 10px; font-family: monospace; }

.main-body { flex: 1; padding: 15px; overflow: hidden; display: flex; flex-direction: column; gap: 10px; }
.toolbar { background: #fff; padding: 12px 20px; border-radius: 4px; display: flex; align-items: center; border: 1px solid #e2e8f0; }
.table-container { flex: 1; background: #fff; border-radius: 4px; overflow: hidden; border: 1px solid #e2e8f0; }

.name-wrapper { display: inline-block; vertical-align: middle; }
.header-wrapper { display: inline-block; vertical-align: middle; }
.mr-8 { margin-right: 8px; vertical-align: middle; }
.node-label { vertical-align: middle; }

/* 工业级层级视觉 */
:deep(.el-table__row.depth-0) { background: #f8fafc !important; font-weight: bold; }
:deep(.el-table__row.depth-1) { background: #fafbfc !important; font-weight: 600; }
:deep(.el-table__row.depth-2) { background: #ffffff !important; }

.price-font { font-family: monospace; font-size: 14px; }
.p-leaf { color: #f56c6c; font-weight: bold; }
.p-agg { color: #333; font-weight: 800; font-size: 15px; }

.edit-box { display: flex; align-items: center; gap: 5px; justify-content: center; }
.u { font-size: 11px; color: #999; }

.footer-bar { height: 50px; background: #fff; border-top: 1px solid #ddd; display: flex; align-items: center; justify-content: flex-end; padding: 0 30px; gap: 30px; }
.f-prices span { font-size: 14px; color: #666; margin-left: 20px; }
.f-prices .total { font-size: 18px; font-weight: bold; color: #f56c6c; }

:deep(.row-checked) { background-color: #f0f9ff !important; }
.ml-20 { margin-left: 20px; }
</style>
