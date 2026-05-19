<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '68px' : '240px'" class="layout-aside">
      <!-- Logo -->
      <div class="logo-area">
        <div class="logo-icon">
          <svg viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="6" width="24" height="4" rx="1.5" fill="#c8956c" opacity="0.9"/>
            <rect x="2" y="12" width="18" height="4" rx="1.5" fill="#c8956c" opacity="0.6"/>
            <rect x="2" y="18" width="24" height="4" rx="1.5" fill="#c8956c" opacity="0.35"/>
          </svg>
        </div>
        <transition name="logo-text">
          <span v-show="!isCollapse" class="logo-text">烟草物流数据</span>
        </transition>
      </div>
      <div class="logo-divider"></div>

      <!-- Navigation -->
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        class="side-menu"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>
        <el-menu-item index="/import">
          <el-icon><Upload /></el-icon>
          <template #title>数据导入</template>
        </el-menu-item>
        <el-sub-menu index="dict">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>字典管理</span>
          </template>
          <el-menu-item index="/dict/person">
            <el-icon><User /></el-icon>
            <template #title>人员管理</template>
          </el-menu-item>
          <el-menu-item index="/dict/vehicle">
            <el-icon><Van /></el-icon>
            <template #title>车辆管理</template>
          </el-menu-item>
          <el-menu-item index="/dict/route">
            <el-icon><Guide /></el-icon>
            <template #title>线路管理</template>
          </el-menu-item>
          <el-menu-item index="/dict/customer">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>零售客户</template>
          </el-menu-item>
          <el-menu-item index="/dict/cigarette">
            <el-icon><Goods /></el-icon>
            <template #title>卷烟品牌</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>

      <!-- Sidebar footer -->
      <div class="aside-footer">
        <div class="aside-footer-divider"></div>
        <div class="aside-footer-content" @click="isCollapse = !isCollapse">
          <el-icon class="collapse-icon" :class="{ rotated: isCollapse }">
            <DArrowLeft />
          </el-icon>
          <transition name="logo-text">
            <span v-show="!isCollapse" class="collapse-label">收起菜单</span>
          </transition>
        </div>
      </div>
    </el-aside>

    <el-container class="main-container">
      <!-- Header -->
      <el-header class="layout-header" height="60px">
        <div class="header-left">
          <div class="breadcrumb-hint">
            <span class="breadcrumb-dot"></span>
            <span>工作台</span>
          </div>
        </div>
        <div class="header-right">
          <div class="user-block">
            <div class="user-avatar">
              {{ (userStore.userInfo?.real_name || userStore.userInfo?.username || 'U').charAt(0) }}
            </div>
            <span class="user-name">{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</span>
          </div>
          <div class="header-divider"></div>
          <button class="logout-btn" @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            <span>退出</span>
          </button>
        </div>
      </el-header>

      <!-- Content -->
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user.js'

const route = useRoute()
const userStore = useUserStore()
const isCollapse = ref(false)

function handleLogout() {
  userStore.logout()
}
</script>

<style scoped>
/* ── Design tokens ── */
.layout-container {
  --navy: #0a1628;
  --navy-mid: #0f1d33;
  --amber: #c8956c;
  --amber-glow: #e8b888;
  --warm-white: #f5f0eb;
  --surface: #f6f4f0;
  --text-muted: #8a9bb5;

  height: 100vh;
  font-family: 'DM Sans', 'Noto Serif SC', sans-serif;
}

/* ── Sidebar ── */
.layout-aside {
  background: linear-gradient(180deg, #0a1628 0%, #0d1b2f 100%);
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(200, 149, 108, 0.08);
}

.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  gap: 12px;
  flex-shrink: 0;
}

.logo-icon {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
}

.logo-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 600;
  color: var(--warm-white);
  white-space: nowrap;
  letter-spacing: 1px;
}

.logo-text-enter-active,
.logo-text-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.logo-text-enter-from,
.logo-text-leave-to {
  opacity: 0;
  transform: translateX(-8px);
}

.logo-divider {
  height: 1px;
  margin: 0 16px 8px;
  background: linear-gradient(90deg, transparent, rgba(200, 149, 108, 0.15), transparent);
  flex-shrink: 0;
}

/* ── Menu override ── */
.side-menu {
  border-right: none !important;
  background: transparent !important;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.side-menu::-webkit-scrollbar {
  width: 0;
}

.side-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  margin: 2px 10px;
  border-radius: 8px;
  color: var(--text-muted);
  font-size: 14px;
  transition: all 0.25s ease;
}

.side-menu :deep(.el-menu-item:hover) {
  background: rgba(200, 149, 108, 0.08) !important;
  color: var(--warm-white);
}

.side-menu :deep(.el-menu-item.is-active) {
  background: rgba(200, 149, 108, 0.12) !important;
  color: var(--amber) !important;
  font-weight: 500;
}

.side-menu :deep(.el-menu-item .el-icon) {
  font-size: 18px;
}

/* ── Sidebar footer ── */
.aside-footer {
  flex-shrink: 0;
  padding-bottom: 12px;
}

.aside-footer-divider {
  height: 1px;
  margin: 0 16px 8px;
  background: linear-gradient(90deg, transparent, rgba(200, 149, 108, 0.1), transparent);
}

.aside-footer-content {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 22px;
  cursor: pointer;
  color: rgba(138, 155, 181, 0.5);
  font-size: 12px;
  transition: color 0.2s;
}

.aside-footer-content:hover {
  color: var(--text-muted);
}

.collapse-icon {
  font-size: 16px;
  transition: transform 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.collapse-icon.rotated {
  transform: rotate(180deg);
}

.collapse-label {
  white-space: nowrap;
  letter-spacing: 1px;
}

/* ── Header ── */
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  border-bottom: 1px solid rgba(10, 22, 40, 0.06);
  padding: 0 28px;
  box-shadow: 0 1px 4px rgba(10, 22, 40, 0.03);
}

.header-left {
  display: flex;
  align-items: center;
}

.breadcrumb-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606878;
  font-weight: 500;
}

.breadcrumb-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--amber);
  box-shadow: 0 0 0 3px rgba(200, 149, 108, 0.15);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-block {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--navy) 0%, #1e3356 100%);
  color: var(--amber);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 600;
}

.user-name {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.header-divider {
  width: 1px;
  height: 20px;
  background: #e8e8e8;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
  color: #909399;
  padding: 6px 10px;
  border-radius: 6px;
  transition: all 0.2s;
  font-family: inherit;
}

.logout-btn:hover {
  color: #c85a5a;
  background: rgba(200, 90, 90, 0.06);
}

.logout-btn .el-icon {
  font-size: 16px;
}

/* ── Main content ── */
.layout-main {
  background: var(--surface);
  padding: 24px;
}

/* ── Page transition ── */
.page-enter-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.page-leave-active {
  transition: opacity 0.15s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
}
</style>
