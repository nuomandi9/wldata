<template>
  <div class="page">
    <div class="page-header">
      <h2 class="page-title">用户管理</h2>
      <el-button type="primary" @click="openCreate">新建用户</el-button>
    </div>

    <div class="card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="搜索">
          <el-input
            v-model="keyword"
            clearable
            placeholder="用户名 / 姓名"
            style="width: 200px;"
            @keyup.enter="query(1)"
            @clear="query(1)"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="query(1)">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="rows" border size="small" v-loading="loading">
        <el-table-column prop="id" label="#" width="70" />
        <el-table-column prop="username" label="用户名" min-width="140" />
        <el-table-column prop="real_name" label="姓名" min-width="120">
          <template #default="{ row }">{{ row.real_name || '-' }}</template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag size="small" :type="row.role === 'admin' ? 'danger' : ''">
              {{ row.role === 'admin' ? '管理员' : '操作员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '在用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="240">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button link type="primary" size="small" @click="openReset(row)">重置密码</el-button>
            <el-button
              link
              :type="row.is_active ? 'danger' : 'success'"
              size="small"
              @click="toggleActive(row)"
            >{{ row.is_active ? '停用' : '启用' }}</el-button>
          </template>
        </el-table-column>
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

    <!-- Create / Edit dialog -->
    <el-dialog v-model="dialogVisible" :title="editing ? '编辑用户' : '新建用户'" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" :disabled="editing" placeholder="登录用户名" />
        </el-form-item>
        <el-form-item v-if="!editing" label="密码" prop="password">
          <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="可选" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" style="width: 100%;">
            <el-option label="操作员" value="operator" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <!-- Reset password dialog -->
    <el-dialog v-model="resetVisible" title="重置密码" width="400px">
      <el-form ref="resetFormRef" :model="resetForm" :rules="resetRules" label-width="90px">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetForm.new_password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetting" @click="doReset">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../../api/request.js'

const rows = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')
const loading = ref(false)

async function query(p = 1) {
  page.value = p
  loading.value = true
  try {
    const params = { page: p, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    const data = await request.get('/api/users', { params })
    rows.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

// ── Create / Edit ──
const dialogVisible = ref(false)
const editing = ref(false)
const editingId = ref(null)
const saving = ref(false)
const formRef = ref(null)
const form = reactive({ username: '', password: '', real_name: '', role: 'operator' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, min: 6, message: '密码至少 6 位', trigger: 'blur' }],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

function openCreate() {
  editing.value = false
  editingId.value = null
  Object.assign(form, { username: '', password: '', real_name: '', role: 'operator' })
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = true
  editingId.value = row.id
  Object.assign(form, { username: row.username, password: '', real_name: row.real_name || '', role: row.role })
  dialogVisible.value = true
}

async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    if (editing.value) {
      await request.put(`/api/users/${editingId.value}`, {
        real_name: form.real_name || null,
        role: form.role,
      })
      ElMessage.success('已保存')
    } else {
      await request.post('/api/users', {
        username: form.username,
        password: form.password,
        real_name: form.real_name || null,
        role: form.role,
      })
      ElMessage.success('用户已创建')
    }
    dialogVisible.value = false
    query(page.value)
  } finally {
    saving.value = false
  }
}

// ── Reset password ──
const resetVisible = ref(false)
const resetting = ref(false)
const resetTargetId = ref(null)
const resetFormRef = ref(null)
const resetForm = reactive({ new_password: '' })
const resetRules = {
  new_password: [{ required: true, min: 6, message: '密码至少 6 位', trigger: 'blur' }],
}

function openReset(row) {
  resetTargetId.value = row.id
  resetForm.new_password = ''
  resetVisible.value = true
}

async function doReset() {
  await resetFormRef.value.validate()
  resetting.value = true
  try {
    await request.post(`/api/users/${resetTargetId.value}/reset-password`, {
      new_password: resetForm.new_password,
    })
    ElMessage.success('密码已重置')
    resetVisible.value = false
  } finally {
    resetting.value = false
  }
}

// ── Enable / Disable ──
async function toggleActive(row) {
  await request.put(`/api/users/${row.id}`, { is_active: !row.is_active })
  ElMessage.success(row.is_active ? '已停用' : '已启用')
  query(page.value)
}

onMounted(() => query(1))
</script>

<style scoped>
.page { font-family: 'DM Sans', 'Noto Serif SC', sans-serif; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.page-title { font-family: 'Noto Serif SC', serif; font-size: 20px; font-weight: 600; color: #0a1628; margin: 0; }
.card { background: #fff; border-radius: 12px; padding: 20px; border: 1px solid rgba(10, 22, 40, 0.05); }
.filter-form { margin-bottom: 8px; }
.pager { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
