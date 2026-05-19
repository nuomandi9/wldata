<template>
  <div class="import-page">
    <div class="import-header">
      <h2 class="import-title">数据导入</h2>
      <el-select
        v-model="templateKey"
        placeholder="选择模板"
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

    <!-- Step 1: Upload -->
    <div class="import-card">
      <div class="card-section-title">1. 上传 Excel</div>
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :show-file-list="true"
        :limit="1"
        :on-change="onFileChange"
        :on-remove="resetPreview"
        accept=".xlsx,.xls"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">拖拽文件到此处，或<em>点击选择</em></div>
        <template #tip>
          <div class="upload-tip">
            支持 .xlsx / .xls，单文件 ≤ 50MB。
            <span v-if="templateInfo">
              当前模板要求列：
              <el-tag v-for="c in templateInfo.columns" :key="c.field" size="small" class="hdr-tag"
                :type="c.required ? 'danger' : ''">{{ c.header }}<span v-if="c.required">*</span></el-tag>
            </span>
          </div>
        </template>
      </el-upload>
      <div class="action-row">
        <el-button
          type="primary"
          :disabled="!selectedFile || !templateKey"
          :loading="previewing"
          @click="doPreview"
        >预览并校验</el-button>
      </div>
    </div>

    <!-- Step 2: Preview -->
    <div v-if="preview" class="import-card">
      <div class="card-section-title">
        2. 校验结果
        <div class="summary">
          <el-tag type="info">共 {{ preview.total }} 行</el-tag>
          <el-tag type="success">通过 {{ preview.ok_count }}</el-tag>
          <el-tag type="warning">WARN {{ preview.warn_count }}</el-tag>
          <el-tag type="danger">BLOCK {{ preview.block_count }}</el-tag>
        </div>
      </div>

      <el-table
        ref="tableRef"
        :data="preview.rows"
        :row-class-name="rowClass"
        border size="small" max-height="500"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="44" :selectable="row => !row.has_block" />
        <el-table-column prop="row_number" label="#" width="60" />
        <el-table-column
          v-for="col in templateInfo?.columns || []"
          :key="col.field"
          :label="col.header"
          :prop="`raw.${col.field}`"
          min-width="100"
          show-overflow-tooltip
        >
          <template #default="{ row }">{{ row.raw[col.field] ?? '-' }}</template>
        </el-table-column>
        <el-table-column label="校验信息" min-width="240">
          <template #default="{ row }">
            <div v-if="row.issues.length === 0" class="ok-text">通过</div>
            <div v-for="(iss, i) in row.issues" :key="i" class="issue-line">
              <el-tag :type="iss.level === 'BLOCK' ? 'danger' : 'warning'" size="small">{{ iss.level }}</el-tag>
              <span class="issue-msg">{{ iss.message }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="WARN 备注" width="200" v-if="preview.warn_count > 0">
          <template #default="{ row }">
            <el-input
              v-if="row.has_warn && !row.has_block"
              v-model="warnNotes[row.row_number]"
              size="small"
              placeholder="必填，说明原因"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="action-row">
        <el-button
          type="primary"
          :loading="committing"
          :disabled="!hasCommittableRows"
          @click="doCommit"
        >入库 {{ committableCount }} 行</el-button>
        <el-button @click="selectAllNonBlock">选择全部非 BLOCK 行</el-button>
        <span class="hint" v-if="preview.block_count > 0">BLOCK 行无法入库，请修正源表后重新上传。</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import request from '../../api/request.js'

const templates = ref([])
const templateKey = ref('')
const templateInfo = computed(() => templates.value.find(t => t.key === templateKey.value))

const uploadRef = ref(null)
const tableRef = ref(null)
const selectedFile = ref(null)
const previewing = ref(false)
const preview = ref(null)
const warnNotes = reactive({})
const selectedRowNumbers = ref(new Set())
const committing = ref(false)

function onSelectionChange(rows) {
  selectedRowNumbers.value = new Set(rows.map(r => r.row_number))
}

const committableCount = computed(() => {
  if (!preview.value) return 0
  return preview.value.rows.filter(r => !r.has_block && selectedRowNumbers.value.has(r.row_number)).length
})
const hasCommittableRows = computed(() => committableCount.value > 0)

async function fetchTemplates() {
  templates.value = await request.get('/api/import/templates')
  if (templates.value.length > 0 && !templateKey.value) {
    templateKey.value = templates.value[0].key
  }
}

function onTemplateChange() {
  resetPreview()
}

function onFileChange(uploadFile) {
  selectedFile.value = uploadFile.raw
  preview.value = null
}

function resetPreview() {
  preview.value = null
  selectedFile.value = null
  selectedRowNumbers.value = new Set()
  for (const k of Object.keys(warnNotes)) delete warnNotes[k]
  uploadRef.value?.clearFiles?.()
}

async function doPreview() {
  if (!selectedFile.value || !templateKey.value) return
  previewing.value = true
  try {
    const form = new FormData()
    form.append('file', selectedFile.value)
    preview.value = await request.post(
      `/api/import/${templateKey.value}/preview`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    await nextTick()
    for (const row of preview.value.rows) {
      if (!row.has_block) tableRef.value?.toggleRowSelection(row, true)
    }
    ElMessage.success(`解析完成：${preview.value.total} 行，BLOCK ${preview.value.block_count}，WARN ${preview.value.warn_count}`)
  } finally {
    previewing.value = false
  }
}

function selectAllNonBlock() {
  if (!preview.value || !tableRef.value) return
  tableRef.value.clearSelection()
  for (const row of preview.value.rows) {
    if (!row.has_block) tableRef.value.toggleRowSelection(row, true)
  }
}

function rowClass({ row }) {
  if (row.has_block) return 'row-block'
  if (row.has_warn) return 'row-warn'
  return ''
}

async function doCommit() {
  if (!preview.value || !selectedFile.value) return
  const toCommit = preview.value.rows.filter(
    r => !r.has_block && selectedRowNumbers.value.has(r.row_number),
  )
  // Ensure WARN rows have notes
  const missingNotes = toCommit.filter(r => r.has_warn && !warnNotes[r.row_number]?.trim())
  if (missingNotes.length > 0) {
    ElMessage.error(`第 ${missingNotes.map(r => r.row_number).join(', ')} 行（WARN）需要填写备注`)
    return
  }
  committing.value = true
  try {
    const form = new FormData()
    form.append('file', selectedFile.value)
    form.append('commit_row_numbers', JSON.stringify(toCommit.map(r => r.row_number)))
    form.append('warn_notes', JSON.stringify(
      Object.fromEntries(Object.entries(warnNotes).filter(([_, v]) => v?.trim()))
    ))
    const result = await request.post(
      `/api/import/${templateKey.value}/commit`,
      form,
      { headers: { 'Content-Type': 'multipart/form-data' } },
    )
    if (result.skipped > 0) {
      ElMessage.warning(`入库 ${result.inserted} 行，跳过 ${result.skipped} 行：${result.skipped_reasons.join('；')}`)
    } else {
      ElMessage.success(`成功入库 ${result.inserted} 行`)
    }
    resetPreview()
  } finally {
    committing.value = false
  }
}

onMounted(fetchTemplates)
</script>

<style scoped>
.import-page { font-family: 'DM Sans', 'Noto Serif SC', sans-serif; }

.import-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.import-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px; font-weight: 600; color: #0a1628; margin: 0;
}
.template-select { width: 220px; }

.import-card {
  background: #fff; border-radius: 12px; padding: 20px;
  border: 1px solid rgba(10, 22, 40, 0.05); margin-bottom: 20px;
}
.card-section-title {
  font-weight: 600; color: #0a1628; margin-bottom: 14px;
  display: flex; align-items: center; gap: 12px;
}
.summary { display: flex; gap: 8px; }

.upload-tip { color: #909399; font-size: 12px; margin-top: 6px; line-height: 1.8; }
.hdr-tag { margin: 0 4px 4px 0; }

.action-row {
  margin-top: 16px; display: flex; align-items: center; gap: 12px;
}
.hint { color: #909399; font-size: 12px; }

.ok-text { color: #67c23a; font-size: 12px; }
.issue-line { display: flex; align-items: center; gap: 6px; line-height: 1.8; }
.issue-msg { font-size: 12px; color: #606266; }

:deep(.row-block) { background-color: rgba(245, 108, 108, 0.08); }
:deep(.row-warn)  { background-color: rgba(230, 162, 60, 0.08); }
</style>
