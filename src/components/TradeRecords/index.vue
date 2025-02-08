<template>
  <div class="trade-records">
    <van-cell-group inset title="交易记录" class="records-card">
      <div class="records-list">
        <div v-for="(trade, index) in trades" :key="trade.id" class="record-item">
          <!-- 交易类型标签 -->
          <div class="trade-type" :class="trade.type === 'buy' ? 'buy' : 'sell'">
            {{ trade.type === 'buy' ? '买入' : '卖出' }}
          </div>

          <!-- 交易详情 -->
          <div class="trade-details">
            <div class="trade-row">
              <span>价格: {{ formatNumber(trade.price) }}</span>
              <span>数量: {{ formatNumber(trade.volume) }}</span>
              <span>金额: {{ formatMoney(trade.amount) }}</span>
            </div>
            <div class="trade-row secondary">
              <span>总资产: {{ formatMoney(getAssetValue(index)) }}</span>
              <span>增长率: {{ formatPercent(getGrowthRate(index)) }}</span>
              <span class="trade-date">{{ formatDate(trade.date) }}</span>
            </div>
          </div>
        </div>
      </div>
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { computed } from '@vue/runtime-core'
import { useBacktestStore } from '@/stores/backtest'
import dayjs from 'dayjs'
import type { Trade } from '@/stores/backtest'

const store = useBacktestStore()

const trades = computed(() => store.backtestResult?.trades || [])

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
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
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
</script>

<style scoped>
.trade-records {
  margin-bottom: 16px;
}

.records-card {
  overflow: hidden;
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