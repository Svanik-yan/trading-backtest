<template>
  <div class="strategy-analysis">
    <!-- 历史表现分析 -->
    <van-cell-group inset title="历史表现分析" class="analysis-card">
      <div class="metrics-grid">
        <van-cell title="年化收益率" :value="formatPercent(store.backtestResult?.annualizedReturn)" />
        <van-cell title="夏普比率" :value="formatNumber(store.backtestResult?.sharpeRatio)" />
        <van-cell title="最大回撤" :value="formatPercent(store.backtestResult?.maxDrawdown)" />
        <van-cell title="胜率" :value="formatPercent(store.backtestResult?.winRate)" />
        <van-cell title="盈亏比" :value="formatNumber(store.backtestResult?.profitFactor)" />
        <van-cell title="最大连续亏损" :value="store.backtestResult?.maxConsecutiveLosses + '次'" />
      </div>
    </van-cell-group>

    <!-- 策略参数优化建议 -->
    <van-cell-group inset title="策略参数优化建议" class="analysis-card">
      <div class="optimization-tips" v-if="store.backtestResult">
        <van-cell>
          <template #title>
            <div class="tip-title">参数建议</div>
            <div class="tip-content">{{ getParameterSuggestions() }}</div>
          </template>
        </van-cell>
        <van-cell>
          <template #title>
            <div class="tip-title">风险提示</div>
            <div class="tip-content">{{ getRiskWarnings() }}</div>
          </template>
        </van-cell>
      </div>
    </van-cell-group>

    <!-- 策略对比 -->
    <van-cell-group inset title="策略对比" class="analysis-card">
      <div class="strategy-comparison">
        <div class="comparison-header">
          <div class="metric-name">指标</div>
          <div class="current-strategy">当前策略</div>
          <div class="benchmark">基准</div>
        </div>
        <div class="comparison-row">
          <div class="metric-name">年化收益</div>
          <div class="current-strategy">{{ formatPercent(store.backtestResult?.annualizedReturn) }}</div>
          <div class="benchmark">{{ formatPercent(benchmarkReturn) }}</div>
        </div>
        <div class="comparison-row">
          <div class="metric-name">最大回撤</div>
          <div class="current-strategy">{{ formatPercent(store.backtestResult?.maxDrawdown) }}</div>
          <div class="benchmark">{{ formatPercent(benchmarkMaxDrawdown) }}</div>
        </div>
        <div class="comparison-row">
          <div class="metric-name">夏普比率</div>
          <div class="current-strategy">{{ formatNumber(store.backtestResult?.sharpeRatio) }}</div>
          <div class="benchmark">{{ formatNumber(benchmarkSharpe) }}</div>
        </div>
      </div>
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from '@vue/runtime-core'
import { useBacktestStore } from '@/stores/backtest'

const store = useBacktestStore()

// 基准数据（可以从市场数据中获取）
const benchmarkReturn = ref(0.08) // 8% 年化收益
const benchmarkMaxDrawdown = ref(0.15) // 15% 最大回撤
const benchmarkSharpe = ref(1.2) // 基准夏普比率

// 格式化函数
const formatMoney = (value: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatNumber = (value: number | undefined) => {
  if (value === undefined) return '-'
  return value.toFixed(2)
}

const formatPercent = (value: number | undefined) => {
  if (value === undefined) return '-'
  return (value * 100).toFixed(2) + '%'
}

// 获取参数优化建议
const getParameterSuggestions = () => {
  if (!store.backtestResult) return '暂无建议'
  
  const suggestions = []
  const { winRate, profitFactor, maxDrawdown } = store.backtestResult

  if (winRate < 0.5) {
    suggestions.push('建议增加策略的胜率，可以考虑调整入场条件或加入更多的过滤指标')
  }

  if (profitFactor < 1.5) {
    suggestions.push('盈亏比偏低，建议优化止盈止损策略，提高单笔盈利金额')
  }

  if (maxDrawdown > 0.2) {
    suggestions.push('最大回撤过大，建议加入风控措施，如设置最大持仓比例或动态调整仓位')
  }

  return suggestions.length > 0 ? suggestions.join('；') : '策略表现良好，可以保持当前参数'
}

// 获取风险提示
const getRiskWarnings = () => {
  if (!store.backtestResult) return '暂无风险提示'
  
  const warnings = []
  const { maxConsecutiveLosses, maxSingleLoss, maxDrawdown } = store.backtestResult

  if (maxConsecutiveLosses > 5) {
    warnings.push(`连续亏损次数较多(${maxConsecutiveLosses}次)，建议关注心理承受能力`)
  }

  if (maxSingleLoss && Math.abs(maxSingleLoss) > store.backtestConfig.initialCapital * 0.1) {
    warnings.push('单笔最大亏损超过初始资金10%，建议设置止损')
  }

  if (maxDrawdown > 0.3) {
    warnings.push('最大回撤超过30%，建议评估风险承受能力')
  }

  return warnings.length > 0 ? warnings.join('；') : '当前风险在可控范围内'
}
</script>

<style scoped>
.strategy-analysis {
  margin-bottom: 16px;
}

.analysis-card {
  margin-bottom: 16px;
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

.optimization-tips {
  padding: 8px 0;
}

.tip-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.tip-content {
  font-size: 13px;
  color: var(--van-gray-6);
  line-height: 1.5;
}

.strategy-comparison {
  padding: 16px;
}

.comparison-header,
.comparison-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid var(--van-cell-border-color);
}

.comparison-header {
  font-weight: 500;
  color: var(--van-gray-8);
}

.comparison-row:last-child {
  border-bottom: none;
}

.metric-name {
  color: var(--van-gray-7);
}

.current-strategy,
.benchmark {
  text-align: right;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .tip-content {
    color: var(--van-gray-5);
  }

  .comparison-header {
    color: var(--van-gray-5);
  }

  .metric-name {
    color: var(--van-gray-6);
  }
}
</style> 