<template>
  <div class="report-page">
    <div class="report-header">
      <h2 class="report-title">报表查询</h2>
      <el-select
        v-model="selectedKey"
        placeholder="选择报表"
        class="template-select"
        @change="onTemplateChange"
      >
        <el-option
          v-for="t in templates"
          :key="t.key"
          :label="t.name"
          :value="t.key"
        />
      </el-select>
    </div>

    <!-- Step 1: Parameter form -->
    <div v-if="currentTemplate" class="report-card">
      <div class="card-section-title">
        1. 查询参数
        <span class="muted">{{ currentTemplate.description || '' }}</span>
      </div>
      <el-form :model="params" label-width="100px" :inline="true">
        <el-form-item
          v-for="p in currentTemplate.params_schema"
          :key="p.name"
          :label="p.label"
          :required="p.required"
        >
          <el-date-picker
            v-if="p.widget === 'date'"
            v-model="params[p.name]"
            type="date"
            value-format="YYYY-MM-DD"
            :placeholder="`选择${p.label}`"
            style="width: 160px;"
          />
          <el-select
            v-else-if="p.widget === 'select'"
            v-model="params[p.name]"
            clearable
            filterable
            :placeholder="`选择${p.label}`"
            style="width: 200px;"
          >
            <el-option
              v-for="opt in selectOptions[p.name] || []"
              :key="opt.id"
              :label="opt.label"
              :value="opt.id"
            />
          </el-select>
          <el-input
            v-else
            v-model="params[p.name]"
            :placeholder="`输入${p.label}`"
            style="width: 180px;"
          />
        </el-form-item>
      </el-form>
      <div class="action-row">
        <el-button type="primary" :loading="loading" @click="doQuery">查询</el-button>
        <el-button :disabled="!result" :loading="exporting" @click="doExport">导出 Excel</el-button>
      </div>
    </div>

    <!-- Step 2: Result -->
    <div v-if="result" class="report-card">
      <div class="card-section-title">
        2. 查询结果
        <el-tag type="info">共 {{ result.total }} 行</el-tag>
      </div>
      <el-table :data="result.rows" border size="small" max-height="540" stripe>
        <el-table-column
          v-for="col in result.columns"
          :key="col.key"
          :prop="col.key"
          :label="col.label"
          min-width="120"
          show-overflow-tooltip
        >
          <template #default="{ row }">{{ formatCell(row[col.key], col.type) }}</template>
        </el-table-column>
      </el-table>
      <el-pagination
        class="pager"
        background
        layout="prev, pager, next, sizes, total"
        :total="result.total"
        :current-page="result.page"
        :page-size="result.page_size"
        :page-sizes="[20, 50, 100, 200]"
        @current-change="onPageChange"
        @size-change="onSizeChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../api/request.js'

const templates = ref([])
const selectedKey = ref('')
const currentTemplate = computed(() =>
  templates.value.find(t => t.key === selectedKey.value) || null
)

const params = reactive({})
const selectOptions = reactive({})

const loading = ref(false)
const exporting = ref(false)
const result = ref(null)

async function fetchTemplates() {
  templates.value = await request.get('/api/report/templates')
  if (templates.value.length > 0 && !selectedKey.value) {
    selectedKey.value = templates.value[0].key
    await primeTemplate()
  }
}

function onTemplateChange() {
  result.value = null
  for (const k of Object.keys(params)) delete params[k]
  for (const k of Object.keys(selectOptions)) delete selectOptions[k]
  primeTemplate()
}

async function primeTemplate() {
  if (!currentTemplate.value) return
  for (const p of currentTemplate.value.params_schema) {
    params[p.name] = p.default ?? null
    if (p.widget === 'select' && p.options_api) {
      try {
        selectOptions[p.name] = await request.get(p.options_api)
      } catch {
        selectOptions[p.name] = []
      }
    }
  }
}

async function doQuery(page = 1, pageSize = null) {
  if (!currentTemplate.value) return
  loading.value = true
  try {
    result.value = await request.post(
      `/api/report/${currentTemplate.value.key}/execute`,
      {
        params: cleanParams(),
        page,
        page_size: pageSize ?? result.value?.page_size ?? 50,
      },
    )
  } finally {
    loading.value = false
  }
}

function cleanParams() {
  const out = {}
  for (const [k, v] of Object.entries(params)) {
    if (v !== null && v !== undefined && v !== '') out[k] = v
  }
  return out
}

function onPageChange(page) {
  doQuery(page)
}
function onSizeChange(size) {
  doQuery(1, size)
}

async function doExport() {
  if (!currentTemplate.value) return
  exporting.value = true
  try {
    const blob = await request.post(
      `/api/report/${currentTemplate.value.key}/export`,
      { params: cleanParams() },
      { responseType: 'blob' },
    )
    triggerDownload(blob, `${currentTemplate.value.name}.xlsx`)
    ElMessage.success('导出成功')
  } finally {
    exporting.value = false
  }
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function formatCell(value, type) {
  if (value === null || value === undefined || value === '') return '-'
  if (type === 'datetime' && typeof value === 'string') return value.replace('T', ' ').slice(0, 19)
  return value
}

onMounted(fetchTemplates)
</script>

<style scoped>
.report-page { font-family: 'DM Sans', 'Noto Serif SC', sans-serif; }

.report-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.report-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px; font-weight: 600; color: #0a1628; margin: 0;
}
.template-select { width: 240px; }

.report-card {
  background: #fff; border-radius: 12px; padding: 20px;
  border: 1px solid rgba(10, 22, 40, 0.05); margin-bottom: 20px;
}
.card-section-title {
  font-weight: 600; color: #0a1628; margin-bottom: 14px;
  display: flex; align-items: center; gap: 12px;
}
.muted { color: #909399; font-size: 12px; font-weight: 400; }

.action-row {
  margin-top: 8px; display: flex; align-items: center; gap: 12px;
}

.pager { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
