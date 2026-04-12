<template>
  <div class="dict-page">
    <!-- Header bar -->
    <div class="dict-header">
      <h2 class="dict-title">{{ config.title }}</h2>
      <div class="dict-actions">
        <el-input
          v-model="keyword"
          placeholder="搜索..."
          clearable
          class="search-input"
          @input="debouncedSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" class="add-btn" @click="openDialog(null)">
          <el-icon><Plus /></el-icon>新增
        </el-button>
      </div>
    </div>

    <!-- Table -->
    <div class="dict-table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        class="dict-table"
      >
        <el-table-column type="index" label="#" width="50" />
        <el-table-column
          v-for="col in config.columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :width="col.width"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span v-if="col.type === 'select'">
              {{ getOptionLabel(col.prop, row[col.prop]) }}
            </span>
            <span v-else>{{ row[col.prop] ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm
              title="确认停用该记录？"
              confirm-button-text="确认"
              cancel-button-text="取消"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button link type="danger" size="small" :disabled="!row.is_active">停用</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="dict-pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchData"
          @size-change="fetchData"
        />
      </div>
    </div>

    <!-- Add / Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑' : '新增'"
      width="600px"
      destroy-on-close
      class="dict-dialog"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="110px">
        <el-form-item
          v-for="col in config.columns"
          :key="col.prop"
          :label="col.label"
          :prop="col.prop"
        >
          <el-date-picker
            v-if="col.type === 'date'"
            v-model="formData[col.prop]"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
          <el-input-number
            v-else-if="col.type === 'number'"
            v-model="formData[col.prop]"
            :controls="false"
            style="width: 100%"
          />
          <el-select
            v-else-if="col.type === 'enum'"
            v-model="formData[col.prop]"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option v-for="c in col.choices" :key="c" :label="c" :value="c" />
          </el-select>
          <el-select
            v-else-if="col.type === 'select'"
            v-model="formData[col.prop]"
            placeholder="请选择"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="opt in optionsMap[col.prop]"
              :key="opt.id"
              :label="opt.label"
              :value="opt.id"
            />
          </el-select>
          <el-input v-else v-model="formData[col.prop]" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../api/request.js'

const props = defineProps({
  config: { type: Object, required: true },
})

const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const keyword = ref('')

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const formData = reactive({})
const submitting = ref(false)

const optionsMap = reactive({})

const formRules = computed(() => {
  const rules = {}
  for (const col of props.config.columns) {
    if (col.required) {
      rules[col.prop] = [{ required: true, message: `请输入${col.label}`, trigger: 'blur' }]
    }
  }
  return rules
})

let searchTimer = null
function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchData()
  }, 300)
}

async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    const data = await request.get(props.config.api, { params })
    tableData.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

async function fetchOptions() {
  for (const col of props.config.columns) {
    if (col.type === 'select' && col.options?.api) {
      try {
        const data = await request.get(col.options.api)
        optionsMap[col.prop] = data
      } catch {
        optionsMap[col.prop] = []
      }
    }
  }
}

function getOptionLabel(prop, value) {
  if (value == null) return '-'
  const list = optionsMap[prop] || []
  const item = list.find((o) => o.id === value)
  return item ? item.label : value
}

function openDialog(row) {
  isEdit.value = !!row
  editingId.value = row?.id || null
  for (const col of props.config.columns) {
    formData[col.prop] = row ? row[col.prop] : (col.type === 'number' ? null : '')
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = {}
    for (const col of props.config.columns) {
      const val = formData[col.prop]
      if (val !== '' && val !== null && val !== undefined) {
        payload[col.prop] = val
      }
    }
    if (isEdit.value) {
      await request.put(`${props.config.api}/${editingId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post(props.config.api, payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row) {
  await request.delete(`${props.config.api}/${row.id}`)
  ElMessage.success('已停用')
  fetchData()
}

onMounted(() => {
  fetchData()
  fetchOptions()
})
</script>

<style scoped>
.dict-page {
  font-family: 'DM Sans', 'Noto Serif SC', sans-serif;
}

.dict-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.dict-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px;
  font-weight: 600;
  color: #0a1628;
  margin: 0;
}

.dict-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.add-btn {
  background: linear-gradient(135deg, #0a1628, #162847);
  border: none;
  border-radius: 8px;
  font-weight: 500;
}

.add-btn:hover {
  background: linear-gradient(135deg, #c8956c, #e8b888);
  color: #0a1628;
}

.dict-table-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(10, 22, 40, 0.05);
}

.dict-table {
  width: 100%;
}

.dict-table :deep(.el-table__header th) {
  background: #faf8f5 !important;
  color: #0a1628;
  font-weight: 600;
  font-size: 13px;
}

.dict-table :deep(.el-table__row) {
  font-size: 13px;
}

.dict-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.dict-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #0a1628, #162847);
  margin: 0;
  padding: 16px 20px;
}

.dict-dialog :deep(.el-dialog__title) {
  color: #f5f0eb;
  font-family: 'Noto Serif SC', serif;
}

.dict-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #8a9bb5;
}

.dict-dialog :deep(.el-dialog__body) {
  padding: 24px 20px;
}
</style>
