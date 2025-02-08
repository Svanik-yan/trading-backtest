<template>
  <div class="timing-config">
    <van-cell-group inset title="择时设置" class="config-card">
      <!-- 买入/卖出条件切换 -->
      <van-tabs v-model:active="activeTab" class="condition-tabs">
        <van-tab title="买入条件">
          <div class="condition-list">
            <div v-for="(condition, index) in buyConditions" :key="index" class="condition-item">
              <div class="condition-content">
                <van-tag type="primary" size="medium">{{ condition }}</van-tag>
                <van-icon name="cross" @click="removeCondition('buy', index)" />
              </div>
            </div>
            <div class="add-condition" @click="showIndicatorPicker('buy')">
              <van-icon name="plus" />
              <span>从左侧添加指标或者多个条件是AND逻辑</span>
            </div>
          </div>
        </van-tab>
        <van-tab title="卖出条件">
          <div class="condition-list">
            <div v-for="(condition, index) in sellConditions" :key="index" class="condition-item">
              <div class="condition-content">
                <van-tag type="danger" size="medium">{{ condition }}</van-tag>
                <van-icon name="cross" @click="removeCondition('sell', index)" />
              </div>
            </div>
            <div class="add-condition" @click="showIndicatorPicker('sell')">
              <van-icon name="plus" />
              <span>从左侧添加指标或者多个条件是AND逻辑</span>
            </div>
          </div>
        </van-tab>
      </van-tabs>
    </van-cell-group>

    <!-- 指标选择弹窗 -->
    <van-popup
      v-model:show="showPicker"
      position="bottom"
      round
      class="indicator-popup"
    >
      <div class="popup-header">
        <div class="popup-title">选择指标</div>
      </div>
      <van-tabs v-model:active="activeIndicatorTab">
        <van-tab title="技术指标">
          <div class="indicator-grid">
            <div
              v-for="indicator in technicalIndicators"
              :key="indicator.value"
              class="indicator-item"
              @click="selectIndicator(indicator)"
            >
              {{ indicator.label }}
            </div>
          </div>
        </van-tab>
        <van-tab title="常用信号">
          <div class="indicator-grid">
            <div
              v-for="signal in commonSignals"
              :key="signal.value"
              class="indicator-item"
              @click="selectIndicator(signal)"
            >
              {{ signal.label }}
            </div>
          </div>
        </van-tab>
        <van-tab title="示例策略">
          <div class="indicator-grid">
            <div
              v-for="strategy in demoStrategies"
              :key="strategy.value"
              class="indicator-item"
              @click="selectIndicator(strategy)"
            >
              {{ strategy.label }}
            </div>
          </div>
        </van-tab>
      </van-tabs>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref } from '@vue/runtime-core'
import { useBacktestStore } from '@/stores/backtest'

const store = useBacktestStore()
const activeTab = ref(0) // 0: 买入条件, 1: 卖出条件
const activeIndicatorTab = ref(0)
const showPicker = ref(false)
const currentMode = ref<'buy' | 'sell'>('buy')

// 买入和卖出条件列表
const buyConditions = ref<string[]>([])
const sellConditions = ref<string[]>([])

// 技术指标列表
const technicalIndicators = [
  { label: 'MACD金叉', value: 'MACD_GOLDEN_CROSS' },
  { label: 'MACD死叉', value: 'MACD_DEAD_CROSS' },
  { label: 'RSI超买', value: 'RSI_OVERBOUGHT' },
  { label: 'RSI超卖', value: 'RSI_OVERSOLD' },
  { label: 'MA交叉向上', value: 'MA_CROSS_UP' },
  { label: 'MA交叉向下', value: 'MA_CROSS_DOWN' },
]

