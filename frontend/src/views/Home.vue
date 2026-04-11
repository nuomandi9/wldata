<template>
  <div class="home-page">
    <!-- Welcome card -->
    <div class="welcome-card">
      <div class="welcome-content">
        <h1 class="welcome-title">
          {{ greeting }}，{{ userStore.userInfo?.real_name || userStore.userInfo?.username || '用户' }}
        </h1>
        <p class="welcome-desc">欢迎使用烟草物流数据管理系统，祝您工作顺利。</p>
      </div>
      <div class="welcome-pattern"></div>
    </div>

    <!-- Stats row -->
    <div class="stats-row">
      <div v-for="(stat, i) in stats" :key="i" class="stat-card" :style="{ animationDelay: `${0.1 + i * 0.08}s` }">
        <div class="stat-icon" :style="{ background: stat.bg }">
          <el-icon :size="22" :color="stat.color"><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-info">
          <span class="stat-value">{{ stat.value }}</span>
          <span class="stat-label">{{ stat.label }}</span>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="section-header">
      <span class="section-dot"></span>
      <h3>快捷操作</h3>
    </div>
    <div class="quick-actions">
      <div v-for="(action, i) in actions" :key="i" class="action-card" :style="{ animationDelay: `${0.3 + i * 0.06}s` }">
        <el-icon :size="24" class="action-icon"><component :is="action.icon" /></el-icon>
        <span class="action-label">{{ action.label }}</span>
        <span class="action-hint">{{ action.hint }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, markRaw } from 'vue'
import { Document, DataLine, TrendCharts, Upload } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user.js'

const userStore = useUserStore()

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 9) return '早上好'
  if (h < 12) return '上午好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const stats = [
  { icon: markRaw(Document), label: '本月报表', value: '--', color: '#c8956c', bg: 'rgba(200,149,108,0.1)' },
  { icon: markRaw(DataLine), label: '数据条目', value: '--', color: '#5b8def', bg: 'rgba(91,141,239,0.1)' },
  { icon: markRaw(TrendCharts), label: '同比增长', value: '--', color: '#52c484', bg: 'rgba(82,196,132,0.1)' },
  { icon: markRaw(Upload), label: '待处理', value: '--', color: '#e8885c', bg: 'rgba(232,136,92,0.1)' },
]

const actions = [
  { icon: markRaw(Upload), label: '上传数据', hint: '导入 Excel 报表' },
  { icon: markRaw(Document), label: '查看报表', hint: '浏览历史数据' },
  { icon: markRaw(DataLine), label: '数据分析', hint: '图表可视化' },
  { icon: markRaw(TrendCharts), label: '趋势对比', hint: '同环比分析' },
]
</script>

<style scoped>
.home-page {
  max-width: 1100px;
  font-family: 'DM Sans', 'Noto Serif SC', sans-serif;
}

/* ── Welcome card ── */
.welcome-card {
  background: linear-gradient(135deg, #0a1628 0%, #162847 60%, #1e3356 100%);
  border-radius: 14px;
  padding: 40px 44px;
  position: relative;
  overflow: hidden;
  margin-bottom: 24px;
  animation: fadeUp 0.5s ease both;
}

.welcome-pattern {
  position: absolute;
  top: 0;
  right: 0;
  width: 45%;
  height: 100%;
  background-image:
    linear-gradient(rgba(200,149,108,0.06) 1px, transparent 1px),
    linear-gradient(90deg, rgba(200,149,108,0.06) 1px, transparent 1px);
  background-size: 32px 32px;
  mask-image: linear-gradient(to left, rgba(0,0,0,0.5), transparent);
  -webkit-mask-image: linear-gradient(to left, rgba(0,0,0,0.5), transparent);
}

.welcome-content {
  position: relative;
  z-index: 1;
}

.welcome-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 26px;
  font-weight: 600;
  color: #f5f0eb;
  margin: 0 0 8px 0;
}

.welcome-desc {
  font-size: 14px;
  color: #8a9bb5;
  margin: 0;
}

/* ── Stats row ── */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 22px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(10, 22, 40, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  animation: fadeUp 0.5s ease both;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(10, 22, 40, 0.06);
}

.stat-icon {
  width: 46px;
  height: 46px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-family: 'DM Sans', sans-serif;
  font-size: 22px;
  font-weight: 700;
  color: #0a1628;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  letter-spacing: 0.5px;
}

/* ── Section header ── */
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.section-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c8956c;
}

.section-header h3 {
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 600;
  color: #0a1628;
  margin: 0;
}

/* ── Quick actions ── */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-card {
  background: #fff;
  border-radius: 12px;
  padding: 28px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  border: 1px solid rgba(10, 22, 40, 0.05);
  transition: all 0.25s ease;
  animation: fadeUp 0.5s ease both;
}

.action-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(10, 22, 40, 0.07);
  border-color: rgba(200, 149, 108, 0.2);
}

.action-card:hover .action-icon {
  color: #c8956c;
}

.action-icon {
  color: #606878;
  transition: color 0.25s;
}

.action-label {
  font-weight: 600;
  font-size: 14px;
  color: #0a1628;
}

.action-hint {
  font-size: 12px;
  color: #909399;
}

/* ── Animations ── */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── Responsive ── */
@media (max-width: 900px) {
  .stats-row,
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
