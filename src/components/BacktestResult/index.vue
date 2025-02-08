<!-- 回测结果展示组件 -->
<template>
  <div class="backtest-result">
    <!-- 指标概览 -->
    <van-cell-group inset title="回测指标" class="result-card">
      <div class="metrics-grid">
        <div class="metric-item">
          <div class="metric-label">净收益</div>
          <div class="metric-value">{{ formatMoney(getNetProfit()) }}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">交易次数</div>
          <div class="metric-value">{{ store.backtestResult?.tradeCount || 0 }}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">胜率</div>
          <div class="metric-value">{{ formatPercent(store.backtestResult?.winRate || 0) }}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">盈亏比</div>
          <div class="metric-value">{{ formatNumber(store.backtestResult?.profitFactor || 0) }}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">最大回撤</div>
          <div class="metric-value">{{ formatPercent(store.backtestResult?.maxDrawdown || 0) }}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">年化收益率</div>
          <div class="metric-value">{{ formatPercent(store.backtestResult?.annualizedReturn || 0) }}</div>
        </div>
      </div>
    </van-cell-group>

    <!-- 策略分析 -->
    <strategy-analysis />

    <!-- 交易记录 -->
    <trade-records />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from '@vue/runtime-core'
import { useBacktestStore } from '@/stores/backtest'
import dayjs from 'dayjs'
import type { Trade } from '@/stores/backtest'
import TradeRecords from '../TradeRecords/index.vue'
import StrategyAnalysis from '../StrategyAnalysis/index.vue'

const store = useBacktestStore()
const isExpanded = ref(true)
const trades = computed(() => store.backtestResult?.trades || [])

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

// 格式化金额
const formatMoney = (value: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

// 格式化数字
const formatNumber = (value: number) => {
  return value.toFixed(2)
}

// 格式化百分比
const formatPercent = (value: number) => {
  return (value * 100).toFixed(2) + '%'
}

// 格式化日期
const formatDate = (date: Date) => {
  return dayjs(date).format('YYYY-MM-DD')
}

// 计算某个交易时点的总资产
const getAssetValue = (index: number) => {
  if (!store.backtestResult) return 0
  const equityData = store.backtestResult.equityData
  const trade = trades.value[index]
  const tradeDate = dayjs(trade.date)
  
  // 找到交易日期对应的净值数据
  const equityPoint = equityData.find((point: { date: Date }) => 
    dayjs(point.date).format('YYYY-MM-DD') === tradeDate.format('YYYY-MM-DD')
  )
  
  return equityPoint?.value || 0
}

// 计算资产增长率
const getGrowthRate = (index: number) => {
  if (!store.backtestResult || index === 0) return 0
  
  const currentValue = getAssetValue(index)
  const previousValue = getAssetValue(index - 1)
  
  if (previousValue === 0) return 0
  return (currentValue - previousValue) / previousValue
}

// 计算净收益（最终总资产 - 初始总资产）
const getNetProfit = () => {
  if (!store.backtestResult?.equityData.length || !store.backtestConfig?.initialCapital) return 0
  const finalValue = store.backtestResult.equityData[store.backtestResult.equityData.length - 1].value
  return finalValue - store.backtestConfig.initialCapital
}
</script>

<style scoped>
.backtest-result {
  margin-bottom: 16px;
}

.result-card {
  overflow: hidden;
  margin-bottom: 16px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
}

.metric-item {
  text-align: center;
}

.metric-label {
  color: var(--van-gray-6);
  font-size: 14px;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 16px;
  font-weight: 500;
}

.records-list {
  padding: 8px;
}

.record-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border-bottom: 1px solid var(--van-cell-border-color);
}

.record-item:last-child {
  border-bottom: none;
}

.trade-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  margin-right: 12px;
  min-width: 48px;
  text-align: center;
}

.trade-type.buy {
  background-color: var(--van-danger-color);
  color: white;
}

.trade-type.sell {
  background-color: var(--van-success-color);
  color: white;
}

.trade-details {
  flex: 1;
}

.trade-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  font-size: 14px;
}

.trade-row:last-child {
  margin-bottom: 0;
}

.trade-row.secondary {
  color: var(--van-gray-6);
  font-size: 12px;
}

.trade-date {
  color: var(--van-gray-5);
}
</style> 