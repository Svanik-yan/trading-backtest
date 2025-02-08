<template>
  <div class="app">
    <van-nav-bar 
      title="策略回测系统" 
      fixed 
      placeholder
      :border="false"
      class="nav-bar"
    />
    
    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 配置部分 -->
      <div class="config-section">
        <!-- 策略设置 -->
        <StrategyConfig />
        
        <!-- 时间和成本设置 -->
        <TimeAndCostConfig />
        
        <!-- 择时设置 -->
        <TimingConfig />
      </div>

      <!-- 回测结果 -->
      <transition name="fade">
        <div v-if="store.backtestResult" class="result-section">
          <KLineChart />
          <TradeAnalysis />
          <BacktestResult />
        </div>
      </transition>

      <!-- 空状态提示 -->
      <div v-if="!store.backtestResult" class="empty-state">
        <van-empty 
          description="请设置策略参数并开始回测"
          image="search"
        />
      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="action-bar">
      <van-button 
        type="primary" 
        block 
        @click="startBacktest" 
        :loading="loading"
        size="large"
        class="submit-button"
      >
        <template #loading>
          <span class="loading-text">回测中...</span>
        </template>
        开始回测
      </van-button>
    </div>

    <!-- 免责声明 -->
    <div class="disclaimer">
      本网站的信息仅供参考，不构成任何投资建议。
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from '@vue/runtime-core'
import { showToast } from 'vant'
import { useBacktestStore } from '@/stores/backtest'
import StrategyConfig from './components/StrategyConfig/index.vue'
import TimingConfig from './components/TimingConfig/index.vue'
import BacktestResult from './components/BacktestResult/index.vue'
import TimeAndCostConfig from './components/TimeAndCostConfig/index.vue'
import KLineChart from '@/components/KLineChart/index.vue'
import TradeAnalysis from '@/components/TradeAnalysis/index.vue'

const store = useBacktestStore()
const loading = ref(false)

const startBacktest = async () => {
  loading.value = true
  try {
    await store.runBacktest()
  } catch (error: any) {
    console.error('回测失败:', error)
    showToast({
      message: error.message || '回测执行失败',
      type: 'fail',
      duration: 2000
    })
  } finally {
    loading.value = false
  }
}
</script>

<style>
:root {
  --app-background: #f7f8fa;
  --card-background: #ffffff;
  --primary-color: #1989fa;
  --border-radius: 12px;
  --shadow-color: rgba(0, 0, 0, 0.05);
}

.app {
  min-height: 100vh;
  background-color: var(--app-background);
  padding-bottom: calc(80px + env(safe-area-inset-bottom));
}

.nav-bar {
  background-color: var(--card-background) !important;
  box-shadow: 0 1px 6px var(--shadow-color);
}

.nav-bar .van-nav-bar__title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.main-content {
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
}

.config-section {
  margin-bottom: 24px;
}

.config-section :deep(.van-cell-group) {
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px var(--shadow-color);
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 16px;
}

.config-section :deep(.van-cell-group:active) {
  transform: scale(0.99);
  box-shadow: 0 1px 4px var(--shadow-color);
}

.result-section {
  margin-bottom: 80px;
}

.result-section :deep(.van-cell-group) {
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px var(--shadow-color);
  margin-bottom: 16px;
  overflow: hidden;
}

.empty-state {
  padding: 48px 0;
  background-color: var(--card-background);
  border-radius: var(--border-radius);
  box-shadow: 0 2px 8px var(--shadow-color);
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
  padding: 16px;
  padding-bottom: calc(16px + env(safe-area-inset-bottom));
  background-color: var(--card-background);
  box-shadow: 0 -2px 8px var(--shadow-color);
}

.submit-button {
  height: 44px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
}

.loading-text {
  margin-right: 8px;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  :root {
    --app-background: #1a1a1a;
    --card-background: #2c2c2c;
    --shadow-color: rgba(0, 0, 0, 0.2);
  }

  .app {
    color: #fff;
  }

  .nav-bar {
    color: #fff;
  }

  .empty-state {
    background-color: var(--card-background);
  }
}

.disclaimer {
  text-align: center;
  padding: 16px;
  color: var(--van-gray-6);
  font-size: 14px;
  margin-bottom: calc(80px + env(safe-area-inset-bottom));
}
</style> 