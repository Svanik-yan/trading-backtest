<template>
  <div class="kline-chart">
    <van-cell-group inset class="chart-card">
      <van-cell 
        title="行情走势" 
        :value="isExpanded ? '收起' : '展开'"
        @click="toggleExpand"
        is-link
        :arrow-direction="isExpanded ? 'up' : 'down'"
      />
      <div v-show="isExpanded" class="chart-container">
        <div v-if="hasData" ref="chartRef" class="kline-chart-inner"></div>
        <div v-else class="no-data">
          <van-empty description="暂无行情数据" />
        </div>
      </div>
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from '@vue/runtime-core'
import { useBacktestStore } from '@/stores/backtest'
import type { Trade, StockData } from '@/stores/backtest'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const store = useBacktestStore()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null
const hasData = computed(() => store.stockData !== null && store.stockData.length > 0)
const isExpanded = ref(true)

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
  // 当展开时，确保图表正确渲染
  if (isExpanded.value) {
    nextTick(() => {
      if (chart) {
        chart.resize()
      } else {
        initChart()
      }
    })
  }
}

// 格式化金额
const formatMoney = (value: number) => {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY'
  }).format(value)
}

// 格式化数字
const formatNumber = (value: number) => {
  return value.toFixed(2)
}

// 格式化成交量
const formatVolume = (value: number) => {
  if (value >= 100000000) {
    return (value / 100000000).toFixed(2) + '亿'
  } else if (value >= 10000) {
    return (value / 10000).toFixed(2) + '万'
  }
  return value.toString()
}

// 监听窗口大小变化
const handleResize = () => {
  if (chart) {
    chart.resize()
  }
}

// 初始化图表
const initChart = async () => {
  if (!chartRef.value) {
    console.log('No chart ref element')
    return
  }
  
  // 等待 DOM 更新完成
  await nextTick()
  
  // 检查容器尺寸
  const container = chartRef.value
  console.log('Chart container dimensions:', {
    width: container.clientWidth,
    height: container.clientHeight,
    offsetWidth: container.offsetWidth,
    offsetHeight: container.offsetHeight
  })
  
  // 销毁旧的图表实例
  if (chart) {
    console.log('Disposing old chart instance')
    chart.dispose()
  }
  
  // 创建新的图表实例
  chart = echarts.init(chartRef.value)
  console.log('Created new chart instance')
  
  // 如果有数据，立即更新图表
  if (hasData.value) {
    console.log('Has data on init, updating chart')
    updateChart()
  } else {
    console.log('No data on init')
  }
}

// 监听展开/收起状态变化
watch(isExpanded, (newVal) => {
  if (newVal) {
    nextTick(() => {
      if (!chart) {
        initChart()
      } else {
        chart.resize()
      }
    })
  }
})

