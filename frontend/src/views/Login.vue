<template>
  <div class="login-page">
    <!-- Left branding panel -->
    <div class="login-brand">
      <div class="brand-grid"></div>
      <div class="brand-content">
        <div class="brand-badge">LOGISTICS DATA</div>
        <h1 class="brand-title">“企业”物流<br/>数据管理系统</h1>
        <p class="brand-subtitle">Enterprise Logistics Data Management</p>
        <div class="brand-divider"></div>
        <p class="brand-desc">高效数据管理 · 智能决策支持 · 全链路可视化</p>
      </div>
      <div class="brand-footer">
        <span class="brand-version">v1.0</span>
      </div>
    </div>

    <!-- Right login panel -->
    <div class="login-panel">
      <div class="login-form-wrapper">
        <div class="form-header">
          <h2 class="form-title">欢迎登录</h2>
          <p class="form-subtitle">请输入您的账户信息以继续</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" label-width="0" @submit.prevent="handleLogin" class="login-form">
          <div class="input-group">
            <label class="input-label">用户名</label>
            <el-form-item prop="username">
              <el-input
                v-model="form.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="UserIcon"
              />
            </el-form-item>
          </div>

          <div class="input-group">
            <label class="input-label">密码</label>
            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                show-password
                :prefix-icon="LockIcon"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
          </div>

          <el-form-item class="login-btn-item">
            <button
              type="button"
              class="login-btn"
              :class="{ 'is-loading': loading }"
              :disabled="loading"
              @click="handleLogin"
            >
              <span v-if="!loading">登 录</span>
              <span v-else class="loading-dots">
                <i></i><i></i><i></i>
              </span>
            </button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user.js'

const UserIcon = markRaw(User)
const LockIcon = markRaw(Lock)

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Design tokens ── */
:root {
  --navy: #0a1628;
  --navy-light: #12213a;
  --amber: #c8956c;
  --amber-glow: #e8b888;
  --warm-white: #f5f0eb;
  --surface: #faf8f5;
  --text-muted: #8a9bb5;
}

/* ── Page layout: split screen ── */
.login-page {
  display: flex;
  height: 100vh;
  overflow: hidden;
  font-family: 'DM Sans', 'Noto Serif SC', sans-serif;
}

/* ── Left branding panel ── */
.login-brand {
  flex: 0 0 46%;
  background: linear-gradient(160deg, #0a1628 0%, #0f1d33 40%, #162847 100%);
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 60px;
  overflow: hidden;
}

.brand-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(200, 149, 108, 0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(200, 149, 108, 0.06) 1px, transparent 1px);
  background-size: 48px 48px;
  mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, black 20%, transparent 70%);
  -webkit-mask-image: radial-gradient(ellipse 70% 60% at 50% 50%, black 20%, transparent 70%);
  animation: gridFade 1.5s ease-out both;
}

@keyframes gridFade {
  from { opacity: 0; }
  to { opacity: 1; }
}

.brand-content {
  position: relative;
  z-index: 1;
  text-align: center;
  animation: brandSlide 0.9s cubic-bezier(0.16, 1, 0.3, 1) both;
}

@keyframes brandSlide {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.brand-badge {
  display: inline-block;
  padding: 6px 20px;
  border: 1px solid rgba(200, 149, 108, 0.35);
  border-radius: 2px;
  font-family: 'DM Sans', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 4px;
  color: #c8956c;
  margin-bottom: 36px;
}

.brand-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 42px;
  font-weight: 700;
  color: #f5f0eb;
  line-height: 1.3;
  margin: 0 0 16px 0;
  letter-spacing: 2px;
}

.brand-subtitle {
  font-family: 'DM Sans', sans-serif;
  font-size: 13px;
  font-weight: 400;
  letter-spacing: 3px;
  color: rgba(200, 149, 108, 0.6);
  text-transform: uppercase;
  margin: 0 0 32px 0;
}

