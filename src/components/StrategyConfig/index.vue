<template>
  <div class="strategy-config">
    <van-cell-group inset title="策略设置" class="config-card">
      <van-cell
        title="股票代码"
        :value="displayStockInfo"
        is-link
        @click="showStockPicker = true"
        class="field-item"
      />
      
      <van-cell
        title="策略选择"
        :value="store.selectedStrategy?.name || '请选择策略'"
        is-link
        @click="showStrategyPicker = true"
        class="field-item"
      />

      <van-field
        v-model="initialCapital"
        label="初始资金"
        type="number"
        placeholder="请输入初始资金"
        input-align="right"
        @input="onInitialCapitalChange"
        class="field-item"
      >
        <template #button>
          <span class="unit">元</span>
        </template>
      </van-field>
    </van-cell-group>

    <!-- 股票选择弹窗 -->
    <van-popup 
      v-model:show="showStockPicker" 
      position="bottom" 
      round
      class="stock-popup"
    >
      <div class="popup-header">
        <div class="popup-title">选择股票</div>
      </div>
      <van-search
        v-model="searchValue"
        placeholder="输入股票代码或名称搜索"
        shape="round"
        :loading="loading"
        @search="onSearch"
        @input="onSearchInput"
      >
        <template #right-icon>
          <van-icon name="search" @click="onSearch" />
        </template>
      </van-search>

      <!-- 搜索提示 -->
      <div v-if="!searchValue && !loading" class="search-tip">
        请输入股票代码（如：300377）或名称进行搜索
      </div>

      <!-- 搜索结果列表 -->
      <div class="stock-list" v-if="!loading && searchValue">
        <div
          v-for="stock in filteredStocks"
          :key="stock.ticker"
          class="stock-item"
          :class="{ active: stock.ticker === store.selectedStock }"
          @click="onStockSelect(stock)"
        >
          <div class="stock-info">
            <div class="stock-name">{{ stock.name }}</div>
            <div class="stock-code">{{ stock.ticker }}</div>
          </div>
          <div class="stock-extra">
            <div class="stock-exchange">{{ getExchangeName(stock.exchange_code) }}</div>
          </div>
        </div>
        
        <!-- 空结果提示 -->
        <div v-if="filteredStocks.length === 0" class="empty-result">
          <van-empty description="没有找到匹配的股票" />
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <van-loading type="spinner" size="24px">搜索中...</van-loading>
      </div>
    </van-popup>

    <!-- 策略选择弹窗 -->
    <van-popup 
      v-model:show="showStrategyPicker" 
      position="bottom" 
      round
      class="strategy-popup"
    >
      <div class="popup-header">
        <div class="popup-title">选择策略</div>
      </div>
      <div class="strategy-list">
        <div
          v-for="strategy in strategyOptions"
          :key="strategy.value"
          class="strategy-item"
          :class="{ active: strategy.value === store.selectedStrategy?.id }"
          @click="onStrategySelect(strategy)"
        >
          <div class="strategy-info">
            <div class="strategy-name">{{ strategy.text }}</div>
            <div class="strategy-desc">{{ strategy.description }}</div>
          </div>
          <van-icon name="success" v-if="strategy.value === store.selectedStrategy?.id" class="check-icon" />
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from '@vue/runtime-core'
import { useBacktestStore } from '@/stores/backtest'
import type { StockInfo } from '@/types'

const store = useBacktestStore()
const showStrategyPicker = ref(false)
const showStockPicker = ref(false)
const searchValue = ref('')
const loading = ref(false)
const stockList = ref<StockInfo[]>([])
const initialCapital = ref(store.backtestConfig.initialCapital.toString())

// 显示股票信息
const displayStockInfo = computed(() => {
  if (!store.selectedStock) return '请选择股票'
  const stock = stockList.value.find((s: StockInfo) => s.ticker === store.selectedStock)
  return stock ? `${stock.name} (${stock.ticker})` : store.selectedStock
})

// 获取交易所名称
const getExchangeName = (code: string) => {
  const exchangeMap: { [key: string]: string } = {
    'XSHG': '上交所',
    'XSHE': '深交所'
  }
  return exchangeMap[code] || code
}