// 更新图表数据
const updateChart = () => {
  if (!chart || !store.stockData?.length) {
    console.log('No chart instance or no stock data:', {
      hasChart: !!chart,
      stockDataLength: store.stockData?.length
    })
    return
  }

  console.log('Updating chart with data:', {
    stockDataLength: store.stockData.length,
    hasBacktestResult: !!store.backtestResult,
    trades: store.backtestResult?.trades?.length
  })

  // 准备K线数据
  const klineData = store.stockData.map((item: StockData) => [
    dayjs(item.date).format('YYYY-MM-DD'),
    item.open,
    item.close,
    item.low,
    item.high
  ])

  console.log('Prepared kline data:', {
    dataPoints: klineData.length,
    firstPoint: klineData[0],
    lastPoint: klineData[klineData.length - 1]
  })

  // 计算MA5和MA20
  const ma5Data = []
  const ma20Data = []
  const dates = store.stockData.map((item: StockData) => dayjs(item.date).format('YYYY-MM-DD'))
  
  for (let i = 0; i < store.stockData.length; i++) {
    if (i >= 4) {
      const ma5 = store.stockData.slice(i - 4, i + 1).reduce((sum: number, item: StockData) => sum + item.close, 0) / 5
      ma5Data.push([dates[i], ma5])
    } else {
      ma5Data.push([dates[i], '-'])
    }

    if (i >= 19) {
      const ma20 = store.stockData.slice(i - 19, i + 1).reduce((sum: number, item: StockData) => sum + item.close, 0) / 20
      ma20Data.push([dates[i], ma20])
    } else {
      ma20Data.push([dates[i], '-'])
    }
  }

  // 准备成交量数据
  const volumeData = store.stockData.map((item: StockData) => [
    dayjs(item.date).format('YYYY-MM-DD'),
    item.volume,
    item.close > item.open ? 1 : -1
  ])

  // 准备交易标记数据
  const markPoints = store.backtestResult?.trades.map((trade: Trade) => ({
    name: trade.type === 'buy' ? '买入' : '卖出',
    coord: [dayjs(trade.date).format('YYYY-MM-DD'), trade.price],
    value: `${trade.type === 'buy' ? '买' : '卖'}@${trade.price.toFixed(2)}`,
    itemStyle: {
      color: trade.type === 'buy' ? '#ee0a24' : '#07c160'
    },
    symbol: trade.type === 'buy' ? 'arrow' : 'arrow',
    symbolSize: 8,
    symbolRotate: trade.type === 'buy' ? 0 : 180,
    label: {
      show: true,
      position: trade.type === 'buy' ? 'bottom' : 'top',
      distance: 5,
      fontSize: 10,
      formatter: '{c}'
    }
  })) ?? []

  try {
    chart.setOption({
      backgroundColor: '#fff',
      animation: false,
      legend: {
        data: ['K线', 'MA5', 'MA20', '成交量', '收益率'],
        top: 10,
        right: 10
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        borderWidth: 1,
        borderColor: '#ccc',
        padding: 10,
        textStyle: {
          color: '#000'
        },
        position: function (pos: number[], params: any, el: any, elRect: any, size: { viewSize: number[] }) {
          const obj: Record<string, number> = {}
          obj[['left', 'right'][+(pos[0] < size.viewSize[0] / 2)]] = 60
          obj[['top', 'bottom'][+(pos[1] < size.viewSize[1] / 2)]] = 20
          return obj
        }
      },
      axisPointer: {
        link: [{ xAxisIndex: 'all' }],
        label: {
          backgroundColor: '#777'
        }
      },
      grid: [
        {
          left: '10%',
          right: '8%',
          top: '60px',
          height: '60%'
        },
        {
          left: '10%',
          right: '8%',
          top: '75%',
          height: '15%'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: dates,
          boundaryGap: true,
          axisLine: { onZero: false },
          axisLabel: {
            formatter: (value: string) => dayjs(value).format('MM-DD'),
            interval: 'auto',
            rotate: 30
          },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax',
          axisPointer: {
            z: 100
          }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          boundaryGap: true,
          axisLine: { onZero: false },
          axisLabel: { show: false },
          splitLine: { show: false }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true
          },
          position: 'right',
          splitLine: {
            show: true,
            lineStyle: {
              type: 'dashed'
            }
          }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          position: 'right',
          axisLabel: { show: true },
          axisLine: { show: true },
          axisTick: { show: true },
          splitLine: { show: false }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          bottom: 10,
          start: 0,
          end: 100,
          height: 20
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: klineData,
          itemStyle: {
            color: '#ee0a24',
            color0: '#07c160',
            borderColor: '#ee0a24',
            borderColor0: '#07c160'
          },
          markPoint: {
            data: markPoints
          }
        },
        {
          name: 'MA5',
          type: 'line',
          data: ma5Data,
          smooth: true,
          lineStyle: {
            opacity: 0.5,
            color: '#1989fa'
          }
        },
        {
          name: 'MA20',
          type: 'line',
          data: ma20Data,
          smooth: true,
          lineStyle: {
            opacity: 0.5,
            color: '#07c160'
          }
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumeData,
          itemStyle: {
            color: (params: any) => {
              return params.data[2] > 0 ? '#ee0a24' : '#07c160'
            }
          }
        }
      ]
    }, true)

    console.log('Chart updated successfully')
  } catch (error) {
    console.error('Failed to update chart:', error)
  }
}

// 监听股票数据变化
watch(() => store.stockData, (newStock) => {
  console.log('Stock data changed:', {
    hasData: !!newStock,
    length: newStock?.length
  })
  if (newStock && newStock.length > 0) {
    nextTick(() => {
      if (!chart) {
        initChart()
      } else {
        updateChart()
      }
    })
  }
}, { deep: true })

// 监听回测结果变化
watch(() => store.backtestResult, (newResult) => {
  console.log('Backtest result changed:', {
    hasResult: !!newResult,
    trades: newResult?.trades?.length
  })
  if (newResult) {
    nextTick(() => {
      if (chart) {
        updateChart()
      }
    })
  }
}, { deep: true })

// 组件挂载时初始化
onMounted(() => {
  console.log('Component mounted')
  window.addEventListener('resize', handleResize)
  initChart()
})

// 组件卸载时清理
onUnmounted(() => {
  console.log('Component unmounting')
  window.removeEventListener('resize', handleResize)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.kline-chart {
  margin-bottom: 16px;
}

.chart-card {
  overflow: hidden;
}

.chart-container {
  position: relative;
  width: 100%;
}

.kline-chart-inner {
  width: 100%;
  height: 500px; /* 设置固定高度 */
  min-height: 400px;
}

.no-data {
  padding: 40px 0;
  text-align: center;
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .chart-card {
    background-color: #1c1c1e;
  }
  
  :deep(.van-cell) {
    background-color: #1c1c1e;
    color: #fff;
  }
  
  :deep(.van-cell__title) {
    color: #fff;
  }
  
  :deep(.van-cell__value) {
    color: #969799;
  }
}
</style> 