.brand-divider {
  width: 48px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #c8956c, transparent);
  margin: 0 auto 28px;
}

.brand-desc {
  font-size: 14px;
  color: #8a9bb5;
  margin: 0;
  letter-spacing: 1px;
}

.brand-footer {
  position: absolute;
  bottom: 36px;
  left: 0;
  right: 0;
  text-align: center;
}

.brand-version {
  font-family: 'DM Sans', sans-serif;
  font-size: 11px;
  color: rgba(138, 155, 181, 0.4);
  letter-spacing: 2px;
}

/* ── Right login panel ── */
.login-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #faf8f5;
  position: relative;
}

.login-panel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse at 20% 80%, rgba(200, 149, 108, 0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(10, 22, 40, 0.02) 0%, transparent 50%);
  pointer-events: none;
}

.login-form-wrapper {
  position: relative;
  width: 380px;
  animation: formAppear 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
}

@keyframes formAppear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.form-header {
  margin-bottom: 40px;
}

.form-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 28px;
  font-weight: 600;
  color: #0a1628;
  margin: 0 0 8px 0;
}

.form-subtitle {
  font-size: 14px;
  color: #8a9bb5;
  margin: 0;
}

/* ── Custom input styling ── */
.input-group {
  margin-bottom: 8px;
}

.input-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #0a1628;
  margin-bottom: 8px;
  font-family: 'DM Sans', sans-serif;
}

.login-form :deep(.el-input__wrapper) {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(10, 22, 40, 0.06), 0 0 0 1px rgba(10, 22, 40, 0.08);
  padding: 4px 16px;
  transition: all 0.25s ease;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 2px 8px rgba(10, 22, 40, 0.08), 0 0 0 1px rgba(200, 149, 108, 0.3);
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 2px 12px rgba(200, 149, 108, 0.12), 0 0 0 2px rgba(200, 149, 108, 0.4);
}

.login-form :deep(.el-input__inner) {
  font-family: 'DM Sans', sans-serif;
  font-size: 15px;
  color: #0a1628;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: #bfc8d6;
}

.login-form :deep(.el-input__prefix .el-icon) {
  color: #c8956c;
  font-size: 18px;
}

.login-form :deep(.el-form-item__error) {
  font-size: 12px;
  padding-top: 4px;
}

/* ── Login button ── */
.login-btn-item {
  margin-top: 12px;
}

.login-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #0a1628 0%, #162847 100%);
  color: #f5f0eb;
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 8px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.35s ease;
}

.login-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #c8956c 0%, #e8b888 100%);
  opacity: 0;
  transition: opacity 0.35s ease;
}

.login-btn:hover::before {
  opacity: 1;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px rgba(200, 149, 108, 0.25);
  color: #0a1628;
}

.login-btn:active {
  transform: translateY(0);
}

.login-btn span {
  position: relative;
  z-index: 1;
}

.login-btn.is-loading {
  pointer-events: none;
  opacity: 0.8;
}

/* ── Loading dots ── */
.loading-dots {
  display: inline-flex;
  gap: 6px;
  align-items: center;
}

.loading-dots i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f5f0eb;
  animation: dotPulse 1.2s ease-in-out infinite;
}

.loading-dots i:nth-child(2) { animation-delay: 0.15s; }
.loading-dots i:nth-child(3) { animation-delay: 0.3s; }

@keyframes dotPulse {
  0%, 80%, 100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .login-brand {
    display: none;
  }
  .login-panel {
    background: linear-gradient(160deg, #0a1628 0%, #162847 50%, #1e3356 100%);
  }
  .login-panel::before {
    background: none;
  }
  .form-title {
    color: #f5f0eb;
  }
  .form-subtitle {
    color: #8a9bb5;
  }
  .input-label {
    color: #c8956c;
  }
  .login-form :deep(.el-input__wrapper) {
    background: rgba(255, 255, 255, 0.07);
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1);
  }
  .login-form :deep(.el-input__inner) {
    color: #f5f0eb;
  }
}
</style>