// 过滤股票列表
const filteredStocks = computed(() => {
  if (!searchValue.value) return []
  const query = searchValue.value.toLowerCase()
  return stockList.value.filter((stock: StockInfo) => 
    stock.ticker.includes(query) ||
    (stock.name && stock.name.toLowerCase().includes(query))
  ).slice(0, 50) // 限制显示前50条结果
})

// 策略选项
const strategyOptions = [
  { text: 'MACD策略', value: 'macd', description: '基于MACD指标的趋势跟踪策略' },
  { text: '均线策略', value: 'ma', description: '基于移动平均线的交叉策略' },
  { text: 'RSI策略', value: 'rsi', description: '基于RSI超买超卖的反转策略' },
  { text: '布林带策略', value: 'boll', description: '基于布林带的区间交易策略' },
]

// 输入时的处理
function onSearchInput() {
  if (!searchValue.value) {
    loading.value = false
  }
}

// 搜索股票
async function onSearch() {
  if (!searchValue.value) return
  loading.value = true
  try {
    const response = await fetch('/stock_list.txt')
    const data = await response.json()
    if (data.code === 200 && Array.isArray(data.data)) {
      stockList.value = data.data
    }
  } catch (e) {
    console.error('搜索股票失败:', e)
  } finally {
    loading.value = false
  }
}

// 选择股票
const onStockSelect = (stock: StockInfo) => {
  store.selectedStock = stock.ticker
  showStockPicker.value = false
}

// 选择策略
const onStrategySelect = (strategy: typeof strategyOptions[0]) => {
  store.selectedStrategy = {
    id: strategy.value,
    name: strategy.text,
    description: strategy.description
  }
  showStrategyPicker.value = false
}

// 处理初始资金变化
const onInitialCapitalChange = (value: string) => {
  const capital = parseFloat(value)
  if (!isNaN(capital)) {
    store.backtestConfig.initialCapital = capital
  }
}

// 初始化加载股票列表
onMounted(async () => {
  try {
    const response = await fetch('/stock_list.txt')
    const data = await response.json()
    if (data.code === 200 && Array.isArray(data.data)) {
      stockList.value = data.data
    }
  } catch (e) {
    console.error('加载股票列表失败:', e)
  }
})
</script>

<style scoped>
.strategy-config {
  margin-bottom: 16px;
}

.config-card {
  overflow: hidden;
}

.field-item {
  transition: background-color 0.2s;
}

.field-item:active {
  background-color: #f5f5f5;
}

.unit {
  color: #969799;
  font-size: 14px;
  padding: 0 8px;
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

.stock-list,
.strategy-list {
  padding: 8px 0;
  max-height: calc(80vh - 108px);
  overflow-y: auto;
}

.stock-item,
.strategy-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #fff;
  transition: background-color 0.2s;
  cursor: pointer;
}

.stock-item:active,
.strategy-item:active {
  background-color: #f5f5f5;
}

.stock-item.active,
.strategy-item.active {
  background-color: #f7f8fa;
}

.stock-info,
.strategy-info {
  flex: 1;
  margin-right: 12px;
}

.stock-name,
.strategy-name {
  font-size: 16px;
  font-weight: 500;
  color: #323233;
  margin-bottom: 4px;
}

.stock-code {
  font-size: 12px;
  color: #969799;
}

.stock-exchange {
  font-size: 12px;
  color: #969799;
  padding: 2px 6px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.strategy-desc {
  font-size: 12px;
  color: #969799;
  line-height: 1.5;
}

.check-icon {
  color: var(--primary-color);
  font-size: 20px;
}

.search-tip {
  padding: 16px;
  text-align: center;
  color: #969799;
  font-size: 14px;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 32px 0;
}

.empty-result {
  padding: 32px 0;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .field-item:active {
    background-color: #3a3a3a;
  }

  .popup-header {
    border-bottom-color: #3a3a3a;
  }

  .popup-title {
    color: #fff;
  }

  .stock-item,
  .strategy-item {
    background: var(--card-background);
  }

  .stock-item:active,
  .strategy-item:active {
    background-color: #3a3a3a;
  }

  .stock-item.active,
  .strategy-item.active {
    background-color: #3a3a3a;
  }

  .stock-name,
  .strategy-name {
    color: #fff;
  }

  .stock-code,
  .stock-exchange,
  .strategy-desc {
    color: #969799;
  }

  .stock-exchange {
    background-color: #3a3a3a;
  }
}
</style> 