<template>
  <div class="time-cost-config">
    <van-cell-group inset title="时间和成本" class="config-card">
      <!-- 开始日期 -->
      <van-cell
        title="开始日期"
        :value="store.formattedStartDate || '请选择开始日期'"
        is-link
        @click="showStartDatePicker = true"
      />
      
      <!-- 结束日期 -->
      <van-cell
        title="结束日期"
        :value="store.formattedEndDate || '请选择结束日期'"
        is-link
        @click="showEndDatePicker = true"
      />

      <!-- 交易成本 -->
      <van-field
        v-model="tradingCost"
        label="交易成本"
        type="number"
        placeholder="请输入交易成本"
        input-align="right"
        @input="onTradingCostChange"
      >
        <template #button>
          <span class="unit">%</span>
        </template>
      </van-field>
    </van-cell-group>

    <!-- 开始日期选择器 -->
    <van-calendar
      v-model:show="showStartDatePicker"
      :min-date="minDate"
      :max-date="maxStartDate"
      :default-date="store.backtestConfig.startDate || defaultStartDate"
      @confirm="onStartDateConfirm"
      title="选择开始日期"
      color="var(--primary-color)"
    />

    <!-- 结束日期选择器 -->
    <van-calendar
      v-model:show="showEndDatePicker"
      :min-date="minEndDate"
      :max-date="maxDate"
      :default-date="store.backtestConfig.endDate || defaultEndDate"
      @confirm="onEndDateConfirm"
      title="选择结束日期"
      color="var(--primary-color)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from '@vue/runtime-core'
import { useBacktestStore } from '@/stores/backtest'
import dayjs from 'dayjs'

const store = useBacktestStore()
const showStartDatePicker = ref(false)
const showEndDatePicker = ref(false)
const tradingCost = ref(store.backtestConfig.tradingCost.toString())

// 日期范围设置
const today = dayjs().toDate()
const minDate = dayjs('2010-01-01').toDate()
const maxDate = dayjs().subtract(1, 'day').toDate() // 昨天

// 默认开始日期：一年前
const defaultStartDate = dayjs().subtract(1, 'year').toDate()

// 默认结束日期：昨天
const defaultEndDate = maxDate

// 计算最大开始日期（不能超过结束日期）
const maxStartDate = computed(() => {
  return store.backtestConfig.endDate || maxDate
})

// 计算最小结束日期（不能早于开始日期）
const minEndDate = computed(() => {
  return store.backtestConfig.startDate || minDate
})

// 初始化默认值
if (!store.backtestConfig.startDate) {
  store.setStartDate(defaultStartDate)
}
if (!store.backtestConfig.endDate) {
  store.setEndDate(defaultEndDate)
}
if (store.backtestConfig.tradingCost === undefined) {
  store.setTradingCost(0)
}

// 处理开始日期选择
const onStartDateConfirm = (value: Date) => {
  store.setStartDate(value)
  showStartDatePicker.value = false
}

// 处理结束日期选择
const onEndDateConfirm = (value: Date) => {
  store.setEndDate(value)
  showEndDatePicker.value = false
}

// 处理交易成本变化
const onTradingCostChange = (value: string) => {
  const cost = parseFloat(value)
  if (!isNaN(cost)) {
    store.setTradingCost(cost)
  }
}
</script>

<style scoped>
.time-cost-config {
  margin-bottom: 16px;
}

.config-card {
  overflow: hidden;
}

.unit {
  color: #969799;
  font-size: 14px;
  padding: 0 8px;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .unit {
    color: #969799;
  }
}
</style> 