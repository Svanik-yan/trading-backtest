<template>
  <div class="trade-analysis">
    <van-cell-group inset title="交易分析" class="analysis-card">
      <!-- 回测指标 -->
      <div class="metrics-grid">
        <van-cell title="盈亏比" :value="formatNumber(store.backtestResult?.profitFactor)" />
        <van-cell title="最大连续亏损" :value="store.backtestResult?.maxConsecutiveLosses + '次'" />
        <van-cell title="平均盈利" :value="formatMoney(store.backtestResult?.avgWinAmount)" />
        <van-cell title="平均亏损" :value="formatMoney(Math.abs(store.backtestResult?.avgLossAmount || 0))" />
        <van-cell title="最大单笔盈利" :value="formatMoney(store.backtestResult?.maxSingleWin)" />
        <van-cell title="最大单笔亏损" :value="formatMoney(Math.abs(store.backtestResult?.maxSingleLoss || 0))" />
      </div>
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { useBacktestStore } from '@/stores/backtest'

const store = useBacktestStore()

// 格式化金额
const formatMoney = (value: number | undefined) => {
  if (value === undefined) return '-'
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

// 格式化数字
const formatNumber = (value: number | undefined) => {
  if (value === undefined) return '-'
  return value.toFixed(2)
}
</script>

<style scoped>
.trade-analysis {
  margin-bottom: 16px;
}

.analysis-card {
  overflow: hidden;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background-color: var(--van-cell-border-color);
}

.metrics-grid :deep(.van-cell) {
  background-color: var(--van-cell-background);
  padding: 10px 16px;
}
</style> 