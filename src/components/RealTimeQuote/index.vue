<template>
  <div class="real-time-quote">
    <van-cell-group inset title="实时行情" class="quote-card">
      <div class="quote-header">
        <div class="stock-info">
          <div class="stock-name">{{ stockName }}</div>
          <div class="stock-code">{{ stockCode }}</div>
        </div>
        <div class="quote-time">{{ formatTime(quoteData?.time) }}</div>
      </div>

      <div class="quote-main">
        <div class="price-info">
          <div class="current-price" :class="getPriceClass(quoteData?.price, quoteData?.pre_close)">
            {{ formatPrice(quoteData?.price) }}
          </div>
          <div class="price-change" :class="getPriceClass(quoteData?.price, quoteData?.pre_close)">
            <span>{{ formatChange(quoteData?.price, quoteData?.pre_close) }}</span>
            <span>{{ formatChangePercent(quoteData?.price, quoteData?.pre_close) }}</span>
          </div>
        </div>

        <div class="quote-grid">
          <div class="quote-item">
            <div class="label">今开</div>
            <div class="value" :class="getPriceClass(quoteData?.open, quoteData?.pre_close)">
              {{ formatPrice(quoteData?.open) }}
            </div>
          </div>
          <div class="quote-item">
            <div class="label">最高</div>
            <div class="value" :class="getPriceClass(quoteData?.high, quoteData?.pre_close)">
              {{ formatPrice(quoteData?.high) }}
            </div>
          </div>
          <div class="quote-item">
            <div class="label">最低</div>
            <div class="value" :class="getPriceClass(quoteData?.low, quoteData?.pre_close)">
              {{ formatPrice(quoteData?.low) }}
            </div>
          </div>
          <div class="quote-item">
            <div class="label">昨收</div>
            <div class="value">{{ formatPrice(quoteData?.pre_close) }}</div>
          </div>
          <div class="quote-item">
            <div class="label">成交量</div>
            <div class="value">{{ formatVolume(quoteData?.volume) }}</div>
          </div>
          <div class="quote-item">
            <div class="label">成交额</div>
            <div class="value">{{ formatAmount(quoteData?.amount) }}</div>
          </div>
        </div>
      </div>
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useMarketStore } from '@/stores/market'
import { tushareService } from '@/services/tushare'
import type { StockBasic } from '@/stores/market'
import dayjs from 'dayjs'

const marketStore = useMarketStore()
const quoteData = ref<any>(null)
const refreshInterval = ref<number | null>(null)

// 获取股票名称和代码
const stockName = computed(() => {
  const stock = marketStore.stockList.find((s: StockBasic) => s.ts_code === marketStore.selectedStock)
  return stock?.name || '--'
})

const stockCode = computed(() => marketStore.selectedStock || '--')

// 格式化工具函数
const formatPrice = (price: number) => {
  return price ? price.toFixed(2) : '--'
}

const formatTime = (time: string) => {
  return time ? dayjs(time).format('HH:mm:ss') : '--'
}

const formatVolume = (volume: number) => {
  if (!volume) return '--'
  return volume >= 10000 
    ? (volume / 10000).toFixed(2) + '万手'
    : volume.toFixed(0) + '手'
}

const formatAmount = (amount: number) => {
  if (!amount) return '--'
  return amount >= 100000000
    ? (amount / 100000000).toFixed(2) + '亿'
    : (amount / 10000).toFixed(2) + '万'
}

const formatChange = (price: number, preClose: number) => {
  if (!price || !preClose) return '--'
  const change = price - preClose
  return (change >= 0 ? '+' : '') + change.toFixed(2)
}

const formatChangePercent = (price: number, preClose: number) => {
  if (!price || !preClose) return '--'
  const percent = ((price - preClose) / preClose) * 100
  return (percent >= 0 ? '+' : '') + percent.toFixed(2) + '%'
}

const getPriceClass = (price: number, preClose: number) => {
  if (!price || !preClose) return ''
  return price > preClose ? 'price-up' : price < preClose ? 'price-down' : ''
}

// 获取实时行情数据
const fetchQuoteData = async () => {
  if (!marketStore.selectedStock) return
  try {
    const response = await tushareService.getRealTimeQuote({
      ts_code: marketStore.selectedStock
    })
    if (response.code === 0 && response.data.items.length > 0) {
      const fields = response.data.fields
      const item = response.data.items[0]
      const data: Record<string, any> = {}
      fields.forEach((field, index) => {
        data[field] = item[index]
      })
      quoteData.value = data
    }
  } catch (error) {
    console.error('获取实时行情失败:', error)
  }
}

// 启动定时刷新
const startRefresh = () => {
  fetchQuoteData()
  refreshInterval.value = window.setInterval(fetchQuoteData, 3000)
}

// 停止定时刷新
const stopRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

// 生命周期钩子
onMounted(() => {
  if (marketStore.selectedStock) {
    startRefresh()
  }
})

onUnmounted(() => {
  stopRefresh()
})

// 监听股票变化
watch(() => marketStore.selectedStock, (newStock: string | null) => {
  if (newStock) {
    startRefresh()
  } else {
    stopRefresh()
  }
})
</script>

<style scoped>
.real-time-quote {
  margin-bottom: 16px;
}

.quote-card {
  overflow: hidden;
}

.quote-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.stock-info {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stock-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.stock-code {
  font-size: 12px;
  color: var(--text-secondary);
}

.quote-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.quote-main {
  padding: 16px;
}

.price-info {
  margin-bottom: 16px;
  text-align: center;
}

.current-price {
  font-size: 32px;
  font-weight: 600;
  line-height: 1.2;
  color: var(--text-color);
}

.price-change {
  display: flex;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-color);
}

.quote-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.quote-item {
  text-align: center;
}

.quote-item .label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.quote-item .value {
  font-size: 14px;
  color: var(--text-color);
}

.price-up {
  color: var(--price-up-color, #f5222d) !important;
}

.price-down {
  color: var(--price-down-color, #52c41a) !important;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .quote-header {
    border-bottom-color: var(--border-color-dark);
  }

  .stock-name {
    color: var(--text-color-dark);
  }

  .stock-code,
  .quote-time {
    color: var(--text-secondary-dark);
  }

  .current-price {
    color: var(--text-color-dark);
  }

  .quote-item .label {
    color: var(--text-secondary-dark);
  }

  .quote-item .value {
    color: var(--text-color-dark);
  }
}
</style> 