<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">审计日志</h2>
    </div>

    <div class="card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="用户名">
          <el-input v-model="filters.username" clearable placeholder="精确匹配" style="width: 150px;" />
        </el-form-item>
        <el-form-item label="动作">
          <el-select v-model="filters.action" clearable placeholder="全部" style="width: 180px;">
            <el-option v-for="a in ACTIONS" :key="a.value" :label="a.label" :value="a.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            start-placeholder="开始"
            end-placeholder="结束"
            style="width: 240px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="query(1)">查询</el-button>
          <el-button @click="reset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="rows" border size="small" max-height="560" v-loading="loading">
        <el-table-column type="expand">
          <template #default="{ row }">
            <pre class="detail-json">{{ pretty(row.detail) }}</pre>
          </template>
        </el-table-column>
        <el-table-column prop="id" label="#" width="70" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">{{ fmtTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="action" label="动作" width="160">
          <template #default="{ row }">
            <el-tag size="small" :type="actionType(row.action)">{{ actionLabel(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="target_type" label="对象类型" width="150" />
        <el-table-column prop="target_id" label="对象ID" width="90" />
        <el-table-column prop="ip" label="IP" min-width="120" />
      </el-table>

      <el-pagination
        class="pager"
        background
        layout="prev, pager, next, total"
        :total="total"
        :current-page="page"
        :page-size="pageSize"
        @current-change="query"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '../../api/request.js'

const ACTIONS = [
  { value: 'login', label: '登录', type: 'info' },
  { value: 'dict.create', label: '字典新增', type: 'success' },
  { value: 'dict.update', label: '字典修改', type: 'warning' },
  { value: 'dict.delete', label: '字典删除', type: 'danger' },
  { value: 'import.commit_warn', label: '强制入库', type: 'danger' },
  { value: 'user.create', label: '新建用户', type: 'success' },
  { value: 'user.update', label: '修改用户', type: 'warning' },
  { value: 'user.reset_password', label: '重置密码', type: 'danger' },
]
const actionMap = Object.fromEntries(ACTIONS.map(a => [a.value, a]))
const actionLabel = (a) => actionMap[a]?.label || a
const actionType = (a) => actionMap[a]?.type || ''

const filters = reactive({ username: '', action: '' })
const dateRange = ref(null)
const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

async function query(p = 1) {
  page.value = p
  loading.value = true
  try {
    const params = { page: p, page_size: pageSize.value }
    if (filters.username) params.username = filters.username
    if (filters.action) params.action = filters.action
    if (dateRange.value?.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const data = await request.get('/api/audit/logs', { params })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function reset() {
  filters.username = ''
  filters.action = ''
  dateRange.value = null
  query(1)
}

function pretty(obj) {
  try { return JSON.stringify(obj, null, 2) } catch { return String(obj) }
}
function fmtTime(t) {
  return t ? t.replace('T', ' ').slice(0, 19) : '-'
}

onMounted(() => query(1))
</script>

<style scoped>
.page { font-family: 'DM Sans', 'Noto Serif SC', sans-serif; }
.page-header { margin-bottom: 20px; }
.page-title { font-family: 'Noto Serif SC', serif; font-size: 20px; font-weight: 600; color: #0a1628; margin: 0; }
.card { background: #fff; border-radius: 12px; padding: 20px; border: 1px solid rgba(10, 22, 40, 0.05); }
.filter-form { margin-bottom: 8px; }
.detail-json {
  margin: 0; padding: 12px 16px; background: #f6f4f0; border-radius: 8px;
  font-size: 12px; color: #303133; white-space: pre-wrap; word-break: break-all;
}
.pager { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