// 常用信号列表
const commonSignals = [
  { label: '布林带上轨突破', value: 'BOLL_BREAK_UP' },
  { label: '布林带下轨突破', value: 'BOLL_BREAK_DOWN' },
  { label: '随机指标金叉', value: 'KDJ_GOLDEN_CROSS' },
  { label: '随机指标死叉', value: 'KDJ_DEAD_CROSS' },
  { label: '价格上穿EMA', value: 'PRICE_ABOVE_EMA' },
  { label: 'ADX趋势强度', value: 'ADX_STRONG_TREND' },
]

// 示例策略列表
const demoStrategies = [
  { label: 'MACD_12_26_9', value: 'MACD_12_26_9' },
  { label: 'CCI超买', value: 'CCI_OVERBOUGHT' },
  { label: 'ATR止损', value: 'ATR_STOP_LOSS' },
  { label: 'SAR指标看涨', value: 'SAR_BULLISH' },
  { label: 'SAR指标看跌', value: 'SAR_BEARISH' },
]

// 显示指标选择器
const showIndicatorPicker = (mode: 'buy' | 'sell') => {
  currentMode.value = mode
  showPicker.value = true
}

// 选择指标
const selectIndicator = (indicator: { label: string, value: string }) => {
  if (currentMode.value === 'buy') {
    buyConditions.value.push(indicator.label)
  } else {
    sellConditions.value.push(indicator.label)
  }
  showPicker.value = false
}

// 移除条件
const removeCondition = (type: 'buy' | 'sell', index: number) => {
  if (type === 'buy') {
    buyConditions.value.splice(index, 1)
  } else {
    sellConditions.value.splice(index, 1)
  }
}
</script>

<style scoped>
.timing-config {
  margin-bottom: 16px;
}

.config-card {
  overflow: hidden;
}

.condition-tabs {
  padding: 16px;
}

.condition-list {
  padding: 8px 0;
}

.condition-item {
  margin-bottom: 8px;
}

.condition-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 4px;
}

/* 买入条件的背景色 */
:deep(.van-tab--active:nth-child(1)) {
  color: var(--van-danger-color) !important;
}

:deep(.van-tabs__line) {
  background-color: var(--van-danger-color);
}

/* 卖出条件的背景色 */
:deep(.van-tab--active:nth-child(2)) {
  color: var(--van-success-color) !important;
}

:deep(.van-tabs__line) {
  background-color: var(--van-success-color);
}

/* 买入条件内容区域 */
.van-tab:nth-child(1).van-tab--active ~ .van-tabs__content .condition-content {
  background-color: var(--van-danger-color-light, #fff1f0);
}

/* 卖出条件内容区域 */
.van-tab:nth-child(2).van-tab--active ~ .van-tabs__content .condition-content {
  background-color: var(--van-success-color-light, #f0fff0);
}

.condition-content .van-icon {
  color: #969799;
  cursor: pointer;
}

.add-condition {
  display: flex;
  align-items: center;
  padding: 12px;
  color: #969799;
  cursor: pointer;
}

.add-condition .van-icon {
  margin-right: 8px;
  font-size: 16px;
}

.indicator-popup {
  max-height: 80vh;
}

.popup-header {
  padding: 16px;
  text-align: center;
  border-bottom: 1px solid #f5f5f5;
}

.popup-title {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.indicator-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 16px;
}

.indicator-item {
  padding: 12px;
  text-align: center;
  background-color: #f7f8fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.indicator-item:active {
  background-color: #e8e8e8;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .condition-content {
    background-color: #2c2c2c;
  }

  .indicator-item {
    background-color: #2c2c2c;
  }

  .indicator-item:active {
    background-color: #363636;
  }

  /* 深色模式下的买入条件内容区域 */
  .van-tab:nth-child(1).van-tab--active ~ .van-tabs__content .condition-content {
    background-color: rgba(255, 69, 58, 0.1);
  }

  /* 深色模式下的卖出条件内容区域 */
  .van-tab:nth-child(2).van-tab--active ~ .van-tabs__content .condition-content {
    background-color: rgba(48, 209, 88, 0.1);
  }
}
</style> 